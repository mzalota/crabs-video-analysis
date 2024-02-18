from __future__ import annotations

import math
from typing import Dict, List

import numpy
import numpy as np
import pandas as pd
from scipy.stats import stats

from lib.data.PandasWrapper import PandasWrapper
from lib.drifts_interpolate.CompensateForZoomService import CompensateForZoomService
from lib.imageProcessing.Camera import Camera
from lib.infra.Configurations import Configurations
from lib.infra.DataframeWrapper import DataframeWrapper
from lib.infra.FolderStructure import FolderStructure
from lib.infra.GraphPlotter import GraphPlotter
from lib.model.Point import Point
from lib.seefloor.VerticalSpeed import VerticalSpeed


class DriftRawData(PandasWrapper):
    #__df = None
    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> DriftRawData
        self.__folderStruct = folderStruct
        filepath = folderStruct.getRawDriftsFilepath()
        self.__df = PandasWrapper.readDataFrameFromCSV(filepath)

        configs = Configurations(folderStruct)
        self.__generate_debug_graphs = configs.is_debug()


    def __save_graphs_comparison(self, df, frame_id_from: int = 0, fream_id_to: int = 123456):
        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]
        graph_plotter = GraphPlotter.createNew(df_to_plot, self.__folderStruct)
        graph_plotter.generate_graph("_averages_y", ["average_y_new", "driftY"])
        graph_plotter.generate_graph("_averages_x", ["average_x_new", "driftX"])


    def __undistorted_points_column(self, point: List[Point]) -> DataframeWrapper:
        camera = Camera.create()
        undistorted_point = [camera.undistort_point(k) for k in point]
        return undistorted_point

    @staticmethod
    def _remove_outliers_stderr(val: Dict) -> Point:
        non_null_values = list()
        for k,v in val.items():
            if k == "frameNumber":
                continue

            if math.isnan(v):
                continue
            non_null_values.append(v)

        has_outlier = DriftRawData._has_outlier_stderr(non_null_values)

        val["has_outlier"] = has_outlier

        #min_loc = ls.index(min(ls))
        #max_loc = ls.index(max(ls))

        return has_outlier
        # return val


    @staticmethod
    def _has_outlier_stderr(ls: List) -> bool:
        if len(ls)<3:
            return "OK"

        stdev = np.std(ls)
        min_loc = ls.index(min(ls))
        max_loc = ls.index(max(ls))
        std_err = stats.sem(ls, axis=None, ddof=0)
        # print("lst     ", std_err, stdev, len(ls), min_loc, max_loc,ls)

        lst_no_min = ls[:min_loc] + ls[min_loc + 1:]
        new_std = np.std(lst_no_min)
        std_err_min = stats.sem(lst_no_min, axis=None, ddof=0)
        # print("lst_no_min", std_err_min, new_std, (stdev/new_std), len(lst_no_min), max(lst_no_min) - min(lst_no_min), lst_no_min)
        if std_err > 8 and std_err_min <4:
            # removing this one value has reduced standard error by more than twice.
            return "MIN_OUTLIER"

        lst_no_max = ls[:max_loc] + ls[max_loc + 1:]
        new_std = np.std(lst_no_max)
        std_err_max = stats.sem(lst_no_max, axis=None, ddof=0)
        # print("lst_no_max", std_err_max, new_std, (stdev/new_std), len(lst_no_max), max(lst_no_max) - min(lst_no_max), lst_no_max)
        if std_err > 8 and std_err_max < 4:
            #removing this one value has reduced standard error by more than twice.
            return "MAX_OUTLIER"

        return "OK"

    def interpolate(self, verticalSpeed: VerticalSpeed, driftsDetectionStep: int) -> None:
        zoom_compensator = CompensateForZoomService(self.__folderStruct)

        raw_drifts_df = self._replaceInvalidValuesWithNaN(self.__df, driftsDetectionStep)
        raw_drifts_df = self.remove_values_in_failed_records(raw_drifts_df)
        if self.__generate_debug_graphs:
            zoom_compensator.save_graphs_drifts_raw(raw_drifts_df, 1000, 1500)
            zoom_compensator.save_graphs_variance_raw(raw_drifts_df)

        df_compensated = zoom_compensator.compensate_for_zoom(raw_drifts_df, verticalSpeed)

        if self.__generate_debug_graphs:
            df_compensated2 = zoom_compensator.compensate_for_zoom_subdata(raw_drifts_df,verticalSpeed)
            zoom_compensator.save_graphs_variance_dezoomed(df_compensated2)
            zoom_compensator.save_graphs_drifts_zoom_compensated(df_compensated2, 1000, 1500)
            self.__save_graphs_comparison(df_compensated2, 1000, 1500)

        df = raw_drifts_df.copy()
        df["driftY"] = df_compensated['average_y_new']
        df["driftX"] = df_compensated['average_x_new']


        #TODO: dividiing drift by driftsDetectionStep is not flexible.
        # What if detectDrift step is not 2, but 3 or if it is mixed?
        df["driftX"] = df["driftX"] / driftsDetectionStep
        df["driftY"] = df["driftY"] / driftsDetectionStep

        df = df[[self.__COLNAME_frameNumber, self.__COLNAME_driftX, self.__COLNAME_driftY]]
        df = df.interpolate(limit_direction='both')

        # df = self.__replace_with_NaN_if_very_diff_to_neighbors(df, "driftY", driftsDetectionStep)
        df = self.__interpolate_to_step_1_frame(df)

        #set drifts in the first row to zero.
        self.__set_values_in_first_row_to_zeros(df)

        self.__df = df

    def remove_values_in_failed_records(self, df):
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            column_name_y_drift_raw = "fm_" + num + "_drift_y"
            column_name_x_drift_raw = "fm_" + num + "_drift_x"
            df.loc[df['fm_' + num + '_result'] != "DETECTED", [column_name_y_drift_raw, column_name_x_drift_raw]] = numpy.nan

            df.loc[df[column_name_x_drift_raw] < -50, [column_name_x_drift_raw, column_name_y_drift_raw]] = numpy.nan
            df.loc[df[column_name_x_drift_raw] > 50, [column_name_x_drift_raw, column_name_y_drift_raw]] = numpy.nan

            df.loc[df[column_name_y_drift_raw] < -200, [column_name_x_drift_raw, column_name_y_drift_raw]] = numpy.nan
            df.loc[df[column_name_y_drift_raw] > 200, [column_name_x_drift_raw, column_name_y_drift_raw]] = numpy.nan

            without_outliers_y = DataframeWrapper(df)
            without_outliers_y.remove_outliers_quantile(column_name_y_drift_raw)
            df[column_name_y_drift_raw] = without_outliers_y.pandas_df()[column_name_y_drift_raw]

            without_outliers_x = DataframeWrapper(df)
            without_outliers_x.remove_outliers_quantile(column_name_x_drift_raw)
            df[column_name_x_drift_raw] = without_outliers_x.pandas_df()[column_name_x_drift_raw]

            df = df.interpolate(limit_direction='both')

        return df

    def pandas_df(self):
        return self.__df

    def __set_values_in_first_row_to_zeros(self, df):
        df.loc[0, self.__COLNAME_driftX] = 0
        df.loc[0, self.__COLNAME_driftY] = 0

    def _replaceInvalidValuesWithNaN(self, df, step_size):
        # type: (pd.DataFrame) -> pd.DataFrame
        df.loc[df['driftY'] == -999, ['driftY', 'driftX']] = numpy.nan
        df.loc[df['driftX'] == -888, ['driftX', 'driftY']] = numpy.nan

        # df.loc[df['driftX'] < -10*step_size, ['driftX', 'driftY']] = numpy.nan #-20
        # df.loc[df['driftX'] > 10*step_size, ['driftX', 'driftY']] = numpy.nan  #30
        #
        # df.loc[df['driftY'] < -10*step_size, ['driftX', 'driftY']] = numpy.nan #-20
        # df.loc[df['driftY'] > 100*step_size/2, ['driftX', 'driftY']] = numpy.nan  #130

        return df

    def __interpolate_to_step_1_frame(self, df):
        # type: (pd.DataFrame) -> pd.DataFrame
        minFrameID = self.__min_frame_id()
        maxFrameID = self.max_frame_id()
        df = df.set_index("frameNumber")
        arrayOfFrameIDs = numpy.arange(start=minFrameID, stop=maxFrameID, step=1)
        everyFrame = pd.DataFrame(arrayOfFrameIDs, columns=["frameNumber"]).set_index("frameNumber")
        df = df.combine_first(everyFrame).reset_index()
        return df

    def __min_frame_id(self) -> int:
        return self.__df[self.__COLNAME_frameNumber].min()

    def max_frame_id(self) -> int:
        return self.__df[self.__COLNAME_frameNumber].max()

    def __replace_with_NaN_if_very_diff_to_neighbors(self, data, colName, step_size):
        targetOfAnalysis = data[colName]
        prevPrev = targetOfAnalysis.shift(periods=2)
        nextNext = targetOfAnalysis.shift(periods=-2)
        prev = targetOfAnalysis.shift(periods=1)
        next = targetOfAnalysis.shift(periods=-1)

        newDF =  pd.concat([prevPrev, prev, targetOfAnalysis, next, nextNext], axis=1)
        median = newDF.median(axis=1)
        diff_to_median = abs(targetOfAnalysis - median)
        is_outlier = diff_to_median > (10)

        data["median"] = median
        data["diff_to_median"] = diff_to_median
        data["isOutlier"] = is_outlier
        #
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.max_rows', None)
        # pd.set_option('expand_frame_repr', False)
        # print(data.head(1300))

        # whipe out
        data.loc[is_outlier, ['driftX', 'driftY']] = numpy.nan

        return data
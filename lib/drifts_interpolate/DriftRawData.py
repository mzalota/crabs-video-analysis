from __future__ import annotations
import math
from typing import Dict, List

import numpy
import numpy as np
import pandas as pd
from scipy.stats import stats

from lib.data.PandasWrapper import PandasWrapper
from lib.data.RedDotsData import RedDotsData
from lib.drifts_detect.DriftManualData import DriftManualData
from lib.drifts_interpolate.ZoomCompensate import CompensateForZoom
from lib.imageProcessing.Camera import Camera
from lib.infra.Configurations import Configurations
from lib.infra.DataframeWrapper import DataframeWrapper
from lib.infra.FolderStructure import FolderStructure
from lib.infra.GraphPlotter import GraphPlotter
from lib.model.Point import Point

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

        print(" value of var is XXXXX __generate_debug_graphs", self.__generate_debug_graphs)

    def __save_graphs_drifts_zoom_compensated(self, df, frame_id_from: int = 0, fream_id_to: int = 123456):
        yColumns_new = list()
        xColumns_new = list()
        for feature_matcher_idx in range(0, 9):
            column_name_y_new = "fm_"+str(feature_matcher_idx)+"_drift_y_new"
            column_name_x_new = "fm_" + str(feature_matcher_idx) + "_drift_x_new"
            yColumns_new.append(column_name_y_new)
            xColumns_new.append(column_name_x_new)

        x_axis_column = ["frameNumber"]
        filepath_prefix = self.__folderStruct.getSubDirpath() + "graph_debug_"
        title_prefix = self.__folderStruct.getVideoFilename()

        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]

        graph_title = title_prefix + "_averages_y"
        graphPlotter = GraphPlotter(df_to_plot)
        graphPlotter.saveGraphToFile(x_axis_column, ["average_y_new", "driftY"], graph_title,
                                     filepath_prefix + "drift_compare_avg_y.png")

        graph_title = title_prefix + "_averages_x"
        graphPlotter = GraphPlotter(df_to_plot)
        graphPlotter.saveGraphToFile(x_axis_column, ["average_x_new", "driftX"], graph_title,
                                     filepath_prefix + "drift_compare_avg_x.png")

        graph_title = title_prefix + "__FrameMatcher_Drifts_X_new"
        graph_plotter = GraphPlotter(df_to_plot)
        graph_plotter.saveGraphToFile(x_axis_column, xColumns_new, graph_title, filepath_prefix + "drift_x_new.png")

        graph_title = title_prefix + "__FrameMatcher_Drifts_Y_new"
        graph_plotter = GraphPlotter(df_to_plot)
        graph_plotter.saveGraphToFile(x_axis_column, yColumns_new, graph_title, filepath_prefix + "drift_y_new.png")


    def __undistort_coeff_column(self, center_point: List[Point]) -> DataframeWrapper:
        camera = Camera.create()
        distortion_coeff = [camera.distortion_at_point(k) for k in center_point]
        return distortion_coeff

    def __undistorted_points_column(self, point: List[Point]) -> DataframeWrapper:
        camera = Camera.create()
        undistorted_point = [camera.undistort_point(k) for k in point]
        return undistorted_point

    def _center_points_list(self, raw_drifts_df, num) -> List[Point]:
        center_y = self.__fm_center_y(raw_drifts_df, num)
        center_x = self.__fm_center_x(raw_drifts_df, num)
        combined = pd.concat([center_x, center_y], axis='columns')
        new_list = DataframeWrapper(combined).as_records_list()
        center_point = [self._point_from_x_y_coord(k) for k in new_list]
        return center_point

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

    def _point_from_x_y_coord(self, val: Dict) -> Point:
        x_coord = val[0]
        y_coord = val[1]
        if math.isnan(x_coord):
            return None
        if math.isnan(y_coord):
            return None

        return Point(x_coord, y_coord)

    def _undistort_coeff_for_point(self, point: Point) ->float:
        camera = Camera.create()
        return camera.distortion_at_point(point)

    def _undistort_coeff_for_point(self, val: Dict):
        x_coord = val[0]
        y_coord = val[1]
        if math.isnan(x_coord):
            return 1
        if math.isnan(y_coord):
            return 1

        point = Point(x_coord, y_coord)
        camera = Camera.create()
        return camera.distortion_at_point(point)

    def __fm_center_y(self, df: pd.DataFrame, num: str) -> pd.DataFrame:
        y_coord_top = df[("fm_" + str(num) + "_top_y")]
        y_coord_bottom = df[("fm_" + str(num) + "_bottom_y")]
        y_coord_center = y_coord_top + (y_coord_bottom - y_coord_top) / 2
        return y_coord_center

    def __fm_center_x(self, df: pd.DataFrame, num: str) -> pd.DataFrame:
        x_coord_top = df[("fm_" + str(num) + "_top_x")]
        x_coord_bottom = df[("fm_" + str(num) + "_bottom_x")]
        x_coord_center = x_coord_top + (x_coord_bottom - x_coord_top) / 2
        return x_coord_center


    def __drift_y_dezoomed(self, df: pd.DataFrame, num: str, zoom_factor: pd.DataFrame)-> pd.DataFrame:
        undistored_drift_y = self._undistored_drift_y(df, num)
        drift_y_due_to_zoom = self._drift_compnent_due_to_zoom_y(df, num, zoom_factor)
        return undistored_drift_y + drift_y_due_to_zoom

    def _drift_compnent_due_to_zoom_y(self, df, num, zoom_factor):
        center_point_undistorted = self._center_points_undistorted_list(df, num)
        center_y_undistorted = pd.Series([k.y for k in center_point_undistorted])
        distance_from_center_along_y = center_y_undistorted - Camera.create().center_point().y
        drift_y_due_to_zoom = distance_from_center_along_y * zoom_factor
        return drift_y_due_to_zoom

    def _undistored_drift_y(self, df, num):
        column_name_y_raw = "fm_" + num + "_drift_y"
        center_point = self._center_points_list(df, num)
        undistort_coeff = pd.Series(self.__undistort_coeff_column(center_point))
        undistored_drift_y = df[column_name_y_raw] * undistort_coeff
        return undistored_drift_y

    def __drift_x_dezoomed(self, df: pd.DataFrame, num: str, zoom_factor: pd.DataFrame) -> pd.DataFrame:
        undistored_drift_x = self._undistored_drift_x(df, num)
        drift_x_due_to_zoom = self._drift_compnent_due_to_zoom_x(df, num, zoom_factor)
        return undistored_drift_x + drift_x_due_to_zoom

    def _drift_compnent_due_to_zoom_x(self, df, num, zoom_factor):
        center_point_undistorted = self._center_points_undistorted_list(df, num)
        center_x_undistorted = pd.Series([k.x for k in center_point_undistorted])
        distance_from_center_along_x = center_x_undistorted - Camera.create().center_point().x
        drift_x_due_to_zoom = distance_from_center_along_x * zoom_factor
        return drift_x_due_to_zoom

    def _undistored_drift_x(self, df, num):
        column_name_x_raw = "fm_" + num + "_drift_x"
        center_point = self._center_points_list(df, num)
        undistort_coeff = pd.Series(self.__undistort_coeff_column(center_point))
        undistored_drift_x = df[column_name_x_raw] * undistort_coeff
        return undistored_drift_x

    def _center_points_undistorted_list(self, df, num):
        point = self._center_points_list(df, num)
        camera = Camera.create()
        undistorted_points = [camera.undistort_point(k) for k in point]
        # frame_a = pd.DataFrame(undistorted_points, columns=['undistored_point'])
        # return DataframeWrapper(frame_a)
        #return undistorted_points
        return pd.Series(undistorted_points)

    def interpolate(self, manualDrifts: DriftManualData, redDotsData: RedDotsData, driftsDetectionStep: int) -> pd.DataFrame:
        raw_drifts_df = self._replaceInvalidValuesWithNaN(self.__df, driftsDetectionStep)

        zoom_factor = redDotsData.scalingFactorColumn(driftsDetectionStep)

        zoom_compensator = CompensateForZoom(self.__folderStruct)
        df_compensated = zoom_compensator.compensate_for_zoom(raw_drifts_df, zoom_factor)
        if self.__generate_debug_graphs:
            self.__save_graphs_drifts_zoom_compensated(df_compensated, 1000, 1500)

        df = raw_drifts_df.copy()
        df = pd.merge(df, df_compensated[['average_y_new', "average_x_new", "frameNumber"]], on='frameNumber', how='left', suffixes=('_draft', '_reddot'))
        df["driftY"] = df['average_y_new']
        df["driftX"] = df['average_x_new']

        #TODO: Check if frame image cannot be read from video due to some technical error. Reset the values and then interpolate

        #TODO: dividiing drift by driftsDetectionStep is not flexible.
        # What if detectDrift step is not 2, but 3 or if it is mixed?
        df["driftX"] = df["driftX"] / driftsDetectionStep
        df["driftY"] = df["driftY"] / driftsDetectionStep

        df = df[[self.__COLNAME_frameNumber, self.__COLNAME_driftX, self.__COLNAME_driftY]]
        df = df.interpolate(limit_direction='both')

        # df = self.__replace_with_NaN_if_very_diff_to_neighbors(df, "driftY", driftsDetectionStep)
        df = self.__interpolateToHaveEveryFrame(df)

        #TODO: extract this function of overwriting raw drifts with manual values elsewhere, so that it is more explicit
        df = manualDrifts.overwrite_values(df)

        #set drifts in the first row to zero.
        self.__set_values_in_first_row_to_zeros(df)
        return df

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

    def __interpolateToHaveEveryFrame(self, df):
        # type: (pd.DataFrame) -> pd.DataFrame
        minFrameID = self.min_frame_id()
        maxFrameID = self.max_frame_id()
        df = df.set_index("frameNumber")
        arrayOfFrameIDs = numpy.arange(start=minFrameID, stop=maxFrameID, step=1)
        everyFrame = pd.DataFrame(arrayOfFrameIDs, columns=["frameNumber"]).set_index("frameNumber")
        df = df.combine_first(everyFrame).reset_index()
        return df

    def min_frame_id(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].min()

    def max_frame_id(self):
        # type: () -> int
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
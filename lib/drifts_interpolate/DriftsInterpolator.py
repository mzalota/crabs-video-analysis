from __future__ import annotations

import math
from typing import Dict, List

import numpy
import numpy as np
import pandas as pd
from scipy.stats import stats

from lib.drifts_interpolate.CompensateForZoomService import CompensateForZoomService
from lib.drifts_interpolate.DriftRawData import DriftRawData
from lib.infra.DataframeWrapper import DataframeWrapper
from lib.infra.FolderStructure import FolderStructure
from lib.model.Point import Point


class DriftsInterpolator:
    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'


    def __init__(self, folderStruct: FolderStructure):
        self.__folderStruct = folderStruct

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

    def clean_up_raw_drifts(self, drd: DriftRawData, driftsDetectionStep, verticalSpeed):
        df = drd.raw_drifts_with_nans()

        zoom_compensator = CompensateForZoomService(self.__folderStruct, df, verticalSpeed)
        df_compensated = zoom_compensator.compensate_for_zoom(df, verticalSpeed)

        df_compensated = df_compensated[[self.__COLNAME_frameNumber, "average_x_new", "average_y_new"]]
        df_clean = df_compensated.rename(
            columns={'average_x_new': self.__COLNAME_driftX, 'average_y_new': self.__COLNAME_driftY,
                     self.__COLNAME_frameNumber: self.__COLNAME_frameNumber})
        df = self.__to_step_1(df_clean, driftsDetectionStep)
        return df

    def save_graphs(self, drd: DriftRawData, verticalSpeed, frame_id_from, fream_id_to):
        df = drd.raw_drifts_with_nans()

        df = self.__remove_absolute_outliers(df)
        df = self.__remove_quantile_outliers(df)
        raw_drifts_df = df

        zoom_compensator = CompensateForZoomService(self.__folderStruct, raw_drifts_df, verticalSpeed)

        zoom_compensator.save_graphs_variance_raw(raw_drifts_df)
        zoom_compensator.save_graphs_variance_dezoomed()

        zoom_compensator.save_graphs_drifts_raw(raw_drifts_df, frame_id_from, fream_id_to)
        zoom_compensator.save_graphs_drifts_zoom_compensated(frame_id_from, fream_id_to)

        zoom_compensator.save_graphs_comparison(frame_id_from, fream_id_to)

    def __to_step_1(self, df, driftsDetectionStep: int):
        # TODO: dividing drift by driftsDetectionStep is not flexible.
        # What if detectDrift step is not 2, but 3 or if it is mixed?
        df[self.__COLNAME_driftX] = df[self.__COLNAME_driftX] / driftsDetectionStep
        df[self.__COLNAME_driftY] = df[self.__COLNAME_driftY] / driftsDetectionStep

        # df = self.__replace_with_NaN_if_very_diff_to_neighbors(df, "driftY", driftsDetectionStep)

        df = self.__interpolate_to_step_1_frame(df)

        # set drifts in the first row to zero.
        self.__set_values_in_first_row_to_zeros(df)
        return df

    def __set_values_in_first_row_to_zeros(self, df):
        df.loc[0, self.__COLNAME_driftX] = 0
        df.loc[0, self.__COLNAME_driftY] = 0


    # TODO: extract this function to PandasWrapper or DataFrameWrapper
    def __interpolate_to_step_1_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        minFrameID = df[self.__COLNAME_frameNumber].min()
        maxFrameID = df[self.__COLNAME_frameNumber].max()
        df = df.set_index("frameNumber")
        arrayOfFrameIDs = numpy.arange(start=minFrameID, stop=maxFrameID, step=1)
        everyFrame = pd.DataFrame(arrayOfFrameIDs, columns=["frameNumber"]).set_index("frameNumber")
        df = df.combine_first(everyFrame).reset_index()
        return df

    def __remove_absolute_outliers(self, df):
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            column_name_y_drift_raw = "fm_" + num + "_drift_y"
            column_name_x_drift_raw = "fm_" + num + "_drift_x"

            df.loc[df[column_name_x_drift_raw] < -50, [column_name_x_drift_raw, column_name_y_drift_raw]] = numpy.nan
            df.loc[df[column_name_x_drift_raw] > 50, [column_name_x_drift_raw, column_name_y_drift_raw]] = numpy.nan

            df.loc[df[column_name_y_drift_raw] < -200, [column_name_x_drift_raw, column_name_y_drift_raw]] = numpy.nan
            df.loc[df[column_name_y_drift_raw] > 200, [column_name_x_drift_raw, column_name_y_drift_raw]] = numpy.nan

        df = DataframeWrapper(df).interpolate_nan_values_everywhere().pandas_df()
        return df

    def __remove_quantile_outliers(self, df):
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            column_name_y_drift_raw = "fm_" + num + "_drift_y"
            column_name_x_drift_raw = "fm_" + num + "_drift_x"

            without_outliers_y = DataframeWrapper(df)
            without_outliers_y.remove_outliers_quantile(column_name_y_drift_raw)
            df[column_name_y_drift_raw] = without_outliers_y.pandas_df()[column_name_y_drift_raw]

            without_outliers_x = DataframeWrapper(df)
            without_outliers_x.remove_outliers_quantile(column_name_x_drift_raw)
            df[column_name_x_drift_raw] = without_outliers_x.pandas_df()[column_name_x_drift_raw]

        df = DataframeWrapper(df).interpolate_nan_values_everywhere().pandas_df()
        return df

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

import math
from typing import Dict, List

import numpy
import numpy as np
import pandas as pd
from scipy.stats import stats

#import statistics as statistics
from lib.imageProcessing.Camera import Camera
from lib.infra.FolderStructure import FolderStructure
from lib.infra.GraphPlotter import GraphPlotter
from lib.drifts.DriftManualData import DriftManualData

from lib.data.PandasWrapper import PandasWrapper
from lib.data.RedDotsData import RedDotsData
from lib.drifts.DriftManualData import DriftManualData
from lib.infra.Configurations import Configurations
from lib.infra.DataframeWrapper import DataframeWrapper
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


    def __save_graphs_drifts_raw(self, df_param, frame_id_from: int = 0, fream_id_to: int = 123456):

        df = df_param.copy()

        xColumns_orig = list()
        yColumns_orig = list()
        for num in range(0, 9):
            column_drift_y = "fm_" + str(num) + "_drift_y"
            column_drift_x = "fm_" + str(num) + "_drift_x"
            yColumns_orig.append(column_drift_y)
            xColumns_orig.append(column_drift_x)

            column_result = 'fm_' + str(num) + '_result'
            df.loc[df[column_result] == "FAILED", [column_drift_y, column_drift_x, "driftX", "driftY"]] = numpy.nan


        dframe = DataframeWrapper(df)
        for col_name in yColumns_orig:
            dframe.remove_outliers_quantile(col_name)

        for col_name in xColumns_orig:
            dframe.remove_outliers_quantile(col_name)

        # dframe.remove_outliers_quantile("driftX", 0.90)
        # dframe.remove_outliers_quantile("driftY", 0.90)

        df = dframe.pandas_df()

        #after removing values in rows with result="FAILED", now fill them out with interpolated values
        df = df.interpolate(limit_direction='both')

        df['average_y_orig'] = df[yColumns_orig].mean(axis=1)
        df['average_x_orig'] = df[xColumns_orig].mean(axis=1)

        # --- now Plot graphs and save them to PNG files
        x_axis_column = ["frameNumber"]
        filepath_prefix = self.__folderStruct.getSubDirpath() + "graph_debug_"
        title_prefix = self.__folderStruct.getVideoFilename()

        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]

        graph_title = title_prefix + "_FrameMatcher_Drifts_X_raw"
        graph_plotter = GraphPlotter(df_to_plot)
        graph_plotter.saveGraphToFile(x_axis_column, xColumns_orig, graph_title, filepath_prefix + "drift_x_raw.png")

        graph_title = title_prefix + "_FrameMatcher_Drifts_Y_raw"
        graph_plotter = GraphPlotter(df_to_plot)
        graph_plotter.saveGraphToFile(x_axis_column, yColumns_orig, graph_title, filepath_prefix + "drift_y_raw.png")

        graph_title = title_prefix + "_median_drifts_x_y"
        graphPlotter = GraphPlotter(df_to_plot)
        graphPlotter.saveGraphToFile(x_axis_column, ["driftY", "driftX", "average_y_orig", "average_x_orig"], graph_title,
                                     filepath_prefix + "drifts_px_raw.png")

        return df

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


    #TODO: Refactor this function into a separate class out of DriftRawData
    def _compensate_for_zoom(self, result_df, zoom_factor: pd.DataFrame) -> pd.DataFrame:

        result_df = pd.merge(result_df, zoom_factor, on='frameNumber', how='left', suffixes=('_draft', '_reddot'))

        result_df = self.__remove_values_in_failed_records(result_df)

        factor = result_df["scaling_factor"]  # scaling_factor scaling_factor_not_smooth
        yColumns_raw = list()
        xColumns_raw = list()
        yColumns_new = list()
        xColumns_new = list()
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)

            yColumns_raw.append("fm_" + num + "_drift_y")
            xColumns_raw.append("fm_" + num + "_drift_x")

            drift_y_dezoomed = self.__drift_y_dezoomed(result_df, num, factor)
            column_name_y_new = ("fm_" + num + "_drift_y_new")
            yColumns_new.append(column_name_y_new)
            # result_df[column_name_y_new] = drift_y_dezoomed

            drift_x_dezoomed = self.__drift_x_dezoomed(result_df, num, factor)
            column_name_x_new = ("fm_" + num + "_drift_x_new")
            xColumns_new.append(column_name_x_new)
            # result_df[column_name_x_new] = drift_x_dezoomed

            result_df[column_name_y_new] = drift_y_dezoomed
            result_df[column_name_x_new] = drift_x_dezoomed

            #if featureMatcher failed, then set values of column_name_x_new and column_name_y_new to NaN (NULL)
            result_df.loc[result_df["fm_" + num + "_result"] == "FAILED", [column_name_x_new, column_name_y_new]] = numpy.nan

        #remove outliers using standard error measure
        new_column_name = "crazy_variance_y"
        newColumnName2 = "crazy_variance_x"
        wrapper = DataframeWrapper(result_df[yColumns_new])
        wrapper.append_dataframe(DataframeWrapper(result_df["frameNumber"]))

        # DataframeWrapper(result_df).df_print_head(100)

        records_list_y = wrapper.as_records_list()
        outliersY = [DriftRawData._remove_outliers_stderr(k) for k in records_list_y]
        wrapper.pandas_df()[new_column_name]= outliersY
        wrapper.df_print_head(600)

        result_df[new_column_name] = outliersY
        result_df.loc[result_df[new_column_name] != "OK", yColumns_new] = numpy.nan
        result_df.loc[result_df[new_column_name] != "OK", xColumns_new] = numpy.nan

        records_list_x = DataframeWrapper(result_df[xColumns_new]).as_records_list()
        outliersX = [DriftRawData._remove_outliers_stderr(k) for k in records_list_x]
        result_df[newColumnName2] = outliersX
        result_df.loc[result_df[newColumnName2] != "OK", yColumns_new] = numpy.nan
        result_df.loc[result_df[newColumnName2] != "OK", xColumns_new] = numpy.nan

        # DataframeWrapper(result_df).df_print_head(600)


        #try to relax the 0.8 quantile outlier removing.
        dframe = DataframeWrapper(result_df)
        for col_name in yColumns_new:
            dframe.remove_outliers_quantile(col_name)

        for col_name in xColumns_new:
            dframe.remove_outliers_quantile(col_name)

        result_df = dframe.pandas_df()
        #result_df = result_df.interpolate(limit_direction='both')

        # ---
        self.__save_graphs_variance(result_df[xColumns_raw], 'variance_x_raw')
        self.__save_graphs_variance(result_df[xColumns_new], 'variance_x_new')
        self.__save_graphs_variance(result_df[yColumns_raw], 'variance_y_raw')
        self.__save_graphs_variance(result_df[yColumns_new], 'variance_y_new')

        #---

        result_df['average_y_new'] = result_df[yColumns_new].mean(axis=1)
        result_df['average_x_new'] = result_df[xColumns_new].mean(axis=1)

        camera = Camera.create()
        distortion_coeff = camera.distortion_at_center()
        result_df["average_x_new"] = result_df["average_x_new"] / distortion_coeff
        result_df["average_y_new"] = result_df["average_y_new"] / distortion_coeff

        return result_df

    def __save_graphs_variance(self, columns, variance_column_name):

        all_x_vals = DataframeWrapper(columns).as_records_list()
        variance_list = [self._for_variance(k) for k in all_x_vals]
        # frame_b = pd.DataFrame(variance_list, columns=[variance_column_name])
        frame_b = DataframeWrapper.create_from_list(variance_list, variance_column_name).pandas_df()

        # print(variance_column_name+"_variance: ", frame_b.var())
        print(variance_column_name+"_variance2: ", np.var(variance_list))
        print(variance_column_name+"_variance_avg: ", sum(variance_list) / len(variance_list) )

        frame_b = frame_b.reset_index()


        filepath_prefix = self.__folderStruct.getSubDirpath() + "graph_debug_"
        graph_title = variance_column_name
        graph_axis_x_column = 'index'
        df_to_plot = frame_b.loc[(frame_b[graph_axis_x_column] > 100) & (frame_b[graph_axis_x_column] < 6000)]
        graphPlotter = GraphPlotter(df_to_plot)
        filename = filepath_prefix + variance_column_name + ".png"

        graphPlotter.saveGraphToFile(["index"], [variance_column_name], graph_title, filename)

    def _for_variance(self, dict_of_vals: Dict):
        values = list(dict_of_vals.values())
        return np.var(values)

    def __undistort_coeff_column(self, center_point: List[Point]) -> DataframeWrapper:
        camera = Camera.create()
        distortion_coeff = [camera.distortion_at_point(k) for k in center_point]
        return distortion_coeff
        # frame_a = pd.DataFrame(distortion_coeff, columns=['undistort_coeff'])
        # return DataframeWrapper(frame_a)

    def __undistorted_points_column(self, point: List[Point]) -> DataframeWrapper:
        camera = Camera.create()
        undistorted_point = [camera.undistort_point(k) for k in point]
        return undistorted_point
        # frame_a = pd.DataFrame(undistorted_point, columns=['undistored_point'])
        # return DataframeWrapper(frame_a)

    def _center_points_list(self, raw_drifts_df, num) -> List[Point]:
        center_y = self.__fm_center_y(raw_drifts_df, num)
        center_x = self.__fm_center_x(raw_drifts_df, num)
        combined = pd.concat([center_x, center_y], axis='columns')
        new_list = DataframeWrapper(combined).as_records_list()
        center_point = [self._point_from_x_y_coord(k) for k in new_list]
        return center_point

    def __remove_values_in_failed_records(self, df):
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            column_name_y_drift_raw = "fm_" + num + "_drift_y"
            column_name_x_drift_raw = "fm_" + num + "_drift_x"
            df.loc[df['fm_' + num + '_result'] != "DETECTED", [column_name_y_drift_raw, column_name_x_drift_raw]] = numpy.nan

            df.loc[df[column_name_x_drift_raw] < -200, [column_name_x_drift_raw, column_name_y_drift_raw]] = numpy.nan
            df.loc[df[column_name_x_drift_raw] > 200, [column_name_x_drift_raw, column_name_y_drift_raw]] = numpy.nan

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


    def _detection_was_successfull_columnName(self, num) -> str:
        column_name_result_raw = "fm_" + num + "_result"

    def aaa(self):
        if column_value == "DETECTED":
            return True
        else:
            return False


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
        if self.__generate_debug_graphs:
            self.__save_graphs_drifts_raw(raw_drifts_df, 1000, 1500)

        zoom_factor = redDotsData.scalingFactorColumn(driftsDetectionStep)

        df_compensated = self._compensate_for_zoom(raw_drifts_df, zoom_factor)
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

        # since drifts were created using undistorted image, we need to increase drifts for raw/distored images
        # camera = Camera.create()
        # distortion_coeff = camera.distortion_at_center()
        # print ("distortion_coeff is ",distortion_coeff)
        # df["driftX"] = df["driftX"] / distortion_coeff
        # df["driftY"] = df["driftY"] / distortion_coeff

        #TODO: extract this function of overwriting raw drifts with manual values elsewhere, so that it is more explicit
        df = manualDrifts.overwrite_values(df)

        #set drifts in the first row to zero.
        self.setValuesInFirstRowToZeros(df)
        return df

    def setValuesInFirstRowToZeros(self, df):
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
        minFrameID = self.minFrameID()
        maxFrameID = self.maxFrameID()
        df = df.set_index("frameNumber")
        arrayOfFrameIDs = numpy.arange(start=minFrameID, stop=maxFrameID, step=1)
        everyFrame = pd.DataFrame(arrayOfFrameIDs, columns=["frameNumber"]).set_index("frameNumber")
        df = df.combine_first(everyFrame).reset_index()
        return df

    def minFrameID(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].min()

    def maxFrameID(self):
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
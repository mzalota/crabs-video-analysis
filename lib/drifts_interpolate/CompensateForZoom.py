from __future__ import annotations

from typing import Dict

import numpy
import numpy as np
import pandas as pd

from lib.drifts_interpolate.DetectedRawDrift import DetectedRawDrift
from lib.infra.Configurations import Configurations
from lib.infra.DataframeWrapper import DataframeWrapper
from lib.infra.FolderStructure import FolderStructure
from lib.infra.GraphPlotter import GraphPlotter


class CompensateForZoom:

    def __init__(self, folderStruct: FolderStructure) -> CompensateForZoom:
        self.__folderStruct = folderStruct
        configs = Configurations(folderStruct)
        self.__generate_debug_graphs = configs.is_debug()


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

    def compensate_for_zoom(self, result_df) -> pd.DataFrame:
        result_df = self.__remove_values_in_failed_records(result_df)

        if self.__generate_debug_graphs:
            self.__save_graphs_drifts_raw(result_df, 1000, 1500)

        yColumns_raw = list()
        xColumns_raw = list()
        yColumns_new = list()
        xColumns_new = list()
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            yColumns_raw.append("fm_" + num + "_drift_y")
            xColumns_raw.append("fm_" + num + "_drift_x")
            yColumns_new.append("fm_" + num + "_drift_y_new")
            xColumns_new.append("fm_" + num + "_drift_x_new")

        full_df = DataframeWrapper(result_df)
        records_list_all = full_df.as_records_list()
        raw_drift_objs = [DetectedRawDrift.createFromDict(k) for k in records_list_all]

        average_y_new = [k.drift_vector().y for k in raw_drift_objs]
        average_x_new = [k.drift_vector().x for k in raw_drift_objs]

        backToDataFrame = [k.to_dict() for k in raw_drift_objs]
        nowBack = DataframeWrapper.create_from_record_list(backToDataFrame)
        full_df.append_dataframe(nowBack)
        result_df = full_df.pandas_df()

        result_df['average_x_new'] = average_x_new
        result_df['average_y_new'] = average_y_new

        # ---
        if self.__generate_debug_graphs:
            self.__save_graphs_variance(result_df[xColumns_raw], 'variance_x_raw')
            self.__save_graphs_variance(nowBack.pandas_df()[xColumns_new], 'variance_x_new')
            self.__save_graphs_variance(result_df[yColumns_raw], 'variance_y_raw')
            self.__save_graphs_variance(nowBack.pandas_df()[yColumns_new], 'variance_y_new')

        return result_df

    def __save_graphs_variance(self, columns, variance_column_name):

        all_x_vals = DataframeWrapper(columns).as_records_list()
        variance_list = [self._for_variance(k) for k in all_x_vals]

        frame_b = DataframeWrapper.create_from_list(variance_list, variance_column_name).pandas_df()

        # print(variance_column_name+"_variance: ", frame_b.var())
        print(variance_column_name+"_variance: ", np.nanvar(variance_list))
        print(variance_column_name+"_variance_mean: ", np.nanmean(variance_list))
        print(variance_column_name+"_variance_avg: ",  np.nansum(variance_list) / len(variance_list) )

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

    def __remove_values_in_failed_records(self, df):
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

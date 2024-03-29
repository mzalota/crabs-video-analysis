from __future__ import annotations

from typing import Dict

import numpy
import numpy as np

from lib.drifts_interpolate.DetectedRawDrift import DetectedRawDrift
from lib.drifts_interpolate.DriftRawData import DriftRawData
from lib.infra.DataframeWrapper import DataframeWrapper
from lib.infra.FolderStructure import FolderStructure
from lib.infra.GraphPlotter import GraphPlotter
from lib.seefloor.VerticalSpeed import VerticalSpeed


class CompensateForZoomService:

    def __init__(self, drd: DriftRawData, folderStruct: FolderStructure, input_df, verticalSpeed: VerticalSpeed) -> CompensateForZoomService:
        self.__folderStruct = folderStruct
        self.__nowBack_df = self.__process_data(input_df, verticalSpeed)
        self.__driftRawData = drd

    def __process_data(self, input_df, verticalSpeed: VerticalSpeed):
        full_dfw = DataframeWrapper(input_df)
        nowBack = self.__process_raw_drifts(full_dfw, verticalSpeed)

        full_dfw.append_dataframe(nowBack)
        return full_dfw.pandas_df()

    def result_df(self):
        return self.__nowBack_df

    def save_graphs_drifts_raw(self, df_param, frame_id_from: int = 0, fream_id_to: int = 123456):
        df = df_param.copy()

        yColumns_raw = self.__driftRawData.columns_y_raw()
        dframe = DataframeWrapper(df)
        for col_name in yColumns_raw:
            dframe.remove_outliers_quantile(col_name)

        xColumns_raw = self.__driftRawData.columns_x_raw()
        for col_name in xColumns_raw:
            dframe.remove_outliers_quantile(col_name)

        df = dframe.pandas_df()

        #after removing values in rows with result="FAILED", now fill them out with interpolated values
        df = DataframeWrapper(df).interpolate_nan_values_everywhere().pandas_df()

        df['driftY_avg'] = df[yColumns_raw].mean(axis=1)
        df['driftX_avg'] = df[xColumns_raw].mean(axis=1)

        # --- now Plot graphs and save them to PNG files
        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]

        graph_plotter = GraphPlotter.createNew(df_to_plot, self.__folderStruct)

        graph_title = "FrameMatcher_Drifts_X_raw"
        graph_plotter.generate_graph(graph_title, xColumns_raw)

        graph_title = "FrameMatcher_Drifts_Y_raw"
        graph_plotter.generate_graph(graph_title, yColumns_raw)

        graph_title = "raw_drifts_avg_vs_median"
        yColumns = ["driftY", "driftX", "driftY_avg", "driftX_avg"]
        graph_plotter.generate_graph(graph_title, yColumns)

        return df

    def save_graphs_drifts_dezoomed(self, frame_id_from: int = 0, fream_id_to: int = 123456):
        df = self.__nowBack_df

        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]
        graph_plotter = GraphPlotter.createNew(df_to_plot, self.__folderStruct)

        xColumns_new = self.__columns_x_dezoomed()
        graph_plotter.generate_graph("FrameMatcher_Drifts_X_zoom", xColumns_new)

        yColumns_new = self.__columns_y_dezoomed()
        graph_plotter.generate_graph("FrameMatcher_Drifts_Y_zoom", yColumns_new)

    def __process_raw_drifts(self, inputDFW, verticalSpeed):
        raw_drift_objs = DetectedRawDrift.createListFromDataFrame(inputDFW, verticalSpeed)
        backToDataFrame = [k.to_dict() for k in raw_drift_objs]
        nowBack = DataframeWrapper.create_from_record_list(backToDataFrame)
        return nowBack

    def save_graphs_variance_raw(self, result_df):
        # TODO: Refactor to accept frame_from and frame_to parameters
        xColumns_raw = self.__driftRawData.columns_x_raw()
        self.__save_graphs_variance(result_df[xColumns_raw], 'variance_x_raw')

        yColumns_raw = self.__driftRawData.columns_y_raw()
        self.__save_graphs_variance(result_df[yColumns_raw], 'variance_y_raw')


    def save_graphs_comparison(self, frame_id_from: int = 0, fream_id_to: int = 123456):
        df = self.__nowBack_df

        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]

        graph_plotter = GraphPlotter.createNew(df_to_plot, self.__folderStruct)
        graph_plotter.generate_graph("drifts_raw_vs_dezoomed_y", ["drift_y_dezoomed", "driftY"])
        graph_plotter.generate_graph("drifts_raw_vs_dezoomed_x", ["drift_x_dezoomed", "driftX"])


    def save_graphs_variance_dezoomed(self):
        result_df = self.__nowBack_df
        # TODO: Refactor to accept frame_from and frame_to parameters
        xColumns_new = self.__columns_x_dezoomed()
        self.__save_graphs_variance(result_df[xColumns_new], 'variance_x_new')

        yColumns_new = self.__columns_y_dezoomed()
        self.__save_graphs_variance(result_df[yColumns_new], 'variance_y_new')


    def __columns_x_dezoomed(self):
        # TODO: Move this function to DetectedRawDrift class.
        xColumns_new = list()
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            xColumns_new.append("fm_" + num + "_drift_x_new")
        return xColumns_new

    def __columns_y_dezoomed(self):
        # TODO: Move this function to DetectedRawDrift class.
        yColumns_new = list()
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            yColumns_new.append("fm_" + num + "_drift_y_new")
        return yColumns_new

    def __save_graphs_variance(self, df, variance_column_name):

        all_x_vals = DataframeWrapper(df).as_records_list()
        variance_list = [self._for_variance(k) for k in all_x_vals]

        frame_b = DataframeWrapper.create_from_list(variance_list, variance_column_name).pandas_df()

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


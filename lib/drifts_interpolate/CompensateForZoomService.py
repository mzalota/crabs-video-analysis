from __future__ import annotations

from typing import Dict

import numpy
import numpy as np

from lib.drifts_interpolate.DetectedRawDrift import DetectedRawDrift
from lib.infra.Configurations import Configurations
from lib.infra.DataframeWrapper import DataframeWrapper
from lib.infra.FolderStructure import FolderStructure
from lib.infra.GraphPlotter import GraphPlotter
from lib.seefloor.VerticalSpeed import VerticalSpeed


class CompensateForZoomService:

    def __init__(self, folderStruct: FolderStructure) -> CompensateForZoomService:
        self.__folderStruct = folderStruct
        configs = Configurations(folderStruct)
        self.__generate_debug_graphs = configs.is_debug()


    def save_graphs_drifts_raw(self, df_param, frame_id_from: int = 0, fream_id_to: int = 123456):
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
        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]

        graph_plotter = GraphPlotter.createNew(df_to_plot, self.__folderStruct)

        graph_title = "FrameMatcher_Drifts_X_raw"
        graph_plotter.generate_graph(graph_title, xColumns_orig)

        graph_title = "FrameMatcher_Drifts_Y_raw"
        graph_plotter.generate_graph(graph_title, yColumns_orig)

        graph_title = "_median_drifts_x_y"
        yColumns = ["driftY", "driftX", "average_y_orig", "average_x_orig"]
        graph_plotter.generate_graph(graph_title, yColumns)

        return df

    def save_graphs_drifts_zoom_compensated(self, df, frame_id_from: int = 0, fream_id_to: int = 123456):

        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]
        graph_plotter = GraphPlotter.createNew(df_to_plot, self.__folderStruct)

        xColumns_new = self.__columns_x_dezoomed()
        graph_plotter.generate_graph("FrameMatcher_Drifts_X_zoom", xColumns_new)

        yColumns_new = self.__columns_y_dezoomed()
        graph_plotter.generate_graph("FrameMatcher_Drifts_Y_zoom", yColumns_new)

    def __columns_y_dezoomed(self):
        yColumns_new = list()
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            yColumns_new.append("fm_" + num + "_drift_y_new")
        return yColumns_new

    def compensate_for_zoom(self, input_df, verticalSpeed: VerticalSpeed):
        full_df = DataframeWrapper(input_df)

        records_list_all = full_df.as_records_list()
        raw_drift_objs = [DetectedRawDrift.createFromDict(k, verticalSpeed) for k in records_list_all]

        average_y_new = [k.drift_vector().y for k in raw_drift_objs]
        average_x_new = [k.drift_vector().x for k in raw_drift_objs]
        #backToDataFrame = [k.to_dict() for k in raw_drift_objs]
        #nowBack = DataframeWrapper.create_from_record_list(backToDataFrame)
        #full_df.append_dataframe(nowBack)

        result_df = full_df.pandas_df()
        result_df['average_x_new'] = average_x_new
        result_df['average_y_new'] = average_y_new
        return result_df
    def compensate_for_zoom_subdata(self, input_df, verticalSpeed: VerticalSpeed):
        full_df = DataframeWrapper(input_df)

        records_list_all = full_df.as_records_list()
        raw_drift_objs = [DetectedRawDrift.createFromDict(k, verticalSpeed) for k in records_list_all]

        average_y_new = [k.drift_vector().y for k in raw_drift_objs]
        average_x_new = [k.drift_vector().x for k in raw_drift_objs]
        backToDataFrame = [k.to_dict() for k in raw_drift_objs]

        nowBack = DataframeWrapper.create_from_record_list(backToDataFrame)
        full_df.append_dataframe(nowBack)

        result_df = full_df.pandas_df()
        result_df['average_x_new'] = average_x_new
        result_df['average_y_new'] = average_y_new

        return result_df

    #TODO: Refactort to accept frame_from and frame_to parameters
    def save_graphs_variance_raw(self, result_df):
        yColumns_raw = list()
        xColumns_raw = list()
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            yColumns_raw.append("fm_" + num + "_drift_y")
            xColumns_raw.append("fm_" + num + "_drift_x")
        self.__save_graphs_variance(result_df[xColumns_raw], 'variance_x_raw')
        self.__save_graphs_variance(result_df[yColumns_raw], 'variance_y_raw')

    # TODO: Refactort to accept frame_from and frame_to parameters
    def save_graphs_variance_dezoomed(self, result_df):
        xColumns_new = self.__columns_x_dezoomed()
        self.__save_graphs_variance(result_df[xColumns_new], 'variance_x_new')
        yColumns_new = self.__columns_y_dezoomed()
        self.__save_graphs_variance(result_df[yColumns_new], 'variance_y_new')


    def __columns_x_dezoomed(self):
        xColumns_new = list()
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            xColumns_new.append("fm_" + num + "_drift_x_new")
        return xColumns_new

    def __save_graphs_variance(self, df, variance_column_name):

        all_x_vals = DataframeWrapper(df).as_records_list()
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

        # graphPlotter = GraphPlotter.createNew(df_to_plot, self.__folderStruct)
        # graphPlotter.generate_graph("variance_"+variance_column_name, [variance_column_name])

    def _for_variance(self, dict_of_vals: Dict):
        values = list(dict_of_vals.values())
        return np.var(values)



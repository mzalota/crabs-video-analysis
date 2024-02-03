from __future__ import annotations
import pandas as pd

from lib.data.FourierSmoothing import FourierSmoothing
from lib.infra.Configurations import Configurations
from lib.infra.FolderStructure import FolderStructure
from lib.infra.GraphPlotter import GraphPlotter


class VerticalSpeed:
    def __init__(self, folderStruct: FolderStructure) -> VerticalSpeed:
        self.__folderStruct = folderStruct
    def vertical_speed_ratio(self, df: pd.DataFrame, driftsDetectionStep) -> pd.DataFrame:

        df['distance_smooth'] = self.__smooth_distance_value(df, "distance")

        result = self.__calculate_scaling_factor(df["distance_smooth"], driftsDetectionStep)
        df["scaling_factor"] = result

        if Configurations(self.__folderStruct).is_debug():
            result = self.__calculate_scaling_factor(df["distance"], driftsDetectionStep)
            df["scaling_factor_not_smooth"] = result
            y = ["scaling_factor", "scaling_factor_not_smooth"]
            df_to_plot = df.loc[(df['frameNumber'] > 1000) & (df['frameNumber'] < 1500)]
            GraphPlotter.createNew(df_to_plot, self.__folderStruct).generate_graph("debug_scale_factor", y)

        return df[["frameNumber", "scaling_factor"]]

    def __calculate_scaling_factor(self, column: pd.Series, driftsDetectionStep: int) ->pd.DataFrame:
        dist_diff = column - column.shift(periods=-1)
        scaling_factor_single_step = dist_diff / column
        result = scaling_factor_single_step + 0
        for increment in range(1, driftsDetectionStep):
            prev = scaling_factor_single_step.shift(periods=-increment)
            result = result + prev

        result = result.shift(periods=driftsDetectionStep)
        result = result + 1
        return result

    def __smooth_distance_value(self, newDF, distance_column_name):
        distance_column = newDF[distance_column_name]
        shifted_0_4 = FourierSmoothing().smooth_curve(distance_column, "distance_0_4", 0.4)
        shifted_1_0 = FourierSmoothing().smooth_curve(distance_column, "distance_1_0", 1)
        shifted_1_6 = FourierSmoothing().smooth_curve(distance_column, "distance_1_6", 1.6)

        newDF['distance_shift1_0'] = shifted_1_0
        newDF['distance_shift1_6'] = shifted_1_6
        newDF['distance_shift0_4'] = shifted_0_4

        if Configurations(self.__folderStruct).is_debug():
            columns_y = [distance_column_name, "distance_shift0_4", "distance_shift1_0", "distance_shift1_6", ]
            self.__save_graphs_smooth_distance(newDF, distance_column_name, columns_y, 1000, 1500)

        # return shifted_0_4
        return shifted_1_6

    def __save_graphs_smooth_distance(self, df, distance_column_name, columns_y, frame_id_from: int = 0, fream_id_to: int = 123456):
        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]

        filepath_prefix = self.__folderStruct.getSubDirpath() + "graph_debug_"+distance_column_name+"_"
        title_prefix = self.__folderStruct.getVideoFilename()

        graph_title = title_prefix + "_Distance_Fourier_"+distance_column_name
        GraphPlotter(df_to_plot).saveGraphToFile(["frameNumber"], columns_y, graph_title, filepath_prefix+"fourier.png")

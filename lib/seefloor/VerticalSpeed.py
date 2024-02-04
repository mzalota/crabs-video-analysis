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

        low_band_pass_cutoff = 0.4 # cuttoff gitter noise (high fequencies) - making curve "smooth"
        df['distance_smooth'] = FourierSmoothing().smooth_curve(df["distance"], low_band_pass_cutoff)

        result = self.calculate_scaling_factor_from_distance_between_reddots(df["distance_smooth"], driftsDetectionStep)
        df["scaling_factor"] = result

        if Configurations(self.__folderStruct).is_debug():
            result = self.calculate_scaling_factor_from_distance_between_reddots(df["distance"], driftsDetectionStep)
            df["scaling_factor_not_smooth"] = result
            y = ["scaling_factor", "scaling_factor_not_smooth"]
            df_to_plot = df.loc[(df['frameNumber'] > 1000) & (df['frameNumber'] < 1500)]
            GraphPlotter.createNew(df_to_plot, self.__folderStruct).generate_graph("debug_scale_factor", y)

        scaling_factor_df = df[["frameNumber", "scaling_factor"]]
        return scaling_factor_df

    def calculate_scaling_factor_from_distance_between_reddots(self, column: pd.Series, driftsDetectionStep: int) ->pd.DataFrame:
        dist_diff = column - column.shift(periods=-1)
        scaling_factor_single_step = dist_diff / column
        result = scaling_factor_single_step + 0
        for increment in range(1, driftsDetectionStep):
            prev = scaling_factor_single_step.shift(periods=-increment)
            result = result + prev

        result = result.shift(periods=driftsDetectionStep)
        result = result + 1
        return result

    def save_graph_smooth_distances(self, df, distance_column_name, frame_id_from, fream_id_to):
        cutoff_freq = [0.2, 0.4, 1.0, 1.6]
        distance_column = df[distance_column_name]
        columns_y = list()

        for cutoff_freq in cutoff_freq:
            smoothed = FourierSmoothing().smooth_curve(distance_column, cutoff_freq)
            colName = "distance_" + str(cutoff_freq)
            columns_y.append(colName)
            df[colName] = smoothed

        columns_y.append(distance_column_name)
        self.__save_graphs_smooth_distance(df, distance_column_name, columns_y, frame_id_from, fream_id_to
                                               )


    def __save_graphs_smooth_distance(self, df, distance_column_name, columns_y, frame_id_from: int = 0, fream_id_to: int = 123456):
        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]

        filepath_prefix = self.__folderStruct.getSubDirpath() + "graph_debug_"+distance_column_name+"_"
        title_prefix = self.__folderStruct.getVideoFilename()

        graph_title = title_prefix + "_Distance_Fourier_"+distance_column_name
        GraphPlotter(df_to_plot).saveGraphToFile(["frameNumber"], columns_y, graph_title, filepath_prefix+"fourier.png")

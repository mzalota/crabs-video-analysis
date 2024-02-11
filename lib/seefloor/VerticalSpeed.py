from __future__ import annotations

import pandas as pd

from lib.data.FourierSmoothing import FourierSmoothing
from lib.imageProcessing.Camera import Camera
from lib.infra.GraphPlotter import GraphPlotter
from lib.model.Vector import Vector


class VerticalSpeed:

    #scaling factor greater than 1 means that seefloor got further away. Everything got smaller. Everything on the image got closer to the center of the image (fewer pixels away from center).
    @staticmethod
    def zoom_correction(point, scaling_factor):
        camera = Camera.create()
        frame_center_point = camera.center_point()

        x_offset_from_middle_old = point.x - frame_center_point.x
        x_offset_from_middle_new = x_offset_from_middle_old / scaling_factor
        x_correction = x_offset_from_middle_new - x_offset_from_middle_old

        y_offset_from_middle_old = point.y - frame_center_point.y
        y_offset_from_middle_new = y_offset_from_middle_old / scaling_factor
        y_correction = y_offset_from_middle_new - y_offset_from_middle_old

        return Vector(x_correction, y_correction)

    def zoom_compensation(self, frame_id_from, frame_id_to) -> float:
        result = 1
        for i in range(frame_id_from, frame_id_to+1, 1):
            scaling_factor = self.__scaling_factor_dict[i]
            result = result * scaling_factor
        return result


    def vertical_speed_ratio(self, df: pd.DataFrame) -> pd.DataFrame:
        df["scaling_factor"] = self.calculate_scaling_factor_from_distance_between_reddots(df["distance_smooth"])

        scaling_factor_df = df[["frameNumber", "scaling_factor"]]

        df_indexed = scaling_factor_df.set_index('frameNumber')
        self.__scaling_factor_dict = df_indexed['scaling_factor'].to_dict()

        return scaling_factor_df

    def calculate_scaling_factor_from_distance_between_reddots(self, column: pd.Series) ->pd.DataFrame:
        distance_prev = column.shift(periods=-1)
        return column/distance_prev


    def save_graph_smooth_distances(self, df, distance_column_name, folderStruct, frame_id_from, fream_id_to):
        cutoff_freq = [0.2, 0.4, 1.0, 1.6]
        distance_column = df[distance_column_name]
        columns_y = list()

        for cutoff_freq in cutoff_freq:
            fourier_smoothing = FourierSmoothing()
            colName = "distance_" + str(cutoff_freq)
            columns_y.append(colName)

            smoothed = fourier_smoothing.smooth_array(distance_column.to_numpy(), cutoff_freq)
            fourier_smoothing.saveGraphFFT(smoothed, colName, folderStruct)
            df[colName] = smoothed

        columns_y.append(distance_column_name)
        self.__save_graphs_smooth_distance(df, distance_column_name, columns_y, folderStruct, frame_id_from, fream_id_to)


    def __save_graphs_smooth_distance(self, df, distance_column_name, columns_y, folder_struct, frame_id_from: int = 0, fream_id_to: int = 123456):
        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]
        filepath_prefix = folder_struct.getSubDirpath() + "graph_debug_" + distance_column_name + "_"
        title_prefix = folder_struct.getVideoFilename()

        graph_title = title_prefix + "_Distance_Fourier_"+distance_column_name
        GraphPlotter(df_to_plot).saveGraphToFile(["frameNumber"], columns_y, graph_title, filepath_prefix+"fourier.png")

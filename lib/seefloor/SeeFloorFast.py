from pandas import DataFrame


class SeeFloorFast:

    def __init__(self, seefloorDF: DataFrame):
        if seefloorDF is None:
            return

        df_indexed = seefloorDF.set_index('frameNumber')

        self.__mm_per_pixel_dict = df_indexed["mm_per_pixel"].to_dict()
        self.__drift_y_dict = df_indexed ['driftY'].to_dict()
        self.__drift_x_dict = df_indexed['driftX'].to_dict()

    def min_frame_id(self) -> int:
        return min(self.__drift_y_dict.keys())

    def max_frame_id(self) -> int:
        return max(self.__drift_y_dict.keys())

    def _mm_per_pixel(self, frame_id):
        return self.__mm_per_pixel_dict[frame_id]

    def _drift_x(self, frame_id: int) -> float:
        return self.__drift_x_dict[frame_id]

    def _drift_y(self, frame_id: int) -> float:
        return self.__drift_y_dict[frame_id]


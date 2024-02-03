from pandas import DataFrame

from lib.model.Vector import Vector


class SeeFloorFast:

    def __init__(self, seefloorDF: DataFrame):
        if seefloorDF is None:
            return

        df_indexed = seefloorDF.set_index('frameNumber')

        #TODO: use smoothed distance between red dots for mm_per_pixel, so that zoom_factor is smooth to0.
        self.__mm_per_pixel_dict = df_indexed["mm_per_pixel"].to_dict()
        self.__drift_y_dict = df_indexed ['driftY'].to_dict()
        self.__drift_x_dict = df_indexed['driftX'].to_dict()

    def min_frame_id(self) -> int:
        return min(self.__drift_y_dict.keys())

    def max_frame_id(self) -> int:
        return max(self.__drift_y_dict.keys())

    def _mm_per_pixel(self, frame_id):
        return self.__mm_per_pixel_dict[frame_id]

    def __drift_x(self, frame_id: int) -> float:
        return self.__drift_x_dict[frame_id]

    def __drift_y(self, frame_id: int) -> float:
        return self.__drift_y_dict[frame_id]

    def get_drift(self, frame_id: int) -> Vector:

        drift_x = self.__drift_x(frame_id)
        drift_y = self.__drift_y(frame_id)
        return Vector(drift_x, drift_y)

    def zoom_factor(self, frame_id: int) -> float:
        if frame_id <= self.min_frame_id():
            return 1

        scale_this = self._mm_per_pixel(frame_id)
        scale_prev = self._mm_per_pixel(frame_id - 1)

        change = scale_this / scale_prev
        return change


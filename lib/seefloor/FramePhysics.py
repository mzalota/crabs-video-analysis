from lib.imageProcessing.Camera import Camera
from lib.model.Vector import Vector
from lib.model.Point import Point


class FramePhysics:

    def __init__(self, drift, zoom):
        # type: (int, float, Vector, float) -> FramePhysics
        self.__drift = drift
        self.__zoom = zoom

    def translate_forward(self, point: Point) -> Point:
        depth_scaling_factor = self.__zoom
        drift_forward = self.__drift
        point_after_drift = point.translate_by_float(drift_forward)
        return self._adjust_location_for_depth_change_zoom(point_after_drift, depth_scaling_factor)

    def translate_backward(self, point: Point) -> Point:
        drift_backward = self.__drift.invert()
        depth_scaling_factor_backward = 1 / self.__zoom
        point_after_drift = point.translate_by_float(drift_backward)
        return self._adjust_location_for_depth_change_zoom(point_after_drift, depth_scaling_factor_backward)

    @staticmethod
    def _adjust_location_for_depth_change_zoom(point: Point, scaling_factor: float) -> Point:
        create = Camera.create()

        mid_frame_width = create.frame_width() / 2
        x_offset_from_middle_old = point.x - mid_frame_width
        x_offset_from_middle_new = x_offset_from_middle_old / scaling_factor
        new_x = mid_frame_width + x_offset_from_middle_new

        mid_frame_height = create.frame_height() / 2
        y_offset_from_middle_old = point.y - mid_frame_height
        y_offset_from_middle_new = y_offset_from_middle_old / scaling_factor
        new_y = mid_frame_height + y_offset_from_middle_new

        return Point(new_x, new_y)

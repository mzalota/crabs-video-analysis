from lib.Camera import Camera
from lib.model.Vector import Vector
from lib.model.Point import Point


class FramePhysics:

    def __init__(self, frame_id, scale, drift, zoom):
        # type: (int, float, Vector, float) -> FramePhysics
        self.__frame_id = frame_id
        self.__drift = drift
        self.__scale = scale
        self.__zoom = zoom

    def translate_forward(self, pointLocation: Point) -> Point:
        drift = self.__drift
        depth_scaling_factor = self.__zoom
        return self.__translate(pointLocation, drift, depth_scaling_factor)

    def translate_backward(self, pointLocation: Point) -> Point:
        drift = self.__drift.invert()
        depth_scaling_factor = 1 / self.__zoom
        return self.__translate(pointLocation, drift, depth_scaling_factor)

    def __translate(self, pointLocation: Point, drift: Vector, depth_scaling_factor: float):
        point_after_drift = pointLocation.translate_by_float(drift)
        point_after_depth_scaling = self._adjust_location_for_depth_change_zoom(point_after_drift, depth_scaling_factor)
        return point_after_depth_scaling

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

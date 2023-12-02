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

    #scaling factor greater than 1 means that seefloor got further away. Everything got smaller. Everything on the image got closer to the center of the image (fewer pixels away from center).
    @staticmethod
    def _adjust_location_for_depth_change_zoom(point: Point, scaling_factor: float) -> Point:
        camera = Camera.create()
        frame_center_point = camera.center_point()

        x_offset_from_middle_old = point.x - frame_center_point.x
        x_offset_from_middle_new = x_offset_from_middle_old / scaling_factor
        new_x = frame_center_point.x + x_offset_from_middle_new

        y_offset_from_middle_old = point.y - frame_center_point.y
        y_offset_from_middle_new = y_offset_from_middle_old / scaling_factor
        new_y = frame_center_point.y + y_offset_from_middle_new

        return Point(new_x, new_y)

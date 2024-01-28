from __future__ import annotations

from lib.imageProcessing.Camera import Camera
from lib.model.Vector import Vector
from lib.model.Point import Point


class FramePhysics:

    def __init__(self, drift: Vector, zoom: float) -> FramePhysics:
        self.__drift = drift
        self.__zoom = zoom

    def translate_forward(self, point: Point) -> Point:
        drift_forward_at_center = self.__drift
        depth_scaling_factor = self.__zoom

        translated_point = self.translate_internal2(depth_scaling_factor, drift_forward_at_center, point)
        return translated_point

    def translate_backward(self, point: Point) -> Point:
        drift_backward_at_center = self.__drift.invert()
        depth_scaling_factor_backward = 1 / self.__zoom

        translated_point = self.translate_internal2(depth_scaling_factor_backward, drift_backward_at_center, point)
        return translated_point

    def translate_internal2(self, depth_scaling_factor, drift_at_center, point):
        camera = Camera.create()
        distortion_at_point = camera.distortion_at_point_vector(point)
        distortion_at_center = camera.distortion_at_center()
        x_drift_at_point = (drift_at_center.x / distortion_at_center.x) * distortion_at_point.x
        y_drift_at_point = (drift_at_center.y / distortion_at_center.y) * distortion_at_point.y
        drift_vector_optical_at_point = Vector(x_drift_at_point, y_drift_at_point)
        point_after_drift = point.translate_by_vector(drift_vector_optical_at_point)

        correction_for_zoom = FramePhysics.zoom_compensation(point_after_drift, depth_scaling_factor)

        return point_after_drift.translate_by_vector(correction_for_zoom)

    #scaling factor greater than 1 means that seefloor got further away. Everything got smaller. Everything on the image got closer to the center of the image (fewer pixels away from center).
    @staticmethod
    def _adjust_location_for_depth_change_zoom(point: Point, scaling_factor: float) -> Point:
        correction_for_zoom = FramePhysics.zoom_compensation(point, scaling_factor)
        return Vector.create_from(point).plus(correction_for_zoom)


    @staticmethod
    def zoom_compensation(point, scaling_factor):
        camera = Camera.create()
        frame_center_point = camera.center_point()
        # frame_center_point = camera.get_optical_center()
        x_offset_from_middle_old = point.x - frame_center_point.x
        x_offset_from_middle_new = x_offset_from_middle_old / scaling_factor
        y_offset_from_middle_old = point.y - frame_center_point.y
        y_offset_from_middle_new = y_offset_from_middle_old / scaling_factor
        correction_for_zoom = Vector(x_offset_from_middle_new - x_offset_from_middle_old,
                                     y_offset_from_middle_new - y_offset_from_middle_old)
        return correction_for_zoom

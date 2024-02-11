from __future__ import annotations

from lib.imageProcessing.Camera import Camera
from lib.model.Point import Point
from lib.model.Vector import Vector
from lib.seefloor.VerticalSpeed import VerticalSpeed


class SeefloorFrame:
    def __init__(self, drift: Vector, zoom: float) -> SeefloorFrame:
        self.__drift = drift
        self.__zoom = zoom

    def _get_zoom(self):
        return self.__zoom

    def _get_drift(self):
        return self.__drift

    def translate_forward(self, point: Point) -> Point:
        drift_forward_at_center = self._get_drift()
        depth_scaling_factor = self._get_zoom()

        correction_for_zoom = self.__zoom_compensation(point, depth_scaling_factor)

        point_after_drift = point.translate_by_vector(drift_forward_at_center)
        return point_after_drift.translate_by_vector(correction_for_zoom)

    def translate_backward(self, point: Point) -> Point:
        drift_backward_at_center = self._get_drift().invert()
        depth_scaling_factor_backward = 1 / self._get_zoom()

        correction_for_zoom = self.__zoom_compensation(point, depth_scaling_factor_backward)

        point_after_drift = point.translate_by_vector(drift_backward_at_center)
        return point_after_drift.translate_by_vector(correction_for_zoom)


    def __zoom_compensation(self, point, scaling_factor):
        return VerticalSpeed.zoom_correction(point,scaling_factor)

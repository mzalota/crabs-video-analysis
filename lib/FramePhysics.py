from lib.Frame import Frame
from lib.common import Point


class FramePhysics:

    def __init__(self, frame_id, scale, drift, zoom):
        # type: (int, float, Vector, float) -> FramePhysics
        self.__frame_id = frame_id
        self.__drift = drift
        self.__scale = scale
        self.__zoom = zoom

    def translate_forward(self, pointLocation):
        # type: (Point, int) -> Point

        drift = self.__drift
        depth_scaling_factor = self.__zoom

        return self.__translate(pointLocation, drift, depth_scaling_factor)

    def translate_backward(self, pointLocation):
        # type: (Point, int) -> Point
        drift = self.__drift.invert()
        depth_scaling_factor = 1/self.__zoom

        return self.__translate(pointLocation, drift, depth_scaling_factor)

    def __translate(self, pointLocation, drift, depth_scaling_factor):
        point_after_drift = pointLocation.translateBy(drift)
        point_after_depth_scaling = self._adjust_location_for_depth_change_zoom(point_after_drift, depth_scaling_factor)
        return point_after_depth_scaling

    @staticmethod
    def _adjust_location_for_depth_change_zoom(point, scaling_factor):
        # type: (Point, float) -> Point
        mid_frame_width = Frame.FRAME_WIDTH / 2
        x_offset_from_middle_old = point.x - mid_frame_width
        x_offset_from_middle_new = x_offset_from_middle_old / scaling_factor
        new_x = mid_frame_width + x_offset_from_middle_new

        mid_frame_height = Frame.FRAME_HEIGHT / 2
        y_offset_from_middle_old = point.y - mid_frame_height
        y_offset_from_middle_new = y_offset_from_middle_old / scaling_factor
        new_y = mid_frame_height + y_offset_from_middle_new

        return Point(int(new_x), int(new_y))
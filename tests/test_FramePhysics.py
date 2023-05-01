from unittest import TestCase

from lib.Frame import Frame
from lib.FramePhysics import FramePhysics
from lib.common import Vector, Point
from lib.data.SeeFloorNoBadBlocks import SeeFloorNoBadBlocks


class TestFramePhysics(TestCase):
    _center_point = Point(Frame._FRAME_WIDTH_HIGH_RES / 2, Frame._FRAME_HEIGHT_HIGH_RES / 2)

    def test_adjust_zoom_location_depth_not_changed(self):
        #setup
        feature_location = self._center_point
        depth_change = 1

        #exercise
        result = FramePhysics._adjust_location_for_depth_change_zoom(feature_location, depth_change)

        #assert
        self.assertEqual(Frame._FRAME_WIDTH_HIGH_RES / 2, result.x)
        self.assertEqual(Frame._FRAME_HEIGHT_HIGH_RES / 2, result.y)

    def test_adjust_zoom_location__depth_doubled__center_point_stayed(self):
        #setup
        feature_location = self._center_point
        depth_change = 2

        #exercise
        result = FramePhysics._adjust_location_for_depth_change_zoom(feature_location, depth_change)

        #assert
        self.assertEqual(Frame._FRAME_WIDTH_HIGH_RES / 2, result.x)
        self.assertEqual(Frame._FRAME_HEIGHT_HIGH_RES / 2, result.y)

    def test_adjust_zoom_location__depth_halved__right_bottom_point_moved(self):
        #setup
        feature_location = self._center_point.translateBy(Vector(10, 10))
        depth_change = 0.5 # depth is half the previous. All points on new frame are further away from center compared to previous frame

        #exercise
        result = FramePhysics._adjust_location_for_depth_change_zoom(feature_location, depth_change)

        #assert
        self.assertEqual((Frame._FRAME_WIDTH_HIGH_RES / 2) + 20, result.x) #X dimention oved out by 20
        self.assertEqual((Frame._FRAME_HEIGHT_HIGH_RES / 2) + 20, result.y) #Y dimention moved out by 20

    def test_adjust_zoom_location__depth_doubled__left_upper_point_moved(self):
        #setup
        feature_location = self._center_point.translateBy(Vector(-66, -66))
        depth_change = 2 # all points appear closer to center on this frame image, compared to previous frame

        #exercise
        result = FramePhysics._adjust_location_for_depth_change_zoom(feature_location, depth_change)

        #assert
        self.assertEqual((Frame._FRAME_WIDTH_HIGH_RES / 2) - 33, result.x) #X dimention oved in by 33, instead of 66
        self.assertEqual((Frame._FRAME_HEIGHT_HIGH_RES / 2) - 33, result.y) #Y dimention moved in by 33, instead of 66

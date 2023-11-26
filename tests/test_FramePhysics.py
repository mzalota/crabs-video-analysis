from os import getcwd, chdir
from unittest import TestCase

from lib.imageProcessing.Camera import Camera
from lib.Frame import Frame
from lib.seefloor.FramePhysics import FramePhysics
from lib.model.Vector import Vector
from lib.model.Point import Point


class TestFramePhysics(TestCase):
    _center_point = Point(Frame._FRAME_WIDTH_HIGH_RES / 2, Frame._FRAME_HEIGHT_HIGH_RES / 2)

    def setUp(self):
        #set current working directory to be not in "tests" subfolder, but one level above together with resource
        #Otherwise Camera() class does not find  _mtx.py file
        self.__filepath = getcwd()
        chdir('../')
        Camera.initialize_4k()

    def tearDown(self) -> None:
        #reset current working directory to be
        chdir(self.__filepath)

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


    def test_change_than_reverse(self):
        #setup
        zoom = 0.9997025696116583
        physics = FramePhysics(Vector(3, 11), zoom)
        point = Point(1000, 1000)

        #exercise
        point_forward = physics.translate_forward(point)
        point_back = physics.translate_backward(point_forward)

        #assert
        self.assertAlmostEqual(point_back.x, point.x, 2)
        self.assertAlmostEqual(point_back.y, point.y, 2)

    def test_change_than_reverse2(self):
        #setup
        zoom = 1.0071198209766583
        physics = FramePhysics(Vector(-0.9365915776278864, 5.538252792970677), zoom)
        point = Point(1000, 1000)

        #exercise
        point_forward = physics.translate_forward(point)
        point_back = physics.translate_backward(point_forward)

        #assert

        self.assertAlmostEqual(point_back.x, point.x, 1)
        self.assertAlmostEqual(point_back.y, point.y, 1)

        self.assertAlmostEqual(point_forward.y, 1005.668, 2)

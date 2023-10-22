import os
from os import getcwd
from unittest import TestCase

from lib.Camera import Camera
from lib.model.Point import Point
from lib.data.CrabsData import CrabsData
from lib.model.Crab import Crab


class TestCrab(TestCase):
    def setUp(self):
        #set current working directory to be not in "tests" subfolder, but one level above together with resource
        #Otherwise Camera() class does not find  _mtx.py file
        self.__filepath = getcwd()
        os.chdir('../')
        Camera.initialize_4k()

    def tearDown(self) -> None:
        #reset current working directory to be
        os.chdir(self.__filepath)

    def test_add_crab_entry(self):
        #setup
        crab_data = CrabsData(None)

        crab = Crab(3049, Point(3033,77), Point(3065,33))
        crab_data.add_crab_entry(crab)

        #exercise
        result = crab_data.getCount()

        #assert
        self.assertEqual(1, result)

    def test_width_px(self):
        # setup
        crab = Crab(3049, Point(3033, 77), Point(3065, 33))

        #exercise
        #assert
        self.assertAlmostEqual(float(54.4059), crab.width_px(), 4)
        self.assertAlmostEqual(float(67.2681), crab.width_px_undistorted(), 4)

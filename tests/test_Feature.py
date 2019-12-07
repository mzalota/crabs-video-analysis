from unittest import TestCase

from lib.data.DriftData import DriftData
from lib.Feature import Feature
from lib.common import Point
import pandas as pd

class TestFeature(TestCase):

    def test_Feature_closeToFirstAndLastFrame_returnsNone(self):
        # Setup
        df = pd.DataFrame()
        #df = pd.DataFrame(columns=['frameNumber', 'driftY'])

        df = df.append({'frameNumber': int(71), 'driftY': 13, 'driftX': -3}, ignore_index=True)
        df = df.append({'frameNumber': int(73), 'driftY': 13, 'driftX': -3}, ignore_index=True)
        df = df.append({'frameNumber': int(75), 'driftY': 13, 'driftX': -3}, ignore_index=True)
        driftData = DriftData(df)

        location = Point(1442,608)
        box_size = 200

        # Exercise
        feature_firstFrame = Feature(driftData,71,location,box_size)
        feature_middleFrame = Feature(driftData,73,location,box_size)
        feature_lastFrame = Feature(driftData,75,location,box_size)

        # Assert
        self.assertIsNotNone(feature_firstFrame)
        self.assertIsNotNone(feature_middleFrame)
        self.assertIsNotNone(feature_lastFrame)


    def test_Feature_frameAfterLast_throwsValueErrorException(self):
        # Setup
        df = pd.DataFrame()
        df = df.append({'frameNumber': int(71), 'driftY': 13, 'driftX': -3}, ignore_index=True)
        df = df.append({'frameNumber': int(73), 'driftY': 13, 'driftX': -3}, ignore_index=True)
        df = df.append({'frameNumber': int(75), 'driftY': 13, 'driftX': -3}, ignore_index=True)
        driftData = DriftData(df)

        location = Point(1442,608) # some valid value that is irrelevant for the test
        box_size = 200 # some valid value that is irrelevant for the test

        # Exercise
        with self.assertRaises(Exception) as cm:
            Feature(driftData,77, location, box_size)

        the_exception = cm.exception

        # Assert
        self.assertIsInstance(the_exception, ValueError)
        self.assertEqual(the_exception.message, "Frame Number above maximum. Passed frame: 77. Maximum frame: 75")

    def test_Feature_frameBeforeFirst_throwsValueErrorException(self):
        # Setup
        df = pd.DataFrame()
        df = df.append({'frameNumber': int(71), 'driftY': 13, 'driftX': -3}, ignore_index=True)
        df = df.append({'frameNumber': int(73), 'driftY': 13, 'driftX': -3}, ignore_index=True)
        df = df.append({'frameNumber': int(75), 'driftY': 13, 'driftX': -3}, ignore_index=True)
        driftData = DriftData(df)

        location = Point(1442,608) # some valid value that is irrelevant for the test
        box_size = 200 # some valid value that is irrelevant for the test

        # Exercise
        with self.assertRaises(Exception) as cm:
            Feature(driftData, 60, location, box_size)

        the_exception = cm.exception

        # Assert
        self.assertIsInstance(the_exception, ValueError)
        self.assertEqual(the_exception.message, "Frame Number below minimum. Passed frame: 60. Minimum frame: 71")

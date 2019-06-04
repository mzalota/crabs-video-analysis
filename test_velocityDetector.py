from unittest import TestCase

from lib.VelocityDetector import VelocityDetector
from lib.common import Vector


class TestVelocityDetector(TestCase):

    def test_getDriftsCount_zeroZero(self):
        vd = VelocityDetector()

        actual = vd.excludeOutliers([Vector(0, 0),Vector(-6, 41),Vector(-6, 41),Vector(-6, 41)])

        # Assert
        expected = [Vector(-6, 41), Vector(-6, 41), Vector(-6, 41)]
        self.assertEqual(Vector.vectorArrayAsString(actual), Vector.vectorArrayAsString(expected))

    def test_getDriftsCount_2outliersAboveMedian(self):
        vd = VelocityDetector()

        actual = vd.excludeOutliers([Vector(-5,44), Vector(-5,44), Vector(-5,43), Vector(30,526), Vector(30,526)])

        # Assert
        expected = [Vector(-5,44), Vector(-5,44), Vector(-5,43)]
        self.assertEqual(3, len(expected))
        self.assertEqual(3, len(actual))
        self.assertEqual( Vector.vectorArrayAsString(actual), Vector.vectorArrayAsString(expected))


    def ttest_getDriftsCount_outlierIsSymmetricalOverZero(self):
        vd = VelocityDetector()

        actual = vd.excludeOutliers([Vector(0,30), Vector(0,30), Vector(0,-32)])

        # Assert
        expected = [Vector(0,30), Vector(0,30)]
        self.assertEqual(2, len(expected))
        self.assertEqual(2, len(actual))
        self.assertEqual( Vector.vectorArrayAsString(actual), Vector.vectorArrayAsString(expected))

    def test_getDriftsCount_outlierIsMinimal(self):
        vd = VelocityDetector()

        actual = vd.excludeOutliers([Vector(47, -408),Vector(-6, 41),Vector(-6, 41),Vector(-6, 41)])

        # Assert
        expected = [Vector(-6, 41), Vector(-6, 41), Vector(-6, 41)]
        self.assertEqual(3, len(expected))
        self.assertEqual(3, len(actual))
        self.assertEqual( Vector.vectorArrayAsString(actual), Vector.vectorArrayAsString(expected))

    def test_getDriftsCount_outlierIsMinimalTotal3Values(self):

        vd = VelocityDetector()

        actual = vd.excludeOutliers([Vector(47, -408),Vector(-6, 41),Vector(-6, 41)])

        #Assert
        expected = [Vector(-6, 41), Vector(-6, 41)]
        self.assertEqual(2, len(expected))
        self.assertEqual(2, len(actual))
        self.assertEqual( Vector.vectorArrayAsString(actual), Vector.vectorArrayAsString(expected))


    def test_getDriftsCount_twoValuesButVeryDifferent(self):

        vd = VelocityDetector()

        actual = vd.excludeOutliers([Vector(47, -408),Vector(-6, 41)])

        # Assert
        expected = [Vector(47, -408),Vector(-6, 41)]
        self.assertEqual(2, len(expected))
        self.assertEqual(2, len(actual))
        self.assertEqual( Vector.vectorArrayAsString(actual), Vector.vectorArrayAsString(expected))


    def test_replaceOutlier(self):
        vd = VelocityDetector()

        actual = vd.replaceOutlier(29, 30, 300, 32, 33)

        # Assert
        self.assertEqual( actual, 31)


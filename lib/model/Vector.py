from __future__ import annotations

import math

import numpy

from lib.model.Point import Point


class Vector(Point):
    # def __init__(self, point):
    #     self.x = point.x
    #     self.y = point.y

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str(Point(self.x, self.y))

    @staticmethod
    def vectorArrayAsString(vectorArray):
        if len(vectorArray) <= 0:
            return ""
        concatStr = [str(x) for x in vectorArray]
        return concatStr

    @staticmethod
    def medianLengthOfVectorArray(vectorArray):
        if len(vectorArray) <= 0:
            return None

        drift_pixels = list()
        for drift in vectorArray:
            drift_pixels.append(drift.length())
        return numpy.median(drift_pixels)

    def invert(self) -> Vector:
        return Vector((-1) * self.x, (-1) * self.y)

    def isZeroVector(self):
        if self.x == 0 and self.y == 0:
            return True
        else:
            return False

    def length(self):
        # type: () -> decimal
        zeroPoint = Point(0, 0)
        endPoint = Point(self.x, self.y)
        return zeroPoint.distanceTo(endPoint)

    def angle(self):
        if self.x == 0:
            # we want to avoid deviding by zero, hence we checked if x==0
            if self.y == 0:
                # both x and y are zero so angle is also zero degrees
                return 0
            if self.y < 0:
                # vector pointing straight south -> angle is -90 degrees
                return -90
            if self.y > 0:
                # vector pointing straight north -> angle is +90 degrees
                return 90

        # tan(theta) = Opposite / Adjacent
        return math.degrees(math.atan(self.y / self.x))

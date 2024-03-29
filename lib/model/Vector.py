from __future__ import annotations

import math

import numpy
import numpy as np

from lib.model.Point import Point


class Vector(Point):
    def __init__(self, x, y):
        if np.isnan(x) or x is None:
            x = 0
        if np.isnan(y) or y is None:
            y = 0
        self.x = x
        self.y = y

    def __str__(self):
        return str(Point(self.x, self.y))

    @staticmethod
    def create_from(point: Point) -> Vector:
        return Vector(point.x, point.y)

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

    def minus(self, vector: Vector) -> Vector:
        return Vector(self.x - vector.x, self.y - vector.y)

    def plus(self, vector: Vector) -> Vector:
        return self.minus(vector.invert())

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

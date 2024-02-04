from __future__ import annotations

import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def from_string(point_as_string):
        if point_as_string[0] != "(":
            return

        if point_as_string[-1] != ")":
            return

        # remove enclosing ( and )
        point_nobrackets = point_as_string[1:-1]
        coordinates = point_nobrackets.split(",")

        if len(coordinates) != 2:
            return

        return Point(int(coordinates[0]), int(coordinates[1]))

    def copy(self) -> Point:
        return Point(self.x, self.y)

    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def calculateMidpoint(self, point2: Point) -> Point:
        x1 = self.x
        y1 = self.y
        x2 = point2.x
        y2 = point2.y

        xDist = math.fabs(x2 - x1)
        yDist = math.fabs(y2 - y1)
        xMid = int(x2 - math.ceil(xDist / 2))
        yMid = int(y2 - math.ceil(yDist / 2))

        return Point(xMid, yMid)

    def distanceTo(self, otherPoint: Point) -> float:
        x1 = self.x
        y1 = self.y
        x2 = otherPoint.x
        y2 = otherPoint.y

        dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return dist

    # def translateBy(self, vector: Vector) -> Point:
    def translateBy(self, vector: Point) -> Point:
        vector_floats = self.translate_by_vector(vector)
        #round to integer
        return Point(int(round(vector_floats.x)), int(round(vector_floats.y)))

    def translate_by_vector(self, vector: Point) -> Point:
        return Point(self.x + vector.x, self.y + vector.y)

    def translate_by_xy(self, x: int, y: int) -> Point:
        return self.translateBy(Point(x, y))

from __future__ import annotations

from lib.model.Point import Point
from lib.model.Vector import Vector


class Box:
    # topLeft = Point(0,0)
    # bottomRight = Point(100, 100)

    def __init__(self, topLeft, bottomRight):
        # type: (Point, Point) -> Box
        self.bottomRight = bottomRight
        self.topLeft = topLeft

    @staticmethod
    def from_string(box_as_string: str) -> Box:
        if box_as_string[0] != "[":
            return

        if box_as_string[-1] != "]":
            return

        # remove enclosing [ and ]
        two_points = box_as_string[1:-1]
        points = two_points.split(":")
        if len(points) != 2:
            return

        point1 = Point.from_string(points[0])
        point2 = Point.from_string(points[1])

        if not point1:
            return

        if not point2:
            return


        return Box(point1, point2)

    @staticmethod
    def __ddd( points_0):
        if points_0[0] != "(":
            return

        if points_0[-1] != ")":
            return

        # remove enclosing ( and )
        point1_nobrackets = points_0[1:-1]
        coordinates = point1_nobrackets.split(",")
        if len(coordinates) != 2:
            return

        return Point(int(coordinates[0]), int(coordinates[1]))


    def __str__(self):
        return "[" + str(self.topLeft) + ":" + str(self.bottomRight) + "]"

    @staticmethod
    def createUsingDimesions(x_width, y_height):
        # type: (int, int) -> Box
        return Box(Point(0, 0), Point(x_width, y_height))

    @staticmethod
    def boxAroundPoint(point : Point, boxSize: int) -> Box:
        offset = int(boxSize / 2)
        return Box(Point(max(point.x - offset, 1), max(point.y - offset, 1)), Point(point.x + offset, point.y + offset))

    def width(self):
        return self.bottomRight.x - self.topLeft.x

    def height(self):
        return self.bottomRight.y - self.topLeft.y

    def diagonal(self):
        return self.topLeft.distanceTo(self.bottomRight)

    def area(self):
        return self.width() * self.height()

    def centerPoint(self) -> Point:
        return self.topLeft.calculateMidpoint(self.bottomRight)

    def distanceTo(self, otherBox):
        # type: (Box) -> int
        return int(self.topLeft.distanceTo(otherBox.topLeft))

    def translateCoordinateToOuter(self, topLeftOuterPoint):
        # type: (Point) -> Box
        topLeftX = topLeftOuterPoint.x + self.topLeft.x
        topLeftY = topLeftOuterPoint.y + self.topLeft.y
        bottomRightX = topLeftOuterPoint.x + self.bottomRight.x
        bottomRightY = topLeftOuterPoint.y + self.bottomRight.y

        return Box(Point(topLeftX, topLeftY), Point(bottomRightX, bottomRightY))

    def translateBy(self, vector: Vector):
        newTopLeft = self.topLeft.translateBy(vector)
        newBottomRight = self.bottomRight.translateBy(vector)
        return Box(newTopLeft, newBottomRight)

    def translate_by_xy(self, x: int, y: int):
        return self.translateBy(Vector(x, y))


def boxAroundBoxes(box1, box2):
    topLeft = Point(min(box1.topLeft.x, box2.topLeft.x), min(box1.topLeft.y, box2.topLeft.y))
    bottomRight = Point(max(box1.bottomRight.x, box2.bottomRight.x), max(box1.bottomRight.y, box2.bottomRight.y))
    return Box(topLeft, bottomRight)

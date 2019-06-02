#from collections import namedtuple

import math
import numpy


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+")"

    def calculateMidpoint(self, point2):
        # type: (Point) -> Point
        x1 = self.x
        y1 = self.y
        x2 = point2.x
        y2 = point2.y

        xDist = math.fabs(x2 - x1)
        yDist = math.fabs(y2 - y1)
        xMid = int(x2 - math.ceil(xDist / 2))
        yMid = int(y2 - math.ceil(yDist / 2))

        return Point(xMid, yMid)

    def distanceTo(self, otherPoint):
        # type: (Point) -> decimal
        x1 = self.x
        y1 = self.y
        x2 = otherPoint.x
        y2 = otherPoint.y

        dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return dist

    def translateBy(self, vector):
        # type: (Vector) -> Point
        return Point(self.x+int(vector.x), int(self.y+vector.y))


    def boxAroundPoint(self, boxSize):
        offset = int(boxSize/2)
        return Box(Point(max(self.x - offset, 1), max(self.y - offset, 1)), Point(self.x + offset, self.y + offset))

class Vector:
    def __init__(self, point):
        self.x = point.x
        self.y = point.y

    def __str__(self):
        return str(Point(self.x,self.y))

    def __init__(self, x,y):
        self.x = x
        self.y = y

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


    def isZeroVector(self):
        if self.x == 0 and self.y == 0:
            return True
        else:
            return False

    def length(self):
        zeroPoint = Point(0,0)
        endPoint = Point(self.x, self.y)
        return zeroPoint.distanceTo(endPoint)

    def angle(self):
        if self.x == 0:
            #we want to avoid deviding by zero, hence we checked if x==0
            if self.y == 0:
                #both x and y are zero so angle is also zero degrees
                return 0
            if self.y <0:
                #vector pointing streight south -> angle is -90 degrees
                return -90
            if self.y > 0:
                #vector pointing streight north -> angle is +90 degrees
                return 90

        # tan(theta) = Opposite / Adjacent
        return math.degrees(math.atan(self.y/self.x))

    def asPoint(self):
        return Point(self.x, self.y)



class Box:
    #topLeft = Point(0,0)
    #bottomRight = Point(100, 100)

    def __init__(self, topLeft, bottomRight):
        # type: (Point, Point) -> Box
        self.bottomRight = bottomRight
        self.topLeft = topLeft

    def __str__(self):
        return "["+str(self.topLeft)+":"+str(self.bottomRight)+"]"

    def width(self):
        return self.bottomRight.x - self.topLeft.x

    def hight(self):
        return self.bottomRight.y - self.topLeft.y

    def diagonal(self):
        return self.topLeft.distanceTo(self.bottomRight)

    def centerPoint(self):
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

def boxAroundBoxes(box1, box2):
    topLeft= Point(min(box1.topLeft.x, box2.topLeft.x), min(box1.topLeft.y, box2.topLeft.y))
    bottomRight= Point(max(box1.bottomRight.x, box2.bottomRight.x), max(box1.bottomRight.y, box2.bottomRight.y))
    return Box(topLeft, bottomRight)

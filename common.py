from collections import namedtuple

import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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

class Vector:
    def __init__(self, point):
        self.x = point.x
        self.y = point.y

    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+")"

    def __init__(self, x,y):
        self.x = x
        self.y = y

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
        self.bottomRight = bottomRight
        self.topLeft = topLeft

    def width(self):
        return self.bottomRight.x - self.topLeft.x
    def hight(self):
        return self.bottomRight.y - self.topLeft.y
    def diagonal(self):
        return self.topLeft.distanceTo(self.bottomRight)



def boxAroundBoxes(box1, box2):
    topLeft= Point(min(box1.topLeft.x, box2.topLeft.x), min(box1.topLeft.y, box2.topLeft.y))
    bottomRight= Point(max(box1.bottomRight.x, box2.bottomRight.x), max(box1.bottomRight.y, box2.bottomRight.y))
    return Box(topLeft, bottomRight)

def translateCoordinateToOuter(innerBox, topLeftOuterPoint):
    """
    :param innerBox: Box
    :param topLeftOuterPoint: Point 
    :return: Box
    """
    topLeftX = topLeftOuterPoint.x + innerBox.topLeft.x
    topLeftY = topLeftOuterPoint.y + innerBox.topLeft.y
    bottomRightX = topLeftOuterPoint.x + innerBox.bottomRight.x
    bottomRightY = topLeftOuterPoint.y + innerBox.bottomRight.y

    return Box(Point(topLeftX, topLeftY), Point(bottomRightX, bottomRightY))

def distanceBetweenPointtts(point1,point2):
	x1 = point1.x
	y1 = point1.y
	x2 = point2.x
	y2 = point2.y

	dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
	return dist


def subImage(image, box):
    """
    :return: numpy.ndarray 
    """
    #print box
    return image[box.topLeft.y:box.bottomRight.y, box.topLeft.x: box.bottomRight.x]


def boxAroundPoint(point, boxSize):
    offset = int(boxSize/2)
    return Box(Point(max(point.x - offset, 1), max(point.y - offset, 1)), Point(point.x + offset, point.y + offset))
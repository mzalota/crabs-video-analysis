from collections import namedtuple

import math

Point = namedtuple('Point', 'x y')
#Box = namedtuple('Box', 'topLeft bottomRight')

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


def boxAroundBoxes(box1, box2):
    topLeft= Point(min(box1.topLeft.x, box2.topLeft.x), min(box1.topLeft.y, box2.topLeft.y))
    bottomRight= Point(max(box1.bottomRight.x, box2.bottomRight.x), max(box1.bottomRight.y, box2.bottomRight.y))
    return Box(topLeft, bottomRight)


def calculateMidpoin2(point1, point2):
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]

    xDist = math.fabs(x2 - x1)
    yDist = math.fabs(y2 - y1)
    xMid = (x2 - math.ceil(xDist / 2))
    yMid = (y2 - math.ceil(yDist / 2))

    return (xMid, yMid)

def calculateMidpoint(point1, point2):
    # type: (Point, Point) -> Point
    x1 = point1.x
    y1 = point1.y
    x2 = point2.x
    y2 = point2.y

    xDist = math.fabs(x2 - x1)
    yDist = math.fabs(y2 - y1)
    xMid = int(x2 - math.ceil(xDist / 2))
    yMid = int(y2 - math.ceil(yDist / 2))

    return Point(xMid, yMid)

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

def distanceBetweenPoints(point1,point2):
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
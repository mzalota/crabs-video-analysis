from collections import namedtuple

import math

Point = namedtuple('Point', 'x y')
Box = namedtuple('Box', 'topLeft bottomRight')


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
    print box
    return image[box.topLeft.y:box.bottomRight.y, box.topLeft.x: box.bottomRight.x]

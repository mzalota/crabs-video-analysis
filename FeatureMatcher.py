import uuid

import cv2
import numpy as np
from skimage import measure

from ImageWindow import ImageWindow
from common import Box, Point, subImage, boxAroundPoint, calculateMidpoint


class FeatureMatcher:
    __featureBoxSize = 100
    __defaultStartingPoint = Point(500, 500)
    __prev_subImage = None
    __featureLocation = None

    def __init__(self, startingPoint, boxSize = 100):
        self.__id = str(uuid.uuid4().fields[-1])[:5]
        self.__featureBoxSize = boxSize
        self.setFeatureLocation(startingPoint)
        self.__subImageWin = ImageWindow(self.__id, Point(50, 50))

    def setFeatureLocation(self, startingPoint):
        self.__defaultStartingPoint = startingPoint
        self.__featureLocation =startingPoint

    def __defaultBoxAroundFeature(self):
        return boxAroundPoint(self.__defaultStartingPoint, self.__featureBoxSize)

    def __defaultBoxAroundFeatur2(self):
        offsetY = 100
        offsetX = 200
        point = self.__defaultStartingPoint
        return Box(Point(max(point.x - offsetX, 1), max(point.y - offsetY, 1)), Point(point.x + offsetX, point.y + offsetY))
        #return boxAroundPoint(self.__defaultStartingPoint, self.__featureBoxSize)

    def getFeature(self, image):

        newBox = self.__findSubImage(image, self.__prev_subImage)
        if newBox is None:
            print "Did not detect feature: resetting Location to Default"
            newBox = self.__defaultBoxAroundFeature()
        if newBox.bottomRight.y >960:
            print "Got to the bottom of the screen: resetting location to default"
            newBox = self.__defaultBoxAroundFeature()

        if newBox.topLeft.x <=40:
            print "Got too close to the left edge: resetting location to default"
            newBox = self.__defaultBoxAroundFeature()

        self.__featureLocation = calculateMidpoint(newBox.topLeft, newBox.bottomRight)
        self.__prev_subImage = subImage(image, newBox)
        return newBox


    def __findSubImage(self, image, subImage):
        if subImage is None:
            return None

        # https: // www.geeksforgeeks.org / template - matching - using - opencv - in -python /
        # Convert it to grayscale
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        subImage_gray = cv2.cvtColor(subImage, cv2.COLOR_BGR2GRAY)

        self.__subImageWin.showWindow(subImage_gray)

        # Read the template
        # Store width and heigth of template in w and h
        d, w, h = subImage.shape[::-1]

        # Perform match operations.
        res = cv2.matchTemplate(img_gray, subImage_gray, cv2.TM_CCOEFF_NORMED)
        #res = cv2.matchTemplate(img_gray, subImage_gray, cv2.TM_CCORR_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # Specify a threshold (it was 0.8)
        threshold = 0.6 #0.6 has worked before
        newLocation = None
        if max_val >= threshold:
            newLocation = Box(Point(max_loc[0], max_loc[1]), Point(max_loc[0] + w, max_loc[1] + h))

        print "id, max_val, max_loc, shape, newLocation"
        print self.__id, max_val, max_loc, subImage_gray.shape, newLocation

        return newLocation


    def drawBoxOnImage(self, image):
        box = boxAroundPoint(self.__featureLocation, self.__featureBoxSize)
        cv2.rectangle(image, (box.topLeft.x, box.topLeft.y),
                      (box.bottomRight.x, box.bottomRight.y), (0, 255, 0), 2)
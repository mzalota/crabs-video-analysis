import uuid

import cv2
import numpy as np
from skimage import measure

from ImageWindow import ImageWindow
from common import Box, Point, subImage, boxAroundPoint, calculateMidpoint

class Feature:
    __id = None
    __subImageWin = None
    __image = None
    __location = None

    def __init__(self):
        self.__id = str(uuid.uuid4().fields[-1])[:5]
        #self.__image = image
        self.__subImageWin = ImageWindow(self.__id, Point(50, 50))

    def showSubImage(self):
        self.__subImageWin.showWindow(self.__image)

    def updateImage(self, image, location):
        self.__image = image
        self.__location = location
        #print "updateing Feature:"
        #print self.__id, location

    def getImage(self):
        return self.__image

    @staticmethod
    def infoHeaders():
        row = []
        row.append("featureId")
        row.append("featureX")
        row.append("featureY")
        return row

    def infoAboutFeature(self):
        row = []
        row.append(self.__id)
        row.append(self.__location.x)
        row.append(self.__location.y)

        return row



class FeatureMatcher:
    __featureBoxSize = 100
    __defaultStartingPoint = Point(500, 500)
    #__prev_subImage = None
    __featureLocation = None
    __threshold_for_matching = 0.6
    __detectionWasReset = False
    __correlation = 0
    __resetReason = ""

    def __init__(self, startingPoint, boxSize = 100):
        self.__id = str(uuid.uuid4().fields[-1])[:5]
        self.__featureBoxSize = boxSize
        self.setFeatureLocation(startingPoint)
        self.__subImageWin = ImageWindow(self.__id, Point(50, 50))
        self.__feature = Feature()

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

    def detectionWasReset(self):
        return self.__detectionWasReset

    def showSubImage(self):
        #self.__subImageWin.showWindow(self.__prev_subImage)
        self.__subImageWin.showWindow(self.__feature.getImage())

    def getFeature(self, image):

        #newBox = self.__findSubImage(image, self.__prev_subImage)
        newBox = self.__findSubImage(image, self.__feature.getImage())

        self.__detectionWasReset = True
        self.__resetReason = ""
        if newBox is None:
            print "Did not detect feature: resetting Location to Default"
            newBox = self.__defaultBoxAroundFeature()
            self.__detectionWasReset = False
            self.__resetReason = "NotDetected"
            self.__feature = Feature()

        if newBox.bottomRight.y >960:
            print "Got to the bottom of the screen: resetting location to default"
            newBox = self.__defaultBoxAroundFeature()
            self.__detectionWasReset = False
            self.__resetReason = "Bottom"
            self.__feature = Feature()

        if newBox.topLeft.x <=40:
            print "Got too close to the left edge: resetting location to default"
            newBox = self.__defaultBoxAroundFeature()
            self.__detectionWasReset = False
            self.__resetReason = "LeftEdge"
            self.__feature = Feature()


        self.__featureLocation = calculateMidpoint(newBox.topLeft, newBox.bottomRight)

        self.__feature.updateImage(subImage(image, newBox),self.__featureLocation)

        print self.__feature.infoAboutFeature()
        return newBox


    def __findSubImage(self, image, subImage):
        if subImage is None:
            return None



        # Algorithm is described here: https: // www.geeksforgeeks.org / template - matching - using - opencv - in -python /

        # Convert image and subImage to grayscale
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        subImage_gray = cv2.cvtColor(subImage, cv2.COLOR_BGR2GRAY)

        # Perform match operations.
        res = cv2.matchTemplate(img_gray, subImage_gray, cv2.TM_CCOEFF_NORMED)

        #determine which rechtangle on the image is the best fit for subImage (has the highest correlation)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        self.__correlation = max_val

        if max_val < self.__threshold_for_matching:
            # If the best matching box still has correlation below the "threshold" then declare defeat -> we could not find a match for subImage on this image
            return None

        # get w and h, so that we can reconstruct the box
        d, w, h = subImage.shape[::-1]
        topLeft = Point(max_loc[0], max_loc[1])
        bottomRight = Point(topLeft.x + w, topLeft.y + h)

        #print "id, max_val, max_loc, newLocation"
        #print self.__id, max_val, max_loc, newLocation

        return Box(topLeft, bottomRight)


    def drawBoxOnImage(self, image):
        box = boxAroundPoint(self.__featureLocation, self.__featureBoxSize)
        cv2.rectangle(image, (box.topLeft.x, box.topLeft.y),
                      (box.bottomRight.x, box.bottomRight.y), (0, 255, 0), 2)

    @staticmethod
    def infoHeaders():
        row = []
        row.append("featureId")
        row.append("boxSize")
        row.append("correlation")
        row.append("Reset")
        row.append("featureX")
        row.append("featureY")
        row.append("resetReason")
        return row

    def infoAboutFeature(self):
        row = []
        row.append(self.__id)
        row.append(self.__featureBoxSize)
        row.append(self.__correlation)
        if self.detectionWasReset():
            row.append("Yes")
            row.append(self.__featureLocation.x)
            row.append(self.__featureLocation.y)
        else:
            row.append("No")
            row.append(self.__featureLocation.x)
            row.append(self.__featureLocation.y)
            #row.append(-1)
            #row.append(-1)
        row.append(self.__resetReason)
        return row

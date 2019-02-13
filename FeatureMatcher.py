import uuid

import cv2
import numpy as np
from skimage import measure

from Frame import Frame
from ImageWindow import ImageWindow
from common import Box, Point, subImage, boxAroundPoint, calculateMidpoint

class Feature:
    __id = None
    __subImageWin = None

    def __init__(self, boxSize = 100):
        self.__id = str(uuid.uuid4().fields[-1])[:5]
        self.__featureBoxSize = boxSize
        self.__subImageWin = ImageWindow(self.__id, Point(50, 50))
        self.__image = None
        self.__images = dict()
        self.__topLeftPoints = dict()


    def __defaultBoxAroundFeature(self):
        return Box(self.__getTopLeft(), Point(self.__getTopLeft().x + self.__featureBoxSize, self.__getTopLeft().y + self.__featureBoxSize))

    def __getTopLeft(self):
        if len(self.__topLeftPoints)<1:
            return None
        #return self.__topLeftPoint
        lastPoint = self.__topLeftPoints[max(self.__topLeftPoints.keys())]

        #print "max lastPoint"
        #print self.__id, lastPoint, self.__topLeftPoints

        return lastPoint

    def __defaultBoxAroundFeatur2(self):
        offsetY = 100
        offsetX = 200
        point = self.__getTopLeft()
        return Box(Point(max(point.x - offsetX, 1), max(point.y - offsetY, 1)),
                   Point(point.x + offsetX, point.y + offsetY))

    def showSubImage(self):
        self.__subImageWin.showWindow(self.getImage())

    def pluckFeature(self, frame, topLeftPoint):
        print "max pluckFeature"
        print self.__id, topLeftPoint, self.__topLeftPoints

        #self.__topLeftPoint = topLeftPoint
        self.__topLeftPoints[frame.getFrameID()] = topLeftPoint #append
        image = subImage(frame.getImage(), self.__defaultBoxAroundFeature())
        self.__images[frame.getFrameID()] = image.copy()
        self.__image = image.copy()

    def drawBoxOnImage(self, image):
        box = self.__defaultBoxAroundFeature()
        cv2.rectangle(image, (box.topLeft.x, box.topLeft.y),
                      (box.bottomRight.x, box.bottomRight.y), (0, 255, 0), 2)

    def getImage(self):
        return self.__image
        #if len(self.__images)<1:
        #    return None
        #return self.__images[max(self.__images.keys())]

    def getLocation(self):
        box = self.__defaultBoxAroundFeature()
        newfeatureLocation = calculateMidpoint(box.topLeft, box.bottomRight)
        return newfeatureLocation

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
        row.append(self.getLocation().x)
        row.append(self.getLocation().y)

        return row



class FeatureMatcher:
    __featureBoxSize = 100
    __defaultStartingPoint = Point(500, 500)
    __threshold_for_matching = 0.6
    __detectionWasReset = False
    __correlation = 0
    __resetReason = ""

    def __init__(self, startingPoint, boxSize = 100):
        self.__id = str(uuid.uuid4().fields[-1])[:5]
        self.__featureBoxSize = boxSize
        self.__defaultStartingPoint = startingPoint
        self.__subImageWin = ImageWindow(self.__id, Point(50, 50))
        self.__feature = Feature(self.__featureBoxSize)

        print "WTF 00"
        print self.__defaultStartingPoint

    def detectionWasReset(self):
        return self.__detectionWasReset

    def showSubImage(self):
        self.__subImageWin.showWindow(self.__feature.getImage())

    def getFeature(self, frame):
        image = frame.getImage()



        newTopLeftOfFeature = self.__findSubImage(image, self.__feature.getImage())
        print "yyyyy "
        print newTopLeftOfFeature

        newTopLeftOfFeature = self.resetFeatureIfNecessary(newTopLeftOfFeature)

        self.__feature.pluckFeature(frame, newTopLeftOfFeature)

        print self.__feature.infoAboutFeature()
        return newTopLeftOfFeature

    def resetFeatureIfNecessary(self, newTopLeftOfFeature):
        print "WTF 10"
        print self.__defaultStartingPoint
        self.__detectionWasReset = True
        self.__resetReason = ""
        if newTopLeftOfFeature is None:
            print "Did not detect feature: resetting Location to Default"
            self.__resetReason = "NotDetected"
            newTopLeftOfFeature = self.resetFeature()
            print "WTF 30"
            print newTopLeftOfFeature
        if ((newTopLeftOfFeature.y + self.__featureBoxSize) > 1000):
            print "Got to the bottom of the screen: resetting location to default"
            self.__resetReason = "Bottom"
            newTopLeftOfFeature = self.resetFeature()
        if newTopLeftOfFeature.x <= 40:
            print "Got too close to the left edge: resetting location to default"
            self.__resetReason = "LeftEdge"
            newTopLeftOfFeature = self.resetFeature()


        print "WTF 100"
        print newTopLeftOfFeature
        return newTopLeftOfFeature

    def resetFeature(self):
        self.__detectionWasReset = False
        self.__feature = Feature(self.__featureBoxSize)
        return self.__defaultStartingPoint


    def __findSubImage(self, image, subImage):
        print "qqqqqqqqq "

        if subImage is None:
            return None

        print "xxxxx "
        print subImage.shape

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
        Point(topLeft.x + w, topLeft.y + h)

        return topLeft



    def drawBoxOnImage(self, image):
        self.__feature.drawBoxOnImage(image)

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
        else:
            row.append("No")
        row.append(self.__feature.getLocation().x)
        row.append(self.__feature.getLocation().y)

        row.append(self.__resetReason)
        return row

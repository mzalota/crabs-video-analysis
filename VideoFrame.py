import cv2
import numpy as np
from skimage.draw import polygon_perimeter

from RedDot import RedDot
from common import Point, Box, boxAroundBoxes, translateCoordinateToOuter, distanceBetweenPoints


#from wip01 import boxAroundBoxes, dotsShift, showWindow, Point


class VideoFrame:
    # initializing the variables
    __initialDistanceForRedBoxSearchArea=200
    dotsShift = 150
    boxAroundRedDotsAbsolute = None
    redDot1 = None
    redDot2 = None


    # defining constructor
    def __init__(self, image, prevFrame=None):
        self.image = image
        self.prevFrame = prevFrame

    def distanceBetweenRedPoints(self):
        if self.redDot1.dotWasDetected() and self.redDot2.dotWasDetected():
            return distanceBetweenPoints(self.redDot1.boxAroundDot.topLeft,self.redDot2.boxAroundDot.topLeft)
        else:
            if self.prevFrame:
                return self.prevFrame.distanceBetweenRedPoints()
            else:
                return self.__initialDistanceForRedBoxSearchArea

    def isolateRedDots(self):
        self.redDot1 = RedDot(True)
        self.redDot1.isolateRedDots(self.image, self.__redDotsSearchArea1())

        if self.redDot1.dotWasDetected():
            print "detected red dot 1:"
            print self.redDot1.boxAroundDot

        self.redDot2 = RedDot(True)
        self.redDot2.isolateRedDots(self.image, self.__redDotsSearchArea2())

        if self.redDot2.dotWasDetected():
            print "detected red dot 2:"
            print self.redDot2.boxAroundDot


    def drawBoxesAroundRedDots(self):
        #https://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html#gsc.tab=0

        image_with_boxes = np.copy(self.image)

        bounding_boxes = []
        #bounding_boxes = [self.redDot1.boxAroundDot, self.redDot2.boxAroundDot]
        if self.redDot1.dotWasDetected():
            bounding_boxes.append(self.redDot1.boxAroundDot)
        if self.redDot2.dotWasDetected():
            bounding_boxes.append(self.redDot2.boxAroundDot)

        for box in bounding_boxes:
            c = [box.topLeft.x, box.bottomRight.x, box.bottomRight.x, box.topLeft.x, box.topLeft.x]
            r = [box.bottomRight.y, box.bottomRight.y, box.topLeft.y, box.topLeft.y, box.bottomRight.y]
            rr, cc = polygon_perimeter(r, c, image_with_boxes.shape)
            image_with_boxes[rr, cc] = 1  # set color white
        return image_with_boxes


    def highlightMatchedFeatureeeeee(self):

        # resize(image, dst, Size(), 0.5, 0.5, interpolation);
        # print Box(Point(topLeftX,topLeftY), Point(bottomRightX,bottomRightY))
        # highlightMatchedFeature(image, featureImage)
        print "aaa"



    def __redDotsSearchArea1(self):
        print "in __redDotsSearchArea1"
        if self.redDot1.dotWasDetected() :
            return self.__updateRedDotsSearchArea(self.redDot1.boxAroundDot)
        elif self.prevFrame:
            return self.prevFrame.__redDotsSearchArea1()
        #return Box(Point(600, 300), Point(1400, 700))
        else:
            return Box(Point(600, 300), Point(900, 600))

    def __redDotsSearchArea2(self):
        print "in __redDotsSearchArea2"
        if self.redDot2.dotWasDetected():
            return self.__updateRedDotsSearchArea(self.redDot2.boxAroundDot)
        elif self.prevFrame:
            return self.prevFrame.__redDotsSearchArea2()
        #return Box(Point(600, 300), Point(1400, 700))
        else:
            return Box(Point(900, 300), Point(1400, 800))


    def __updateRedDotsSearchArea(self, boxAroundRedDots):
        print "__updateRedDotsSearchArea.boxAroundRedDots"
        print boxAroundRedDots
        dotsShift = int(self.distanceBetweenRedPoints()/2)
        print "dotsShift"
        print dotsShift
        topLeftX = max(boxAroundRedDots.topLeft.x - dotsShift, 1)
        topLeftY = max(boxAroundRedDots.topLeft.y - dotsShift, 1)
        bottomRightX = min(boxAroundRedDots.bottomRight.x + dotsShift, self.image.shape[1])
        bottomRightY = min(boxAroundRedDots.bottomRight.y + dotsShift, self.image.shape[0])
        redDotsSearchArea = Box(Point(topLeftX, topLeftY), Point(bottomRightX, bottomRightY))

        return redDotsSearchArea


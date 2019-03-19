import cv2
import numpy as np
from skimage.draw import polygon_perimeter

from Image import Image
from RedDot import RedDot
from common import Point, Box


class RedDotsDetector:
    __initialDistanceForRedBoxSearchArea = 200

    def __init__(self, frame, prevFrame=None):
        # type: (Frame, RedDotsDetector) -> RedDotsDetector
        self.__frame = frame
        self.__prevFrame = prevFrame
        self.__redDot1 = None
        self.__redDot2 = None

    def drawBoxesAroundRedDots(self):
        #img = self.__getImage()
        self.__getImage().drawBoxOnImage(self.__redDot1.boxAroundDot)
        self.__getImage().drawBoxOnImage(self.__redDot2.boxAroundDot)
        #return img

    def isolateRedDots(self):
        self.__redDot1 = RedDot(self.__frame.getImgObj(), self.__redDotsSearchArea1())
        #self.__redDot1.isolateRedDots()
        self.__redDot2 = RedDot(self.__frame.getImgObj(), self.__redDotsSearchArea2())
        #self.__redDot2.isolateRedDots()


    def __getImage(self):
        return self.__frame.getImgObj()

    def __distanceBetweenRedPoints(self):
        if self.__redDot1.dotWasDetected() and self.__redDot2.dotWasDetected():
            return int(self.__redDot1.boxAroundDot.distanceTo(self.__redDot2.boxAroundDot))

        if self.__prevFrame:
            return int(self.__prevFrame.__distanceBetweenRedPoints())

        return int(self.__initialDistanceForRedBoxSearchArea)


    def __redDotsSearchArea1(self):
        if self.__redDot1 and self.__redDot1.dotWasDetected():
            return self.__updateRedDotsSearchArea(self.__redDot1.boxAroundDot)

        if self.__prevFrame:
            return self.__prevFrame.__redDotsSearchArea1()

        return Box(Point(600, 300), Point(900, 600))

    def __redDotsSearchArea2(self):
        if self.__redDot2 and self.__redDot2.dotWasDetected():
            return self.__updateRedDotsSearchArea(self.__redDot2.boxAroundDot)
        if self.__prevFrame:
            return self.__prevFrame.__redDotsSearchArea2()

        return Box(Point(900, 300), Point(1400, 800))

    def __updateRedDotsSearchArea(self, boxAroundRedDots):
        dotsShift = int(self.__distanceBetweenRedPoints() / 2)

        bottomRightLimit_x = self.__getImage().width() - 200
        bottomRightLimit_y = self.__getImage().height() - 200

        topLeftX = min(max(boxAroundRedDots.topLeft.x - dotsShift, 1), bottomRightLimit_x-100)
        topLeftY = min(max(boxAroundRedDots.topLeft.y - dotsShift, 1), bottomRightLimit_y-100)
        bottomRightX = min(boxAroundRedDots.bottomRight.x + dotsShift, bottomRightLimit_x)
        bottomRightY = min(boxAroundRedDots.bottomRight.y + dotsShift, bottomRightLimit_y)

        redDotsSearchArea = Box(Point(topLeftX, topLeftY), Point(bottomRightX, bottomRightY))
        return redDotsSearchArea

    def infoAboutFrame(self):
        row = []

        row.append(self.__distanceBetweenRedPoints())
        row.append(self.__redDot1.dotWasDetected())
        row.append(self.__redDot2.dotWasDetected())
        if self.__redDot1.dotWasDetected():
            row.append(self.__redDot1.boxAroundDot.topLeft.x)
            row.append(self.__redDot1.boxAroundDot.topLeft.y)
            row.append(self.__redDot1.boxAroundDot.bottomRight.x)
            row.append(self.__redDot1.boxAroundDot.bottomRight.y)
            row.append(self.__redDot1.boxAroundDot.diagonal())
        else:
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
        if self.__redDot2.dotWasDetected():
            row.append(self.__redDot2.boxAroundDot.topLeft.x)
            row.append(self.__redDot2.boxAroundDot.topLeft.y)
            row.append(self.__redDot2.boxAroundDot.bottomRight.x)
            row.append(self.__redDot2.boxAroundDot.bottomRight.y)
            row.append(self.__redDot2.boxAroundDot.diagonal())
        else:
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
        row.append(self.__getSearchAreaAsString())

        return row


    def __getSearchAreaAsString(self):
        redBox1 = self.__redDotsSearchArea1()
        redBox2 = self.__redDotsSearchArea2()
        return str(redBox1)+"_"+str(redBox2)

    @staticmethod
    def infoHeaders():
        row = []
        row.append("distance")
        row.append("redDot1Detected")
        row.append("redDot2Detected")
        row.append("redDot1_topLeft_x")
        row.append("redDot1_topLeft_y")
        row.append("redDot1_bootomRight_x")
        row.append("redDot1_bootomRight_y")
        row.append("redDot1_box_diagonal")
        row.append("redDot2_topLeft_x")
        row.append("redDot2_topLeft_y")
        row.append("redDot2_bootomRight_x")
        row.append("redDot2_bootomRight_y")
        row.append("redDot2_box_diagonal")
        row.append("searchArea")
        return row

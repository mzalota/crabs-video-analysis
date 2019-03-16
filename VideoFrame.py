import cv2
import numpy as np
from skimage.draw import polygon_perimeter

from RedDot import RedDot
from common import Point, Box


class VideoFrame:
    __initialDistanceForRedBoxSearchArea=200
    redDot1 = None
    redDot2 = None

    def __init__(self, frame, prevFrame=None):
        # type: (Frame, VideoFrame) -> VideoFrame
        self.__frame = frame
        self.prevFrame = prevFrame

    def __getImage(self):
        return self.__frame.getImage()

    def distanceBetweenRedPoints(self):
        if self.redDot1.dotWasDetected() and self.redDot2.dotWasDetected():
            return int(self.redDot1.boxAroundDot.topLeft.distanceTo(self.redDot2.boxAroundDot.topLeft))
        else:
            if self.prevFrame:
                return int(self.prevFrame.distanceBetweenRedPoints())
            else:
                return int(self.__initialDistanceForRedBoxSearchArea)

    def isolateRedDots(self):
        self.redDot1 = RedDot(self.__frame, self.__redDotsSearchArea1())
        self.redDot1.isolateRedDots()

        self.redDot2 = RedDot(self.__frame, self.__redDotsSearchArea2())
        self.redDot2.isolateRedDots()


    def drawBoxesAroundRedDots(self):
        #https://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html#gsc.tab=0

        image_with_boxes = np.copy(self.__getImage())

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


    def searchArea(self):
        redBox1 = self.__redDotsSearchArea1()
        redBox2 = self.__redDotsSearchArea2()

        return str(redBox1)+"_"+str(redBox2)

    def __redDotsSearchArea1(self):
        #print "in __redDotsSearchArea1"
        if self.redDot1 and self.redDot1.dotWasDetected():
            return self.__updateRedDotsSearchArea(self.redDot1.boxAroundDot)
        elif self.prevFrame:
            return self.prevFrame.__redDotsSearchArea1()
        else:
            return Box(Point(600, 300), Point(900, 600))

    def __redDotsSearchArea2(self):
        if self.redDot2 and self.redDot2.dotWasDetected():
            return self.__updateRedDotsSearchArea(self.redDot2.boxAroundDot)
        elif self.prevFrame:
            return self.prevFrame.__redDotsSearchArea2()
        else:
            return Box(Point(900, 300), Point(1400, 800))


    def __updateRedDotsSearchArea(self, boxAroundRedDots):
        #print "__updateRedDotsSearchArea.boxAroundRedDots"
        #print boxAroundRedDots
        dotsShift = int(self.distanceBetweenRedPoints()/2)
        #print "dotsShift"
        #print dotsShift

        bottomRightLimit_x = self.__getImage().shape[1]-200
        bottomRightLimit_y = self.__getImage().shape[0] - 200

        topLeftX = min(max(boxAroundRedDots.topLeft.x - dotsShift, 1), bottomRightLimit_x-100)
        topLeftY = min(max(boxAroundRedDots.topLeft.y - dotsShift, 1), bottomRightLimit_y-100)
        bottomRightX = min(boxAroundRedDots.bottomRight.x + dotsShift, bottomRightLimit_x)
        bottomRightY = min(boxAroundRedDots.bottomRight.y + dotsShift, bottomRightLimit_y)
        redDotsSearchArea = Box(Point(topLeftX, topLeftY), Point(bottomRightX, bottomRightY))

        return redDotsSearchArea


    def infoAboutFrame(self):
        row = []

        row.append(self.distanceBetweenRedPoints())
        row.append(self.redDot1.dotWasDetected())
        row.append(self.redDot2.dotWasDetected())
        if self.redDot1.dotWasDetected():
            row.append(self.redDot1.boxAroundDot.topLeft.x)
            row.append(self.redDot1.boxAroundDot.topLeft.y)
            row.append(self.redDot1.boxAroundDot.bottomRight.x)
            row.append(self.redDot1.boxAroundDot.bottomRight.y)
            row.append(self.redDot1.boxAroundDot.diagonal())
        else:
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
        if self.redDot2.dotWasDetected():
            row.append(self.redDot2.boxAroundDot.topLeft.x)
            row.append(self.redDot2.boxAroundDot.topLeft.y)
            row.append(self.redDot2.boxAroundDot.bottomRight.x)
            row.append(self.redDot2.boxAroundDot.bottomRight.y)
            row.append(self.redDot2.boxAroundDot.diagonal())
        else:
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
        row.append(self.searchArea())

        return row

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

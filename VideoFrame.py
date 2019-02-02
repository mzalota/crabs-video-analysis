import cv2
import numpy as np
from skimage.draw import polygon_perimeter

from RedDot import RedDot
from common import Point, Box, boxAroundBoxes, translateCoordinateToOuter


#from wip01 import boxAroundBoxes, dotsShift, showWindow, Point


class VideoFrame:
    # initializing the variables
    dotsShift = 150
    boxAroundRedDotsAbsolute = None
    redDot1 = None
    redDot2 = None


    # defining constructor
    def __init__(self, image, prevFrame=None):
        self.image = image
        self.prevFrame = prevFrame


    def isolateRedDots(self):
        self.redDot1 = RedDot(True)
        self.redDot1.isolateRedDots(self.image, self.__redDotsSearchArea1())

        self.redDot2 = RedDot(True)
        self.redDot2.isolateRedDots(self.image, self.__redDotsSearchArea2())


    def drawBoxesAroundRedDots(self):
        #https://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html#gsc.tab=0

        image_with_boxes = np.copy(self.image)

        bounding_boxes = [self.redDot1.boxAroundDot, self.redDot2.boxAroundDot]
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


    def __redDotsSearchImage(self):
        """
        :return: numpy.ndarray 
        """
        redDotsSearchArea = self.__redDotsSearchArea1()

        return self.image[redDotsSearchArea.topLeft.y:redDotsSearchArea.bottomRight.y,
                               redDotsSearchArea.topLeft.x: redDotsSearchArea.bottomRight.x]

    def __redDotsSearchArea1(self):
        if self.boxAroundRedDotsAbsolute:
            return self.__updateRedDotsSearchArea(self.redDot1.boxAroundDot)
        if self.prevFrame:
            return self.__updateRedDotsSearchArea(self.prevFrame.redDot1.boxAroundDot)
        #return Box(Point(600, 300), Point(1400, 700))

        return Box(Point(600, 300), Point(900, 600))

    def __redDotsSearchArea2(self):
        if self.boxAroundRedDotsAbsolute:
            return self.__updateRedDotsSearchArea(self.redDot2.boxAroundDot)
        if self.prevFrame:
            return self.__updateRedDotsSearchArea(self.prevFrame.redDot2.boxAroundDot)
        #return Box(Point(600, 300), Point(1400, 700))

        return Box(Point(900, 300), Point(1400, 800))

    def __updateRedDotsSearchArea(self, boxAroundRedDots):
        topLeftX = max(boxAroundRedDots.topLeft.x - self.dotsShift, 1)
        topLeftY = max(boxAroundRedDots.topLeft.y - self.dotsShift, 1)
        bottomRightX = min(boxAroundRedDots.bottomRight.x + self.dotsShift, self.image.shape[1])
        bottomRightY = min(boxAroundRedDots.bottomRight.y + self.dotsShift, self.image.shape[0])
        redDotsSearchArea = Box(Point(topLeftX, topLeftY), Point(bottomRightX, bottomRightY))

        return redDotsSearchArea


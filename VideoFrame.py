import numpy as np
from skimage.draw import polygon_perimeter

from FeatureMatcher import isolateRedDots
from common import Point, Box, boxAroundBoxes


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


    def updateRedDotsSearchArea(self,boxAroundRedDots):
        # print max(boxAroundDots.topLeft.x + boxAroundBoxesInner.topLeft.x - dotsShift,1)
        topLeftX = max(boxAroundRedDots.topLeft.x - self.dotsShift, 1)
        topLeftY = max(boxAroundRedDots.topLeft.y - self.dotsShift, 1)
        bottomRightX = min(boxAroundRedDots.bottomRight.x + self.dotsShift, self.image.shape[1])
        bottomRightY = min(boxAroundRedDots.bottomRight.y + self.dotsShift, self.image.shape[0])
        redDotsSearchArea = Box(Point(topLeftX, topLeftY), Point(bottomRightX, bottomRightY))

        return redDotsSearchArea


    def boxAroundRedDotsAbsoluteFunc(self,boxAroundBoxesInner):
        topLeftAbsolute = self.__redDotsSearchArea().topLeft

        self.boxAroundRedDotsAbsolute = self.__innerCoordinateToOuter(boxAroundBoxesInner, topLeftAbsolute)


    def __innerCoordinateToOuter(self, innerBox, topLeftOuterPoint):

        """

        :param innerBox: Box
        :param topLeftOuterPoint: Point 
        :return: Box
        """
        topLeftX = max(topLeftOuterPoint.x + innerBox.topLeft.x, 1)
        topLeftY = max(topLeftOuterPoint.y + innerBox.topLeft.y, 1)
        bottomRightX = min(topLeftOuterPoint.x + innerBox.bottomRight.x, self.image.shape[1])
        bottomRightY = min(topLeftOuterPoint.y + innerBox.bottomRight.y, self.image.shape[0])
        #return bottomRightX, bottomRightY, topLeftX, topLeftY

        return Box(Point(topLeftX, topLeftY), Point(bottomRightX, bottomRightY))


    def redDotsSearchImage(self):
        """

        :return: numpy.ndarray 
        """
        redDotsSearchArea = self.__redDotsSearchArea()

        return self.image[redDotsSearchArea.topLeft.y:redDotsSearchArea.bottomRight.y,
                               redDotsSearchArea.topLeft.x: redDotsSearchArea.bottomRight.x]

    def __redDotsSearchArea(self):
        if self.boxAroundRedDotsAbsolute:
            return self.updateRedDotsSearchArea(self.boxAroundRedDotsAbsolute)
        if self.prevFrame:
            return self.updateRedDotsSearchArea(self.prevFrame.boxAroundRedDotsAbsolute)
        return Box(Point(600, 300), Point(1400, 700))


    def isolateRedDots(self):

        redDotsSearchBox = self.__redDotsSearchArea()

        redDotsImageFragment= self.redDotsSearchImage() #self.image[redDotsSearchBox.topLeft.y:redDotsSearchBox.bottomRight.y,
                               #redDotsSearchBox.topLeft.x: redDotsSearchBox.bottomRight.x]
        #redDotsImageFragment = self.redDotsSearchImage()
        # print "shape of redDotsArea"
        # print redDotsArea.shape


        dots = isolateRedDots(redDotsImageFragment)
        self.redDot1 = self.__innerCoordinateToOuter(dots[0],redDotsSearchBox.topLeft)
        self.redDot2 = self.__innerCoordinateToOuter(dots[1],redDotsSearchBox.topLeft)

        self.boxAroundBoxesInner = boxAroundBoxes(dots[0], dots[1])

        print "dddddd"
        self.boxAroundRedDotsAbsoluteFunc(self.boxAroundBoxesInner)

        #print "self.boxAroundRedDotsAbsolute"
        #print self.boxAroundRedDotsAbsolute

        #withRedDots = drawContoursAroundRedDots(redDotsImageFragment)
        #withRedDots = drawBoxesAroundRedDots(self.image, [self.redDot1,self.redDot2])
        #return withRedDots


    def processFrameOlllldddd(self):

        # resize(image, dst, Size(), 0.5, 0.5, interpolation);
        # print Box(Point(topLeftX,topLeftY), Point(bottomRightX,bottomRightY))
        # highlightMatchedFeature(image, featureImage)



        '''

        redDotsImageFragment = self.redDotsSearchImage()
        # print "shape of redDotsArea"
        # print redDotsArea.shape
        dots = isolateRedDots(redDotsImageFragment)
        self.redDot1 = dots[0]
        self.redDot1 = dots[1]

        # showWindow("redDotsArea", redDotsArea, Point(400, 400))
        # cv2.waitKey(0)

        self.boxAroundBoxesInner = boxAroundBoxes(dots[0], dots[1])

        #print "boxAroundBoxesInner"
        #print self.boxAroundBoxesInner
        #print "image.shapte"
        #print self.image.shape
        #print "shape x width"
        #print self.image.shape[1]

        print "dddddd"
        self.boxAroundRedDotsAbsolute = self.boxAroundRedDotsAbsolute(redDotsSearchArea.topLeft, self.boxAroundBoxesInner)
        print "self.boxAroundRedDotsAbsolute"
        print self.boxAroundRedDotsAbsolute
        

        withRedDots = drawContoursAroundRedDots(redDotsImageFragment)
        '''
        return self.isolateRedDots()


    def drawBoxesAroundRedDots(self, image_without_boxes, bounding_boxes):
        #https://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html#gsc.tab=0

        with_boxes = np.copy(image_without_boxes)

        for box in bounding_boxes:
            #print box
            c = [box.topLeft.x, box.bottomRight.x, box.bottomRight.x, box.topLeft.x, box.topLeft.x]
            r = [box.bottomRight.y, box.bottomRight.y, box.topLeft.y, box.topLeft.y, box.bottomRight.y]
            rr, cc = polygon_perimeter(r, c, with_boxes.shape)
            with_boxes[rr, cc] = 1  # set color white
        return with_boxes
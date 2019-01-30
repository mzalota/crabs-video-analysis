from FeatureMatcher import isolateRedDots, drawContoursAroundRedDots

from common import Point, Box, boxAroundBoxes


#from wip01 import boxAroundBoxes, dotsShift, showWindow, Point


class VideoFrame:
    # initializing the variables
    #topLeftX = 600
    #topLeftY = 300
    #bottomRightX = 1400
    #bottomRightY = 700

    dotsShift = 150

    # defining constructor
    def __init__(self, image, prevFrame=None):
        self.image = image
        self.prevFrame = prevFrame


    def updateRedDotsSearchArea(self,prevFrame):
        # print max(boxAroundDots.topLeft.x + boxAroundBoxesInner.topLeft.x - dotsShift,1)
        topLeftX = max(prevFrame.boxAroundRedDotsAbsolute.topLeft.x - self.dotsShift, 1)
        topLeftY = max(prevFrame.boxAroundRedDotsAbsolute.topLeft.y - self.dotsShift, 1)
        bottomRightX = min(prevFrame.boxAroundRedDotsAbsolute.bottomRight.x + self.dotsShift,self.image.shape[1])
        bottomRightY = min(prevFrame.boxAroundRedDotsAbsolute.bottomRight.y + self.dotsShift,self.image.shape[0])
        redDotsSearchArea = Box(Point(topLeftX, topLeftY), Point(bottomRightX, bottomRightY))

        return redDotsSearchArea


    def boxAroundRedDotsAbsolute(self,topLeftAbsolute, boxAroundBoxesInner):
        # print max(boxAroundDots.topLeft.x + boxAroundBoxesInner.topLeft.x - dotsShift,1)
        topLeftX = max(topLeftAbsolute.x + boxAroundBoxesInner.topLeft.x, 1)
        topLeftY = max(topLeftAbsolute.y + boxAroundBoxesInner.topLeft.y, 1)
        bottomRightX = min(topLeftAbsolute.x + boxAroundBoxesInner.bottomRight.x, self.image.shape[1])
        bottomRightY = min(topLeftAbsolute.y + boxAroundBoxesInner.bottomRight.y, self.image.shape[0])

        redDotsSearchArea = Box(Point(topLeftX, topLeftY), Point(bottomRightX, bottomRightY))

        return redDotsSearchArea

    def processFrame(self):

        # resize(image, dst, Size(), 0.5, 0.5, interpolation);
        # print Box(Point(topLeftX,topLeftY), Point(bottomRightX,bottomRightY))
        # highlightMatchedFeature(image, featureImage)

        if self.prevFrame:
            redDotsSearchArea = self.updateRedDotsSearchArea(self.prevFrame)
        else:
            #redDotsSearchArea = self.redDotsSearchArea
            redDotsSearchArea = Box(Point(600, 300), Point(1400, 700))

        redDotsImageFragment = self.image[redDotsSearchArea.topLeft.y:redDotsSearchArea.bottomRight.y, redDotsSearchArea.topLeft.x: redDotsSearchArea.bottomRight.x]
        # print "shape of redDotsArea"
        # print redDotsArea.shape
        dots = isolateRedDots(redDotsImageFragment)
        # showWindow("redDotsArea", redDotsArea, Point(400, 400))
        # cv2.waitKey(0)
        self.boxAroundBoxesInner = boxAroundBoxes(dots[0], dots[1])

        print "boxAroundBoxesInner"
        print self.boxAroundBoxesInner
        print "image.shapte"
        print self.image.shape
        print "shape x width"
        print self.image.shape[1]

        print "dddddd"
        self.boxAroundRedDotsAbsolute = self.boxAroundRedDotsAbsolute(redDotsSearchArea.topLeft, self.boxAroundBoxesInner)
        print "self.boxAroundRedDotsAbsolute"
        print self.boxAroundRedDotsAbsolute


        withRedDots = drawContoursAroundRedDots(redDotsImageFragment)
        return withRedDots


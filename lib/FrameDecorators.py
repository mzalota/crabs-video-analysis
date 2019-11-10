from lib.CrabsData import CrabsData
from lib.Feature import Feature
from lib.Frame import Frame
from lib.FramesStitcher import FramesStitcher
from lib.MyTimer import MyTimer
from lib.SeeFloor import SeeFloor
from lib.common import Point, Vector

class FrameDecorator:

    def __init__(self, frameDeco):
        # type: (FrameDecorator) -> FrameDecorator
        self.frameDeco = frameDeco

    def getFrameID(self):
        return self.frameDeco.getFrameID()

    #def getImgObj(self):
    #    # type: () -> Image
    #    return self.frameDeco.getImgObj()

class DecoGridLines(FrameDecorator):

    def __init__(self, frameDeco, redDotsData, startPoint):
        FrameDecorator.__init__(self, frameDeco)
        self.__redDotsData = redDotsData
        self.__startPoint = startPoint

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()
        frame_id = self.frameDeco.getFrameID()

        distancePix = int(self.__redDotsData.getDistancePixels(frame_id))

        #draw 8 grid squares along X and Y axis.
        for i in range(-4, 4):
            #draw 9 X-lines. One through midpoint between red dots (i=0) and then 4 north-west and 4 south-east
            point = self.__startPoint.translateBy(Vector(i*distancePix, i*distancePix))
            self.__drawGridX(imgObj, point, 0)
        return imgObj

    def __drawGridX(self, imgObj, startingPoint, distancePix):
        verticalTop = Point(startingPoint.x + distancePix, 0)
        verticalBottom = Point(startingPoint.x + distancePix, imgObj.height())
        horisontalLeft = Point(0, startingPoint.y + distancePix)
        horisontalRight = Point(imgObj.width(), startingPoint.y + distancePix)

        imgObj.drawLine(verticalTop, verticalBottom, thickness=3, color=(255, 255, 0))
        imgObj.drawLine(horisontalLeft, horisontalRight, thickness=3, color=(255, 255, 0))


class DecoMarkedCrabs(FrameDecorator):

    def __init__(self, frameDeco, seefloorGeometry):
        # type: (FrameDecorator, SeeFloor) -> DecoMarkedCrabs
        FrameDecorator.__init__(self, frameDeco)
        self.__seefloorGeometry = seefloorGeometry

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()
        self.__markCrabsOnImage(imgObj, self.getFrameID())
        return imgObj

    def __markCrabsOnImage(self, mainImage, frame_id):
        markedCrabs = self.__seefloorGeometry.crabsOnFrame(frame_id)

        for markedCrab in markedCrabs:
            #print ('markedCrab', markedCrab)
            #timer = MyTimer("crabsOnFrame")

            frame_number = markedCrab['frameNumber']

            crabLocation = Point(markedCrab['crabLocationX'], markedCrab['crabLocationY'])

            crabFeature = Feature(self.__seefloorGeometry.getDriftData(), frame_number, crabLocation, 5)
            #timer.lap("Step 150")
            crabLocation = crabFeature.getCoordinateInFrame(frame_id)

            #print ('crabLocation', str(crabLocation))

            mainImage.drawCross(crabLocation)

            #timer.lap("crab: "+str(frame_number))


class DecoRedDots(FrameDecorator):
    def __init__(self, frameDeco, redDotsData):
        # type: (FrameDecorator, RedDotsData) -> object
        FrameDecorator.__init__(self, frameDeco)
        self.__redDotsData = redDotsData

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()

        redDot1 = self.__redDotsData.getRedDot1(self.getFrameID())
        imgObj.drawCross(redDot1,5, color=(0, 0, 255))

        redDot2 = self.__redDotsData.getRedDot2(self.getFrameID())
        imgObj.drawCross(redDot2,5, color=(0, 0, 255))

        return imgObj


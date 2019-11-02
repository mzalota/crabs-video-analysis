from lib.CrabsData import CrabsData
from lib.Feature import Feature
from lib.Frame import Frame
from lib.FramesStitcher import FramesStitcher
from lib.MyTimer import MyTimer
from lib.common import Point, Vector


class DecoGridLines(Frame):

    def __init__(self, frameNumber, videoStream, redDotsData, startPoint):
        Frame.__init__(self, frameNumber, videoStream)
        self.__redDotsData = redDotsData
        self.__startPoint = startPoint

    def getImgObj(self):
        # type: () -> Image
        imgObj = Frame.getImgObj(self)
        frame_id = self.getFrameID()

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


class DecoMarkedCrabs(Frame):

    def __init__(self, frameNumber, videoStream, driftData, crabsData):
        Frame.__init__(self, frameNumber, videoStream)
        self.__driftData = driftData
        self.__crabsData = crabsData

    def getImgObj(self):
        # type: () -> Image
        imgObj = Frame.getImgObj(self)
        self.__markCrabsOnImage(imgObj, self.getFrameID())
        return imgObj

    def __markCrabsOnImage(self, mainImage, frame_id):
        nextFrame = self.__driftData.getNextFrame(FramesStitcher.FRAME_HEIGHT,frame_id)
        prevFrame = self.__driftData.getNextFrame(-FramesStitcher.FRAME_HEIGHT,frame_id)

        #print("in markCrabsOnImage", frame_id,nextFrame, prevFrame)

        markedCrabs = self.__crabsData.crabsBetweenFrames(prevFrame,nextFrame)

        for markedCrab in markedCrabs:
            #print ('markedCrab', markedCrab)
            #timer = MyTimer("crabsOnFrame")

            frame_number = markedCrab['frameNumber']

            crabLocation = Point(markedCrab['crabLocationX'], markedCrab['crabLocationY'])

            crabFeature = Feature(self.__driftData, frame_number, crabLocation, 5)
            #timer.lap("Step 150")
            crabLocation = crabFeature.getCoordinateInFrame(frame_id)

            #print ('crabLocation', str(crabLocation))

            mainImage.drawCross(crabLocation)

            #timer.lap("crab: "+str(frame_number))
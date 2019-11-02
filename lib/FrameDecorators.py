from lib.CrabsData import CrabsData
from lib.Feature import Feature
from lib.Frame import Frame
from lib.FramesStitcher import FramesStitcher
from lib.MyTimer import MyTimer
from lib.common import Point


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
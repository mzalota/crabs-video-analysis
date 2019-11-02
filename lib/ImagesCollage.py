from pandas.compat.numpy import np

from lib.Frame import Frame
from lib.FrameDecorators import DecoMarkedCrabs
from lib.Image import Image


class ImagesCollage:
    def __init__(self, videoStream, seeFloorGeometry, crabsData):
        self.__videoStream = videoStream
        self.__seeFloorGeometry = seeFloorGeometry
        self.__crabsData = crabsData

    def attachNeighbourFrames(self, thisFrame, neighboursHeight):
        # type: (Frame, Int) -> np

        prevFrame = self.__getPrevFrame(thisFrame)
        nextFrame = self.__getNextFrame(thisFrame)

        image = thisFrame.getImgObj()
        image.drawFrameID(thisFrame.getFrameID())
        prevSubImage = self.__buildPrevImagePart(prevFrame, neighboursHeight)
        nextSubImage = self.__buildNextImagePart(nextFrame, neighboursHeight)

        mainCollage = self.__glueTogether(image, nextSubImage, prevSubImage)

        collageHeight = thisFrame.getImgObj().height() + neighboursHeight * 2

        rightCollage = self.constructRightCollage(thisFrame, nextFrame, prevFrame, collageHeight)
        filler = Image.empty(collageHeight, 100, 0).asNumpyArray()

        withImageOnTheRight = np.concatenate((mainCollage, filler, rightCollage), axis=1)
        return withImageOnTheRight

    def __getNextFrame(self, thisFrame):
        nextFrameID = self.__seeFloorGeometry.jumpToSeefloorSlice(thisFrame.getFrameID(), +1)
        nextFrame = self.__constructFrame(nextFrameID)
        return nextFrame

    def __getPrevFrame(self, thisFrame):
        prevFrameID = self.__seeFloorGeometry.jumpToSeefloorSlice(thisFrame.getFrameID(), -1)
        prevFrame = self.__constructFrame(prevFrameID)
        return prevFrame

    def __constructFrame(self, newFrameID):
        driftData = self.__seeFloorGeometry.getDriftData()
        frame = DecoMarkedCrabs(newFrameID, self.__videoStream, driftData, self.__crabsData)
        return frame

    def constructRightCollage(self, thisFrame, nextFrame, prevFrame, mainCollageHeight):
        # type: (Frame, Frame, int) -> np
        beforeMiddleImage = self.__constructRightPrev(thisFrame, prevFrame)
        afterMiddleImage = self.__constructRightNext(thisFrame, nextFrame)

        rightCollageHeight = beforeMiddleImage.height() + afterMiddleImage.height()
        fillerHeight = (mainCollageHeight - rightCollageHeight) / 2
        fillerImage = Image.empty(fillerHeight, thisFrame.getImgObj().width(), 0).asNumpyArray()

        return np.concatenate((fillerImage, afterMiddleImage.asNumpyArray(), beforeMiddleImage.asNumpyArray(), fillerImage))

    def __constructRightNext(self, thisFrame, nextFrame):
        # type: (Frame) -> Image
        nextFrameID = int(nextFrame.getFrameID())
        afterMiddleFrameID = int(thisFrame.getFrameID()) + int((nextFrameID - int(thisFrame.getFrameID())) / 2)
        afterMiddleFrame = self.__constructFrame(afterMiddleFrameID)
        afterMiddleImage = afterMiddleFrame.getImgObj()
        afterMiddleImage.drawFrameID(str(afterMiddleFrameID))
        return afterMiddleImage

    def __constructRightPrev(self, thisFrame, prevFrame):
        prevFrameID = int(prevFrame.getFrameID())
        beforeMiddleFrameID = prevFrameID + int((int(thisFrame.getFrameID()) - prevFrameID) / 2)
        beforeMiddleFrame = self.__constructFrame(beforeMiddleFrameID)

        beforeMiddleImage = beforeMiddleFrame.getImgObj()
        beforeMiddleImage.drawFrameID(str(beforeMiddleFrameID))
        return beforeMiddleImage

    def __buildPrevImagePart(self, prevFrame, height):
        # boxLine = Box(Point(0, prevImage.height() - 3), Point(prevImage.width(), prevImage.height()))
        # prevImage.drawBoxOnImage(boxLine)
        prevSubImage = prevFrame.getImgObj().topPart(height)
        prevSubImage.drawFrameID(prevFrame.getFrameID())

        return prevSubImage

    def __buildNextImagePart(self, nextFrame, height):
        nextSubImage = nextFrame.getImgObj().bottomPart(height)
        nextSubImage.drawFrameID(nextFrame.getFrameID())

        return nextSubImage

    def __glueTogether(self, image, nextSubImage, prevSubImage):
        # type: (Image, Image, Image) -> object
        res = np.concatenate((nextSubImage.asNumpyArray(), image.asNumpyArray()))
        res2 = np.concatenate((res, prevSubImage.asNumpyArray()))
        return res2


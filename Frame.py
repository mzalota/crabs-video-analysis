from Image import Image
from pandas.compat.numpy import np

from common import Point, Box


class Frame:
    #__frameID = None
    #__image = None

    def __init__(self, frameNumber, videoStream):
        # type: (int, VideoStream) -> Frame
        self.__frameID = frameNumber
        self.__videoStream = videoStream


    def getFrameID(self):
        return self.__frameID

    def getImage(self):
        return self.__videoStream.readImage(self.__frameID)

    def getImgObj(self):
        # type: () -> Image
        return Image(self.__videoStream.readImage(self.__frameID))

    def saveImageToFile(self, rootDirectory):
        imageFilePath = self.__constructFilePath(rootDirectory)
        #print("image path is: " + imageFilePath)
        self.getImgObj().writeToFile(imageFilePath)

    def __constructFilePath(self, rootDirectory):
        frameNumberString = str(self.__frameID).zfill(6)
        imageFileName = "frame" + frameNumberString + ".jpg"
        imageFilePath = rootDirectory + "/seqFrames/" + imageFileName
        return imageFilePath

    def attachNeighbourFrames(self, nextFrame, prevFrame, neighboursHeight):
        image = self.getImgObj()
        image.drawFrameID(self.getFrameID())
        prevSubImage = self.__buildPrevImagePart(prevFrame, neighboursHeight)
        nextSubImage = self.__buildNextImagePart(nextFrame, neighboursHeight)
        return self.__glueTogether(image, nextSubImage, prevSubImage)

    def __glueTogether(self, image, nextSubImage, prevSubImage):
        res = np.concatenate((nextSubImage.asNumpyArray(), image.asNumpyArray()))
        res2 = np.concatenate((res, prevSubImage.asNumpyArray()))
        return res2

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
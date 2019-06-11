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
        imageFilePath = self.constructFilePath(rootDirectory)
        print("image path is: " + imageFilePath)
        self.getImgObj().writeToFile(imageFilePath)

    def constructFilePath(self, rootDirectory):
        frameNumberString = str(self.__frameID).zfill(6)
        imageFileName = "frame" + frameNumberString + ".jpg"
        imageFilePath = rootDirectory + "/seqFrames/" + imageFileName
        return imageFilePath

    def attachNeighbourFrames(self, nextFrame, prevFrame, neighboursHeight):
        image = self.getImgObj()
        image.drawFrameID(self.getFrameID())
        prevSubImage = self.__buildPrevImagePart(prevFrame, neighboursHeight)
        nextSubImage = self.__buildNextImagePart(nextFrame, neighboursHeight)

        mainCollage = self.__glueTogether(image, nextSubImage, prevSubImage)

        #collageHeight = self.getImgObj().height() + neighboursHeight * 2

        #rightCollage = self.constructRightCollage(collageHeight, nextFrame, prevFrame)
        #filler = Image.empty(collageHeight, 100, 0).asNumpyArray()

        #withImageOnTheRight = np.concatenate((mainCollage, filler, rightCollage), axis=1)
        #return withImageOnTheRight
        return image.asNumpyArray()

    def constructRightCollage(self, mainCollageHeight, nextFrame, prevFrame):
        beforeMiddleImage = self.constructRightPrev(prevFrame)
        afterMiddleImage = self.__constructRightNext(nextFrame)

        rightCollageHeight = beforeMiddleImage.height() + afterMiddleImage.height()
        fillerHeight = (mainCollageHeight - rightCollageHeight) / 2
        fillerImage = Image.empty(fillerHeight, self.getImgObj().width(), 0).asNumpyArray()

        return np.concatenate((fillerImage, afterMiddleImage.asNumpyArray(), beforeMiddleImage.asNumpyArray(), fillerImage))

    def __constructRightNext(self, nextFrame):
        nextFrameID = int(nextFrame.getFrameID())
        afterMiddleFrameID = int(self.getFrameID()) + int((nextFrameID - int(self.getFrameID())) / 2)
        afterMiddleFrame = Frame(afterMiddleFrameID, self.__videoStream)
        afterMiddleImage = afterMiddleFrame.getImgObj()
        afterMiddleImage.drawFrameID(str(afterMiddleFrameID))
        return afterMiddleImage

    def constructRightPrev(self, prevFrame):
        prevFrameID = int(prevFrame.getFrameID())
        beforeMiddleFrameID = prevFrameID + int((int(self.getFrameID()) - prevFrameID) / 2)
        beforeMiddleFrame = Frame(beforeMiddleFrameID, self.__videoStream)
        beforeMiddleImage = beforeMiddleFrame.getImgObj()
        beforeMiddleImage.drawFrameID(str(beforeMiddleFrameID))
        return beforeMiddleImage

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
from pandas.compat.numpy import np
from lib.Image import Image

class Frame:
    #__frameID = None
    #__image = None

    FRAME_HEIGHT = 1080
    FRAME_WIDTH = 1920

    def __init__(self, frameNumber, videoStream):
        # type: (int, VideoStream) -> Frame
        self.__frameID = frameNumber
        self.__videoStream = videoStream

    def getFrameID(self):
        return self.__frameID

    def getVideoStream(self):
        return self.__videoStream

    def getImage(self):
        return self.__videoStream.readImage(self.__frameID)

    def getImgObj(self):
        # type: () -> Image
        return Image(self.__videoStream.readImage(self.__frameID))

    def constructFilename(self):
        frameNumberString = str(self.__frameID).zfill(6)
        imageFileName = "frame" + frameNumberString + ".jpg"
        return imageFileName

    @staticmethod
    def deconstructFilename(filename):
        #returns FrameID that was embeded in the filename
        return int(filename[5:11])

    def attachNeighbourFrames(self, nextFrame, prevFrame, neighboursHeight):
        # type: (Frame, Frame, Int) -> np
        image = self.getImgObj()
        image.drawFrameID(self.getFrameID())
        prevSubImage = self.__buildPrevImagePart(prevFrame, neighboursHeight)
        nextSubImage = self.__buildNextImagePart(nextFrame, neighboursHeight)

        mainCollage = self.__glueTogether(image, nextSubImage, prevSubImage)

        collageHeight = self.getImgObj().height() + neighboursHeight * 2

        rightCollage = self.constructRightCollage(nextFrame, prevFrame, collageHeight)
        filler = Image.empty(collageHeight, 100, 0).asNumpyArray()

        withImageOnTheRight = np.concatenate((mainCollage, filler, rightCollage), axis=1)
        return withImageOnTheRight


    def constructRightCollage(self, nextFrame, prevFrame, mainCollageHeight):
        # type: (Frame, Frame, int) -> np
        beforeMiddleImage = self.constructRightPrev(prevFrame)
        afterMiddleImage = self.__constructRightNext(nextFrame)

        rightCollageHeight = beforeMiddleImage.height() + afterMiddleImage.height()
        fillerHeight = (mainCollageHeight - rightCollageHeight) / 2
        fillerImage = Image.empty(fillerHeight, self.getImgObj().width(), 0).asNumpyArray()

        return np.concatenate((fillerImage, afterMiddleImage.asNumpyArray(), beforeMiddleImage.asNumpyArray(), fillerImage))

    def __constructRightNext(self, nextFrame):
        # type: (Frame) -> Image
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
        # type: (Image, Image, Image) -> object
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
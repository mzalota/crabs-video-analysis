from Image import Image


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
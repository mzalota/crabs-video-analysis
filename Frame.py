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

#from pandas.compat.numpy import np
import numpy as np
from lib.Image import Image

class Frame:
    #__frameID = None
    #__image = None

    # FRAME_HEIGHT = 1080
    # FRAME_WIDTH = 1920

    FRAME_HEIGHT = 2048
    FRAME_WIDTH = 3072

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



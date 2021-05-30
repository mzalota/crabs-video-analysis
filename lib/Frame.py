#from pandas.compat.numpy import np
import numpy as np
from lib.Image import Image

class Frame:
    #__frameID = None
    #__image = None

    __FRAME_HEIGHT_LOW_RES = 1080
    __FRAME_WIDTH_LOW_RES = 1920
    __FRAME_HEIGHT_HIGH_RES = 2048
    __FRAME_WIDTH_HIGH_RES = 3072

    FRAME_HEIGHT = __FRAME_HEIGHT_HIGH_RES
    FRAME_WIDTH = __FRAME_WIDTH_HIGH_RES

    @staticmethod
    def is_high_resolution():
        # type: () -> bool
        if Frame.FRAME_HEIGHT == Frame.__FRAME_HEIGHT_HIGH_RES:
            return True
        return False

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



#from pandas.compat.numpy import np
import numpy as np

from lib.FrameId import FrameId
from lib.Image import Image

class Frame:
    #__frameID = None
    #__image = None

    __FRAME_HEIGHT_LOW_RES = 1080
    __FRAME_WIDTH_LOW_RES = 1920

    _FRAME_HEIGHT_HIGH_RES = 2048
    __FRAME_WIDTH_HIGH_RES = 3072

    FRAME_HEIGHT = _FRAME_HEIGHT_HIGH_RES
    FRAME_WIDTH = __FRAME_WIDTH_HIGH_RES

    def __init__(self, frameNumber, videoStream):
        # type: (int, VideoStream) -> Frame
        self.__frameID = frameNumber
        self.__videoStream = videoStream

    def is_high_resolution(self):
        # type: () -> bool
        # if Frame.FRAME_HEIGHT == Frame.__FRAME_HEIGHT_HIGH_RES:
        if self.__videoStream.frame_height() >= Frame._FRAME_HEIGHT_HIGH_RES:
            return True
        return False

    def frame_height(self):
        # type: () -> int
        return self.__videoStream.frame_height()

    def frame_width(self):
        # type: () -> int
        return self.__videoStream.frame_width()

    def getFrameID(self):
        return self.__frameID

    def getVideoStream(self):
        return self.__videoStream

    def getImage(self):
        return self.__videoStream.read_image(self.__frameID)

    def getImgObj(self):
        # type: () -> Image
        return Image(self.__videoStream.read_image(self.__frameID))

    def constructFilename(self):
        frameNumberString = str(self.__frameID).zfill(6)
        imageFileName = "frame" + frameNumberString + ".jpg"
        return imageFileName

    @staticmethod
    def deconstructFilename(filename):
        #returns FrameID that was embeded in the filename
        return int(filename[5:11])



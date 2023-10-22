#from pandas.compat.numpy import np

from lib.model.Image import Image

class Frame:
    #__frameID = None
    #__image = None

    __FRAME_HEIGHT_LOW_RES = 1080
    __FRAME_WIDTH_LOW_RES = 1920

    _FRAME_HEIGHT_HIGH_RES = 2048
    _FRAME_WIDTH_HIGH_RES = 3072

    def __init__(self, frameNumber, videoStream):
        # type: (int, VideoStream) -> Frame
        self.__frameID = frameNumber
        self.__videoStream = videoStream

    @staticmethod
    def is_high_resolution(frame_height: int) -> bool:
        if frame_height >= Frame._FRAME_HEIGHT_HIGH_RES:
            return True
        return False

    def frame_height(self) -> int:
        return self.__videoStream.frame_height()

    def frame_width(self) -> int:
        return self.__videoStream.frame_width()

    def getFrameID(self) -> int:
        return self.__frameID

    # def getImage(self):
    #     return self.__videoStream.read_image(self.__frameID)

    def getImgObj(self) -> Image:
        return Image(self.__videoStream.read_image(self.__frameID))

    def constructFilename(self):
        frameNumberString = str(self.__frameID).zfill(6)
        imageFileName = "frame" + frameNumberString + ".jpg"
        return imageFileName

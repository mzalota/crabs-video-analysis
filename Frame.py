class Frame:
    __frameID = None
    __image = None

    def __init__(self, frameNumber, image):
        self.__frameID = frameNumber
        self.__image = image

    def getFrameID(self):
        return self.__frameID

    def getImage(self):
        return self.__image
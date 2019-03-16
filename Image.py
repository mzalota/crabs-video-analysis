from cv2 import cv2


class Image:
    def __init__(self, imageAsNumpyArray):
        self.__image = imageAsNumpyArray

    def drawBoxOnImage(self, box):
        cv2.rectangle(self.__image, (box.topLeft.x, box.topLeft.y), (box.bottomRight.x, box.bottomRight.y), (0, 255, 0), 2)

    def asNumpyArray(self):
        return self.__image
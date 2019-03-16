from cv2 import cv2

from common import Point, Box


class Image:
    def __init__(self, imageAsNumpyArray):
        self.__image = imageAsNumpyArray

    def asNumpyArray(self):
        return self.__image

    def drawBoxOnImage(self, box):
        cv2.rectangle(self.__image, (box.topLeft.x, box.topLeft.y), (box.bottomRight.x, box.bottomRight.y), (0, 255, 0), 2)

    def drawTextInBox(self, box, text):
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (box.topLeft.x, box.topLeft.y + 27)
        fontScale = 1
        fontColor = (0, 255, 0)
        lineType = 2
        cv2.putText(self.__image, text,
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)

    def drawDriftVectorOnImage(self, driftVector):
        if driftVector is not None:
            vectorStart = Point(100, 100)
            vectorEnd = vectorStart.translateBy(driftVector)
            vectorBox = Box(vectorStart, vectorEnd)
            self.drawBoxOnImage(vectorBox)

    def subImage(self, box):
        # type: (Box) -> Image
        return Image(self.__image[box.topLeft.y:box.bottomRight.y, box.topLeft.x: box.bottomRight.x])


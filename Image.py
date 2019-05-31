from cv2 import cv2, os

from pandas.compat.numpy import np
from common import Point, Box

class Image:
    def __init__(self, imageAsNumpyArray):
        self.__image = imageAsNumpyArray

    @staticmethod
    def empty(height, width, color):
        image = np.zeros([height, width, 3], dtype=np.uint8)
        image.fill(color)
        return Image(image)

    def width(self):
        return self.__image.shape[1]

    def height(self):
        return self.__image.shape[0]

    def asNumpyArray(self):
        return self.__image

    def drawBoxOnImage(self, box):
        if box:
            cv2.rectangle(self.__image, (box.topLeft.x, box.topLeft.y), (box.bottomRight.x, box.bottomRight.y), (0, 255, 0), 2)

    def drawFrameID(self, frameID):
        self.drawTextInBox(Box(Point(0, 0), Point(80, 50)), frameID)

    def drawTextInBox(self, box, text):
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (box.topLeft.x, box.topLeft.y + 27)
        fontScale = 1
        fontColor = (0, 255, 0)
        lineType = 2
        cv2.putText(self.__image, str(text),
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
        return Image(self.__image[box.topLeft.y:box.bottomRight.y, box.topLeft.x: box.bottomRight.x].copy())

    def bottomPart(self, height):
        # type: (integer) -> Image
        box = Box(Point(0, self.height() - height), Point(self.width(), self.height()))
        return self.subImage(box)

    def topPart(self, height):
        # type: (integer) -> Image
        box = Box(Point(0, 0), Point(self.width(), height))
        return self.subImage(box)


    def findBrightestSpot(self, image):
        # https://www.pyimagesearch.com/2014/09/29/finding-brightest-spot-image-using-python-opencv/
        orig = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        radius_ = 37
        gray = cv2.GaussianBlur(gray, (radius_, radius_), 0)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
        image = orig.copy()
        cv2.circle(image, maxLoc, radius_, (255, 0, 0), 2)
        print "brigtest spot maxLoc"
        print maxLoc
        print maxVal
        imageWin.showWindowAndWaitForClick(image)

    def drawBoxOnImage2(self):
        #https://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html#gsc.tab=0

        image_with_boxes = np.copy(self.__getImage())

        bounding_boxes = []
        #bounding_boxes = [self.redDot1.boxAroundDot, self.redDot2.boxAroundDot]
        if self.redDot1.dotWasDetected():
            bounding_boxes.append(self.redDot1.boxAroundDot)
        if self.redDot2.dotWasDetected():
            bounding_boxes.append(self.redDot2.boxAroundDot)

        for box in bounding_boxes:
            c = [box.topLeft.x, box.bottomRight.x, box.bottomRight.x, box.topLeft.x, box.topLeft.x]
            r = [box.bottomRight.y, box.bottomRight.y, box.topLeft.y, box.topLeft.y, box.bottomRight.y]
            rr, cc = polygon_perimeter(r, c, image_with_boxes.shape)
            image_with_boxes[rr, cc] = 1  # set color white
        return image_with_boxes

    def writeToFile(self, filepath):
        self.__createDirectoriesIfNecessary(filepath)
        cv2.imwrite(filepath, self.asNumpyArray())  # save frame as JPEG file

    def __createDirectoriesIfNecessary(self, filepath):

        if not os.path.exists(os.path.dirname(filepath)):
            try:
                os.makedirs(os.path.dirname(filepath))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
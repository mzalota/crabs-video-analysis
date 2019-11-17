from cv2 import cv2, os

from pandas.compat.numpy import np
from common import Point, Box, Vector


#from Frame import Frame
#from lib.Frame import Frame


class Image:
    def __init__(self, imageAsNumpyArray):
        self.__image = imageAsNumpyArray

    @staticmethod
    def empty(height, width, color=0): #default color is black
        image = np.zeros([height, width, 3], dtype=np.uint8)
        image.fill(color)
        return Image(image)

    def width(self):
        return self.__image.shape[1]

    def height(self):
        return self.__image.shape[0]

    def asNumpyArray(self):
        return self.__image

    def copy(self):
        # type: () -> Image
        return Image(self.__image.copy())

    def drawLine(self, point1, point2, thickness=5, color=(0, 255, 0)):
        cv2.line(self.__image, (point1.x, point1.y), (point2.x, point2.y), color, thickness)

    def drawCross(self, point, size=8, color=(0, 255, 0)):
        self.drawLine(point.translateBy(Vector(-size, -size)), point.translateBy(Vector(size, size)), color=color)
        self.drawLine(point.translateBy(Vector(size, -size)), point.translateBy(Vector(-size, size)), color=color)

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
        #return Image(self.__image[max(box.topLeft.y,1):min(box.bottomRight.y,self.height()), max(box.topLeft.x,1): min(box.bottomRight.x,self.width())].copy())
        return Image(self.__image[max(box.topLeft.y,0):min(box.bottomRight.y,self.height()), max(box.topLeft.x,0): min(box.bottomRight.x,self.width())].copy())

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
        #print "brigtest spot maxLoc"
        #print maxLoc
        #print maxVal
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


    def padOnBottom(self, height):
        # type: (int) -> Image
        fillerHorizontal = Image.empty(height, self.width())
        return self.concatenateToTheBottom(fillerHorizontal)

    def padOnTop(self, height):
        # type: (int) -> Image
        fillerHorizontal = Image.empty(height, self.width())
        return fillerHorizontal.concatenateToTheBottom(self)

    def padLeft(self, widthToAdd):
        # type: (int) -> Image
        origHeight = self.height()
        filler = Image.empty(origHeight, widthToAdd)
        return filler.concatenateToTheRight(self)

    def padRight(self, widthToAdd):
        # type: (int) -> Image
        origHeight = self.height()
        filler = Image.empty(origHeight, widthToAdd)
        return self.concatenateToTheRight(filler)

    def padSidesToMakeWider(self, widthToAdd):
        #newWidth = self.width()
        origHeight = self.height()

        #widthToAdd = (origWidth - newWidth)

        fillerVertical1 = Image.empty(origHeight, int(widthToAdd / 2))
        fillerVertical2 = Image.empty(origHeight, widthToAdd - int(widthToAdd / 2))
        tmp2 = self.concatenateToTheRight(fillerVertical1)
        imageToReturn = fillerVertical2.concatenateToTheRight(tmp2)
        return imageToReturn

    def concatenateToTheBottom(self, imageObj):

        maxWidth = max(self.width(), imageObj.width())

        # get objects to the same width. Leave their heights unchanged
        topImageObj = self.growImage(maxWidth, self.height())
        bottomImageObj = imageObj.growImage(maxWidth, imageObj.height())

        resultImg = self.__concatenateNumpyArrayToTheBottom(topImageObj.asNumpyArray(), bottomImageObj.asNumpyArray())
        return Image(resultImg)


    def concatenateToTheRight(self, imageObj):

        maxHeight = max(self.height(), imageObj.height())

        #get objects to the same height. Leave their widths unchanged
        leftImageObj = self.growImage(self.width(), maxHeight)
        rightImageObj = imageObj.growImage(imageObj.width(), maxHeight)

        resultImg = self.__concatenateNumpyArrayToTheRight(leftImageObj.asNumpyArray(), rightImageObj.asNumpyArray())
        return Image(resultImg)

    def resizeImage(self, newHeight, newWidth):
        # type: (int, int) -> Image
        newImageNP = cv2.resize(self.asNumpyArray(), dsize=(newWidth, newHeight),
                                   interpolation=cv2.INTER_CUBIC)
        return Image(newImageNP)

    def growImage(self, newWidth, newHeight):
        fillerWidth = newWidth - self.width()
        fillerHeight = newHeight - self.height()

        return Image(self.__padFillers(self, fillerWidth, fillerHeight))

    def __padFillers(self, imgObj, fillerWidth, fillerHeight):

        fillerBottom = Image.empty(fillerHeight, imgObj.width(), 0)
        tmpImg = self.__concatenateNumpyArrayToTheBottom(imgObj.asNumpyArray(), fillerBottom.asNumpyArray())

        newHeight = imgObj.height() + fillerHeight
        fillerRight = Image.empty(newHeight, fillerWidth, 0)
        return self.__concatenateNumpyArrayToTheRight(tmpImg, fillerRight.asNumpyArray())

    def __concatenateNumpyArrayToTheBottom(self, topImg, bottomImg):
        return np.concatenate((topImg, bottomImg))

    def __concatenateNumpyArrayToTheRight(self, leftImg, rightImg):
        return np.concatenate((leftImg, rightImg), axis=1)

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
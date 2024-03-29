from __future__ import annotations

import cv2
import numpy as np

from lib.infra.FolderStructure import FolderStructure
from lib.model.Box import Box
from lib.model.Vector import Vector
from lib.model.Point import Point


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

    def is_identical_to(self, other_image: Image) -> bool:
        return np.array_equal(self.asNumpyArray(), other_image.asNumpyArray())

    def copy(self):
        # type: () -> Image
        return Image(self.__image.copy())

    def drawLine(self, point1, point2, thickness=5, color=(0, 255, 0)):
        cv2.line(self.__image, (point1.x, point1.y), (point2.x, point2.y), color, thickness)

    def drawCross(self, point, size=8, color=(0, 255, 0)):
        self.drawLine(point.translateBy(Vector(-size, -size)), point.translateBy(Vector(size, size)), color=color)
        self.drawLine(point.translateBy(Vector(size, -size)), point.translateBy(Vector(-size, size)), color=color)

    def drawCrossVertical(self, point, size=8, color=(0, 255, 0)):
        self.drawLine(point.translateBy(Vector(-size, 0)), point.translateBy(Vector(size, 0)), thickness=2, color=color)
        self.drawLine(point.translateBy(Vector(0, -size)), point.translateBy(Vector(0, size)), thickness=2, color=color)

    def drawBoxOnImage(self, box, color=(0, 255, 0), thickness = 2):
        if not box:
            return

        cv2.rectangle(self.__image, (int(box.topLeft.x), int(box.topLeft.y)), (int(box.bottomRight.x), int(box.bottomRight.y)), color, thickness)

    def drawFrameID(self, frameID):
        self.drawTextInBox(Box(Point(0, 0), Point(80, 50)), frameID)

    def drawTextInBox(self, box, text, color = (0, 255, 0)):
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (box.topLeft.x, box.topLeft.y + 27)
        fontScale = 1
        #fontColor = (0, 255, 0)
        lineType = 2
        cv2.putText(self.__image, str(text),
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    color,
                    lineType)

    def drawDriftVectorOnImage(self, driftVector, vectorStart = Point(100, 100)):
        if driftVector is not None:
            vectorEnd = vectorStart.translateBy(driftVector)
            #vectorBox = Box(vectorStart, vectorEnd)
            #self.drawBoxOnImage(vectorBox)

            self.drawLine(vectorStart, vectorEnd)

    def subImage(self, box):
        # type: (Box) -> Image
        #return Image(self.__image[max(box.topLeft.y,1):min(box.bottomRight.y,self.height()), max(box.topLeft.x,1): min(box.bottomRight.x,self.width())].copy())
        return Image(self.__image[int(max(box.topLeft.y,0)):int(min(box.bottomRight.y,self.height())), 
                                int(max(box.topLeft.x,0)): int(min(box.bottomRight.x,self.width()))].copy())

    def bottomPart(self, height):
        # type: (integer) -> Image
        box = Box(Point(0, self.height() - height), Point(self.width(), self.height()))
        return self.subImage(box)

    def topPart(self, height):
        # type: (integer) -> Image
        box = Box(Point(0, 0), Point(self.width(), height))
        return self.subImage(box)


    def shiftImageHorizontally(self, pixelsToShift):
        # type: (int) -> Image

        boxSizeOfImage = Box.createUsingDimesions(self.width(), self.height())

        fillerWidth = abs(pixelsToShift)
        imageWithFillerOnBothSides = self.padSidesToMakeWider(fillerWidth*2)
        boxEncompasingImage = boxSizeOfImage.translateBy(Vector(fillerWidth, 0))

        #slide "boxEncompasingImage" to the left or to the right depending if xDrift is negative or positive
        boxAroundAreaThatWeNeedToCrop = boxEncompasingImage.translateBy(Vector(pixelsToShift, 0))
        return imageWithFillerOnBothSides.subImage(boxAroundAreaThatWeNeedToCrop)

    def adjustWidthWithoutRescaling(self,newWidth):
        if self.width() > newWidth:
            return self.trimSides(newWidth)
        else:
            return self.padSidesToMakeWider(newWidth - self.width())

    def trimSides(self, newWidth):
        # type: (int) -> Image
        widthToCutOutLeft = int((self.width() - newWidth) / 2)

        areaToCut = Box(Point(widthToCutOutLeft, 0), Point(widthToCutOutLeft + newWidth, self.height()))
        return  self.subImage(areaToCut)

    def padSidesToMakeWider(self, widthToAdd):
        # type: (int) -> Image
        leftPadding = int(widthToAdd / 2)
        rightPadding = widthToAdd - leftPadding
        return self.padLeft(leftPadding).padRight(rightPadding)

    def padOnBottom(self, height):
        # type: (int) -> Image
        filler = Image.empty(height, self.width())
        return Image(self.__concatenateNumpyArrayToTheBottom(self.asNumpyArray(),filler.asNumpyArray()))

    def padOnTop(self, height):
        # type: (int) -> Image
        filler = Image.empty(height, self.width())
        return Image(self.__concatenateNumpyArrayToTheBottom(filler.asNumpyArray(),self.asNumpyArray()))

    def padLeft(self, widthToAdd):
        # type: (int) -> Image
        filler = Image.empty(self.height(), widthToAdd)
        return Image(self.__concatenateNumpyArrayToTheRight(filler.asNumpyArray(),self.asNumpyArray()))

    def padRight(self, widthToAdd):
        # type: (int) -> Image
        filler = Image.empty(self.height(), widthToAdd)
        return Image(self.__concatenateNumpyArrayToTheRight(self.asNumpyArray(),filler.asNumpyArray()))

    def concatenateToTheBottom(self, imageObj):
        # type: (Image) -> Image
        maxWidth = max(self.width(), imageObj.width())

        # get objects to the same width. Leave their heights unchanged
        topImageObj = self.growByPaddingBottomAndRight(maxWidth, self.height())
        bottomImageObj = imageObj.growByPaddingBottomAndRight(maxWidth, imageObj.height())

        resultImg = self.__concatenateNumpyArrayToTheBottom(topImageObj.asNumpyArray(), bottomImageObj.asNumpyArray())
        return Image(resultImg)

    def concatenateToTheRight(self, imageObj):
        # type: (Image) -> Image
        maxHeight = max(self.height(), imageObj.height())

        #get objects to the same height. Leave their widths unchanged
        leftImageObj = self.growByPaddingBottomAndRight(self.width(), maxHeight)
        rightImageObj = imageObj.growByPaddingBottomAndRight(imageObj.width(), maxHeight)

        resultImg = self.__concatenateNumpyArrayToTheRight(leftImageObj.asNumpyArray(), rightImageObj.asNumpyArray())
        return Image(resultImg)


    def scaleImage(self, newHeight, newWidth):
        # type: (int, int) -> Image
        newImageNP = cv2.resize(self.asNumpyArray(), dsize=(newWidth, newHeight),
                                interpolation=cv2.INTER_CUBIC)
        return Image(newImageNP)

    def scale_by_factor(self, scale_factor: float) -> Image:
        return self.scaleImage(int(self.height() * scale_factor), int(self.width() * scale_factor))

    def growByPaddingBottomAndRight(self, newWidth, newHeight):
        # type: (int, int) -> Image
        fillerWidth = newWidth - self.width()
        fillerHeight = newHeight - self.height()
        return self.padOnBottom(fillerHeight).padRight(fillerWidth)

    def __concatenateNumpyArrayToTheBottom(self, topImg, bottomImg):
        # type: (np, np) -> np
        return np.concatenate((topImg, bottomImg))

    def __concatenateNumpyArrayToTheRight(self, leftImg, rightImg):
        # type: (np, np) -> np
        return np.concatenate((leftImg, rightImg), axis=1)

    # based on this article:
    # https://stackoverflow.com/questions/39308030/how-do-i-increase-the-contrast-of-an-image-in-python-opencv
    # Contrast control (1.0-3.0)
    # Brightness control (0-100)
    def changeBrightness(self, contrast, brightness):
        # type: (float, float) -> Image
        adjusted = cv2.convertScaleAbs(self.asNumpyArray(), alpha=contrast, beta=brightness)
        return Image(adjusted)

    def equalize(self):
        equalized = self.__eqHist(self.asNumpyArray())
        return Image(equalized)

    def sharpen(self):
        # image_sharp = self._sharp_mask(self.asNumpyArray(), amount=3.0)
        image_sharp = self.__sharp_mask(self.asNumpyArray(), sigma=2.0, amount=6.0, threshold=1)
        return Image(image_sharp)

    def sharpen_more(self):
        image_sharp = self.__sharp_mask(self.asNumpyArray(), sigma=4.0, amount=12.0, threshold=2)
        return Image(image_sharp)

    # as described here https://stackoverflow.com/a/55590133/962244
    def __sharp_mask(self, image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
        """Return a sharpened version of the image, using an unsharp mask."""
        blurred = cv2.GaussianBlur(image, kernel_size, sigma)
        sharpened = float(amount + 1) * image - float(amount) * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint8)
        if threshold > 0:
            low_contrast_mask = np.absolute(image - blurred) < threshold
            np.copyto(sharpened, image, where=low_contrast_mask)
        return sharpened

    def writeToFile(self, filepath):
        FolderStructure.createDirectoriesIfDontExist(filepath)
        cv2.imwrite(filepath, self.asNumpyArray())  # save frame as JPEG file

        if not cv2.imwrite(filepath, self.asNumpyArray()):
            mesage = "Could not write image: " + filepath + ", width: " + str(self.width()) + ", height: " + str(
                self.height())
            print("ERROR in Image.py in writeToFile: "+mesage)
            raise Exception(mesage)

    def __eqHist(self, image, clache=True, gray_only=False):
        """
        Equalization of image, by default based on CLACHE method
        """
        if gray_only:
            L = image
        else:
            imgHLS = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
            L = imgHLS[:,:,1]
        if clache:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            equ = clahe.apply(L)
        else:
            equ = cv2.equalizeHist(L)

        if gray_only:
            return equ

        imgHLS[:,:,1] = equ
        res = cv2.cvtColor(imgHLS, cv2.COLOR_HLS2BGR)
        return res
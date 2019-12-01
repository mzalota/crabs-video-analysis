from pandas.compat.numpy import np

import cv2

from lib.Frame import Frame
from lib.FrameDecorators import DecoMarkedCrabs, DecoGridLines, FrameDecorator, DecoRedDots, FrameDecoFactory
from lib.Image import Image
from lib.MyTimer import MyTimer
from lib.common import Point, Box, Vector


class ImagesCollage:
    def __init__(self, frameImagesFactory, seeFloorGeometry):
        # type: (FrameDecoFactory, SeeFloor) -> object
        #self.__videoStream = videoStream
        self.__frameImagesFactory = frameImagesFactory
        self.__seeFloorGeometry = seeFloorGeometry

    def constructCollage(self, thisFrameID, neighboursHeight):
        # type: (Frame, Int) -> Image

        paddingBetweenCollages = 20

        leftCollage = self.constructLeftCollage(thisFrameID, neighboursHeight)
        rightCollage = self.constructRightCollage(thisFrameID, leftCollage.height())

        #concatenate left collage to the right with a small padding in-between
        wholeCollage = leftCollage.padRight(paddingBetweenCollages).concatenateToTheRight(rightCollage)

        return wholeCollage

    def constructLeftCollage(self, thisFrameID, neighboursHeight):

        thisFrameImage = self.__constructImageUsingFrameDeco(thisFrameID, thisFrameID)
        thisFrameImage.drawFrameID(thisFrameID)

        prevFrameID = self.__seeFloorGeometry.getPrevFrame(thisFrameID)
        nextFrameID = self.__seeFloorGeometry.getNextFrame(thisFrameID)

        prevSubImage = self.__buildImageUsingTopPart(thisFrameID, prevFrameID, neighboursHeight)
        nextSubImage = self.__buildImageUsingBottomPart(thisFrameID, nextFrameID, neighboursHeight)

        leftCollage = nextSubImage.concatenateToTheBottom(thisFrameImage).concatenateToTheBottom(prevSubImage)

        return leftCollage

    def constructRightCollage(self, thisFrameID, mainCollageHeight):
        # type: (Frame, int) -> Image
        height = Frame.FRAME_HEIGHT

        afterMiddleFrameID = self.__getFrameIDForRightTopImage(thisFrameID)
        beforeMiddleFrameID = self.__seeFloorGeometry.getPrevFrame(afterMiddleFrameID)

        beforeMiddleImage = self.__buildImageUsingTopPart(thisFrameID, beforeMiddleFrameID, height)
        afterMiddleImage = self.__buildImageUsingBottomPart(thisFrameID, afterMiddleFrameID, height)

        rightCollageHeight = beforeMiddleImage.height() + afterMiddleImage.height()
        fillerHeight = int((mainCollageHeight - rightCollageHeight) / 2)

        rightCollageWithoutBottomFiller = afterMiddleImage.concatenateToTheBottom(beforeMiddleImage).padOnTop(fillerHeight)
        rightCollage = rightCollageWithoutBottomFiller.padOnBottom(mainCollageHeight-rightCollageWithoutBottomFiller.height())

        return rightCollage

    def __getFrameIDForRightTopImage(self, thisFrameID):
        thisFrameHeightMM = self.__seeFloorGeometry.heightMM(int(thisFrameID))
        afterMiddleFrameID = self.__seeFloorGeometry.getFrame(thisFrameHeightMM / 2, thisFrameID)
        return afterMiddleFrameID

    def __buildImageUsingTopPart(self, referenceFrameID, frameID, height):
        # type: (int, int, int) -> Image
        origImage = self.__constructImageUsingFrameDeco(referenceFrameID, frameID)
        adjustedImage = self.__scaleAndSchiftOtherFrameToMatchThisFrame(referenceFrameID, frameID, origImage)

        imageToReturn = adjustedImage.topPart(int(height))

        if imageToReturn.height()<height:
            imageToReturn = imageToReturn.padOnBottom(height-imageToReturn.height())

        imageToReturn.drawFrameID(frameID)
        return imageToReturn

    def __buildImageUsingBottomPart(self, referenceFrameID, frameID, height):
        # type: (int, int, int) -> Image

        origImage = self.__constructImageUsingFrameDeco(referenceFrameID, frameID)
        adjustedImage = self.__scaleAndSchiftOtherFrameToMatchThisFrame(referenceFrameID, frameID, origImage)

        imageToReturn = adjustedImage.bottomPart(int(height))
        if imageToReturn.height()<height:
            imageToReturn = imageToReturn.padOnTop(height-imageToReturn.height())

        imageToReturn.drawFrameID(frameID)
        return imageToReturn

    def __constructImageUsingFrameDeco(self, referenceFrameID, frameID):
        # type: (int, int) -> Image
        #timer = MyTimer("in ImagesCollage.__constructFrame")

        frameDeco = self.__frameImagesFactory.getFrame(frameID)
        frameDeco = self.__frameImagesFactory.getFrameDecoMarkedCrabs(frameDeco)
        frameDeco = self.__frameImagesFactory.getFrameDecoGridLines(frameDeco, referenceFrameID)
        frameDeco = self.__frameImagesFactory.getFrameDecoRedDots(frameDeco)

        #timer.lap("chaining frameDeco")
        #TODO: Optimize! The function below takes 500ms to execute and it is called 5 times to build each Collage (2,5 seconds)
        newImage = frameDeco.getImgObj()
        #timer.lap("frameDeco.getImgObj()")
        return newImage.copy()


    def __scaleAndSchiftOtherFrameToMatchThisFrame(self, referenceFrameID, frameID, imageToScale):
        # type: (int, int, Image) -> Image

        width = imageToScale.width()
        #scalingFactor = self.__calculateImageScalingFactor(referenceFrameID, frameID)
        scalingFactor = self.__seeFloorGeometry.getRedDotsData().scalingFactor(referenceFrameID, frameID)
        xShift = self.__seeFloorGeometry.getXDriftPixels(referenceFrameID, frameID)

        newHeight = int(imageToScale.height() * scalingFactor)
        newWidth = int(imageToScale.width() * scalingFactor)
        scaledImage = imageToScale.scaleImage(newHeight, newWidth)

        if scalingFactor > 1:
            imageShiftedAlongXAxis = scaledImage.shiftImageHorizontally(xShift)
            imageCorrectWidth = imageShiftedAlongXAxis.adjustWidthWithoutRescaling(width)
            imageToReturn = imageCorrectWidth
        else:
            imageCorrectWidth = scaledImage.adjustWidthWithoutRescaling(width)
            imageShiftedAlongXAxis = imageCorrectWidth.shiftImageHorizontally(xShift)
            imageToReturn = imageShiftedAlongXAxis

        return imageToReturn

from pandas.compat.numpy import np

import cv2

from lib.Frame import Frame
from lib.FrameDecorators import DecoMarkedCrabs, DecoGridLines, FrameDecorator, DecoRedDots
from lib.Image import Image
from lib.MyTimer import MyTimer
from lib.common import Point, Box, Vector


class ImagesCollage:
    def __init__(self, videoStream, seeFloorGeometry, crabsData):
        # type: (VideoStream, SeeFloor, CrabsData) -> object
        self.__videoStream = videoStream
        self.__seeFloorGeometry = seeFloorGeometry
        self.__crabsData = crabsData

    def attachNeighbourFrames(self, thisFrameID, neighboursHeight):
        # type: (Frame, Int) -> Image

        paddingBetweenCollages = 20

        leftCollage = self.constructLeftCollage(thisFrameID, neighboursHeight)
        rightCollage = self.constructRightCollage(thisFrameID, leftCollage.height())

        #concatenate left collage to the right with a small padding in-between
        wholeCollage = leftCollage.padRight(paddingBetweenCollages).concatenateToTheRight(rightCollage)

        return wholeCollage

    def constructLeftCollage(self, thisFrameID, neighboursHeight):

        thisFrameImage = self.__constructImageUsingFrameDeco(thisFrameID, thisFrameID)

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
        newFrame = Frame(frameID, self.__videoStream)

        frameDeco = DecoMarkedCrabs(newFrame, self.__seeFloorGeometry)

        gridMidPoint = self.__seeFloorGeometry.getRedDotsData().midPoint(referenceFrameID)
        drift = self.__seeFloorGeometry.getDriftData().driftBetweenFrames(referenceFrameID, frameID)
        newPoint = gridMidPoint.translateBy(drift)

        frameDeco = DecoGridLines(frameDeco, self.__seeFloorGeometry.getRedDotsData(), newPoint)
        frameDeco = DecoRedDots(frameDeco,self.__seeFloorGeometry.getRedDotsData())

        #timer.lap("chaining frameDeco")
        #TODO: Optimize! The function below takes 500ms to execute and it is called 5 times to build each Collage (2,5 seconds)
        newImage = frameDeco.getImgObj()
        #timer.lap("frameDeco.getImgObj()")
        return newImage.copy()

    def __scaleAndSchiftOtherFrameToMatchThisFrame(self, referenceFrameID, frameID, imageToScale):
        # type: (int, int, Image) -> Image

        width = imageToScale.width()
        scalingFactor = self.__calculateImageScalingFactor(referenceFrameID, frameID)
        xShift = self.__xDriftBetweenFrames(referenceFrameID, frameID)

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

    def __calculateImageScalingFactor(self, thisFrameID, otherFrameID):
        distanceThis = self.__seeFloorGeometry.getRedDotsData().getDistancePixels(thisFrameID)
        distancePrev = self.__seeFloorGeometry.getRedDotsData().getDistancePixels(otherFrameID)
        scalingFactor = distanceThis / distancePrev
        return scalingFactor

    def __xDriftBetweenFrames(self, thisFrameID, nextFrameID):
        # type: (int, int) -> int
        xDriftMM = self.__seeFloorGeometry.getXDriftMM(thisFrameID,nextFrameID)
        mmPerPixel = self.__seeFloorGeometry.getRedDotsData().getMMPerPixel(thisFrameID)
        xDrift = xDriftMM/mmPerPixel
        return int(xDrift)

    def __shiftImageHorizontally_orig(self, subImage, xDrift):

        #add filler to both sides of subImage.
        fillerWidth = abs(xDrift)
        fillerImage = Image.empty(subImage.height(), fillerWidth, 0)
        result = np.concatenate((fillerImage.asNumpyArray(), subImage.asNumpyArray(), fillerImage.asNumpyArray()), axis=1)
        subImageWithFillerOnBothSides = Image(result)
        boxAroundImage = Box(Point(fillerWidth, 0), Point(fillerWidth + subImage.width(), subImage.height()))

        #slide "boxAroundImage" to the left or to the right depending if xDrift is negative or positive
        boxAroundAreaThatWeNeedToKeep = boxAroundImage.translateBy(Vector(xDrift,0))
        imageToReturn = subImageWithFillerOnBothSides.subImage(boxAroundAreaThatWeNeedToKeep)
        return imageToReturn




from pandas.compat.numpy import np

import cv2

from lib.Frame import Frame
from lib.FrameDecorators import DecoMarkedCrabs, DecoGridLines, FrameDecorator, DecoRedDots
from lib.Image import Image
from lib.common import Point, Box, Vector


class ImagesCollage:
    def __init__(self, videoStream, seeFloorGeometry, crabsData):
        # type: (VideoStream, SeeFloor, CrabsData) -> object
        self.__videoStream = videoStream
        self.__seeFloorGeometry = seeFloorGeometry
        self.__crabsData = crabsData

    def attachNeighbourFrames(self, thisFrame, neighboursHeight):
        # type: (Frame, Int) -> Image

        paddingBetweenCollages = 20

        leftCollage = self.constructLeftCollage(thisFrame.getFrameID(), neighboursHeight)

        rightCollage = self.constructRightCollage(thisFrame.getFrameID(), leftCollage.height())

        wholeCollage = leftCollage.padRight(paddingBetweenCollages).concatenateToTheRight(rightCollage)

        return wholeCollage

    def constructLeftCollage(self, thisFrameID, neighboursHeight):

        thisFrameImage = self.__constructFrame(thisFrameID,thisFrameID).getImgObj().copy()

        prevFrameID = self.__seeFloorGeometry.getPrevFrame(thisFrameID)
        nextFrameID = self.__seeFloorGeometry.getNextFrame(thisFrameID)

        prevSubImage = self.__buildPrevImagePart(thisFrameID, prevFrameID, neighboursHeight)
        nextSubImage = self.__buildNextImagePart(thisFrameID, nextFrameID, neighboursHeight)

        leftCollage = nextSubImage.concatenateToTheBottom(thisFrameImage).concatenateToTheBottom(prevSubImage)

        return leftCollage

    def constructRightCollage(self, thisFrameID, mainCollageHeight):
        # type: (Frame, int) -> Image
        height = Frame.FRAME_HEIGHT

        afterMiddleFrameID = self.__getFrameIDForRightTopImage(thisFrameID)
        beforeMiddleFrameID = self.__seeFloorGeometry.getPrevFrame(afterMiddleFrameID)

        beforeMiddleImage = self.__buildPrevImagePart(thisFrameID, beforeMiddleFrameID, height)
        afterMiddleImage = self.__buildNextImagePart(thisFrameID, afterMiddleFrameID, height)

        rightCollageHeight = beforeMiddleImage.height() + afterMiddleImage.height()
        fillerHeight = int((mainCollageHeight - rightCollageHeight) / 2)

        rightCollageWithoutBottomFiller = afterMiddleImage.concatenateToTheBottom(beforeMiddleImage).padOnTop(fillerHeight)
        rightCollage = rightCollageWithoutBottomFiller.padOnBottom(mainCollageHeight-rightCollageWithoutBottomFiller.height())

        return rightCollage


    def __getFrameIDForRightTopImage(self, thisFrameID):
        thisFrameHeightMM = self.__seeFloorGeometry.heightMM(int(thisFrameID))
        afterMiddleFrameID = self.__seeFloorGeometry.getFrame(thisFrameHeightMM / 2, thisFrameID)
        return afterMiddleFrameID

    def __buildPrevImagePart(self, thisFrameID, prevFrameID, height):
        # type: (int, int, int) -> Image

        prevFrame = self.__constructFrame(prevFrameID, thisFrameID)

        #TODO: move copy() of image into constructFrame() function
        origImage = prevFrame.getImgObj().copy()
        adjustedImage = self.__scaleAndSchiftOtherFrameToMatchThisFrame(thisFrameID, prevFrameID, origImage)

        imageToReturn = adjustedImage.topPart(int(height))

        if imageToReturn.height()<height:
            imageToReturn = imageToReturn.padOnBottom(height-imageToReturn.height())

        imageToReturn.drawFrameID(prevFrameID)
        return imageToReturn


    def __buildNextImagePart(self, thisFrameID, nextFrameID, height):
        # type: (int, int, int) -> Image

        nextFrame = self.__constructFrame(nextFrameID, thisFrameID)

        #TODO: move copy() of image into constructFrame() function
        origImage = nextFrame.getImgObj().copy()
        adjustedImage = self.__scaleAndSchiftOtherFrameToMatchThisFrame(thisFrameID, nextFrameID, origImage)

        imageToReturn = adjustedImage.bottomPart(int(height))
        if imageToReturn.height()<height:
            imageToReturn = imageToReturn.padOnTop(height-imageToReturn.height())

        imageToReturn.drawFrameID(nextFrameID)
        return imageToReturn

    def __constructFrame(self, newFrameID, thisFrameID):
        # type: (int, int) -> FrameDecorator

        newFrame = Frame(newFrameID, self.__videoStream)

        frameDeco = DecoMarkedCrabs(newFrame, self.__seeFloorGeometry)

        gridMidPoint = self.__seeFloorGeometry.getRedDotsData().midPoint(thisFrameID)
        drift = self.__seeFloorGeometry.getDriftData().driftBetweenFrames(thisFrameID, newFrameID)
        newPoint = gridMidPoint.translateBy(drift)

        frameDeco2 = DecoGridLines(frameDeco, self.__seeFloorGeometry.getRedDotsData(), newPoint)
        frameDeco3 = DecoRedDots(frameDeco2,self.__seeFloorGeometry.getRedDotsData())
        return frameDeco3

    def __scaleAndSchiftOtherFrameToMatchThisFrame(self, thisFrameID, otherFrameID, image):
        # type: (int, int, Image) -> Image
        width = image.width()

        scalingFactor = self.__calculateImageScalingFactor(thisFrameID, otherFrameID)
        xShift = self.__xDriftBetweenFrames(thisFrameID, otherFrameID)

        newHeight = int(image.height() * scalingFactor)
        newWidth = int(image.width() * scalingFactor)
        #scaledImage = self.__resizeImage(imgCopy, newHeight, newWidth)
        scaledImage = image.resizeImage(newHeight, newWidth)

        if scalingFactor > 1:
            xShiftedImage = self.__shiftImageHorizontally(scaledImage, xShift)
            imageToReturn = xShiftedImage.adjustWidthWithoutRescaling(width)
        else:
            tmp2 = scaledImage.adjustWidthWithoutRescaling(width)
            imageToReturn = self.__shiftImageHorizontally(tmp2, xShift)

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

    def __shiftImageHorizontally(self, subImage, xDrift):

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




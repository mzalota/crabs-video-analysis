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
        # type: (Frame, Int) -> np

        image = thisFrame.getImgObj()
        image.drawFrameID(thisFrame.getFrameID())

        collageHeight = thisFrame.getImgObj().height() + neighboursHeight * 2

        leftCollage = self.constructLeftCollage(thisFrame, neighboursHeight, image)

        rightCollage = self.constructRightCollage(thisFrame, collageHeight)
        print ("rightCollage hight", rightCollage.height(), "width", rightCollage.width())

        withImageOnTheRight = self.__mergeSideBySide(leftCollage, rightCollage, collageHeight)

        return withImageOnTheRight


    def __mergeSideBySide(self, leftCollage, rightCollage, collageHeight):
        filler = Image.empty(collageHeight, 100, 0).asNumpyArray()
        withImageOnTheRight = np.concatenate((leftCollage.asNumpyArray(), filler, rightCollage.asNumpyArray()), axis=1)
        return withImageOnTheRight

    def __resizeImage(self, mainCollage, newHeight, newWidth):
        # type: (Image, int, int) -> Image
        mainCollageNP = cv2.resize(mainCollage.asNumpyArray(), dsize=(newWidth, newHeight),
                                   interpolation=cv2.INTER_CUBIC)
        return Image(mainCollageNP)

    def __getFrameIDForLeftTopImage(self, thisFrame):
        # type: (Frame) -> int
        nextFrameID = self.__seeFloorGeometry.getNextFrame(thisFrame.getFrameID()) #.jumpToSeefloorSlice(thisFrame.getFrameID(), +1)
        return nextFrameID

    def __getFrameIDForLeftBottomImage(self, thisFrame):
        # type: (Frame) -> int
        prevFrameID = self.__seeFloorGeometry.getPrevFrame(thisFrame.getFrameID()) # .jumpToSeefloorSlice(thisFrame.getFrameID(), -1)
        return prevFrameID

    def __constructFrame(self, newFrameID, thisFrameID):
        # type: (int, Frame) -> FrameDecorator

        #thisFrameID = thisFrame.getFrameID()
        newFrame = Frame(newFrameID, self.__videoStream)

        frameDeco = DecoMarkedCrabs(newFrame, self.__seeFloorGeometry)

        gridMidPoint = self.__seeFloorGeometry.getRedDotsData().midPoint(thisFrameID)
        drift = self.__seeFloorGeometry.getDriftData().driftBetweenFrames(thisFrameID, newFrameID)
        newPoint = gridMidPoint.translateBy(drift)

        frameDeco2 = DecoGridLines(frameDeco, self.__seeFloorGeometry.getRedDotsData(), newPoint)
        frameDeco3 = DecoRedDots(frameDeco2,self.__seeFloorGeometry.getRedDotsData())
        return frameDeco3

    def constructLeftCollage(self, thisFrame, neighboursHeight, image):
        prevFrameID = self.__getFrameIDForLeftBottomImage(thisFrame)
        nextFrameID = self.__getFrameIDForLeftTopImage(thisFrame)

        prevSubImage = self.__buildPrevImagePart(thisFrame.getFrameID(), prevFrameID, neighboursHeight)
        nextSubImage = self.__buildNextImagePart(thisFrame.getFrameID(), nextFrameID, neighboursHeight)

        mainCollage = self.__glueTogether(image, nextSubImage, prevSubImage)

        # resize leftCollage
        newWidth = mainCollage.width()
        newHeight = mainCollage.height()
        leftCollage = self.__resizeImage(mainCollage, newHeight, newWidth)

        print ("leftCollage hight", newHeight, "width", newWidth)

        return leftCollage

    def constructRightCollage(self, thisFrame, mainCollageHeight):
        # type: (Frame, int) -> Image
        beforeMiddleFrameID = self.getFrameIDForRightBottomImage(thisFrame)
        afterMiddleFrameID = self.__getFrameIDForRightTopImage(thisFrame)

        beforeMiddleImage = self.__buildPrevImagePart(thisFrame.getFrameID(), beforeMiddleFrameID, thisFrame.getImgObj().height())
        #self.__constructRightPrev(thisFrame, beforeMiddleFrameID)
        #afterMiddleImage = self.__constructRightNext(thisFrame)
        afterMiddleImage = self.__buildNextImagePart(thisFrame.getFrameID(), afterMiddleFrameID, thisFrame.getImgObj().height())

        rightCollageHeight = beforeMiddleImage.height() + afterMiddleImage.height()
        fillerHeight = (mainCollageHeight - rightCollageHeight) / 2
        fillerImage = Image.empty(fillerHeight, thisFrame.getImgObj().width(), 0).asNumpyArray()

        collageNP = np.concatenate((fillerImage, afterMiddleImage.asNumpyArray(), beforeMiddleImage.asNumpyArray(), fillerImage))
        return Image(collageNP)

    def __constructRightNext_old(self, thisFrame):
        # type: (Frame) -> Image

        afterMiddleFrameID = self.__getFrameIDForRightTopImage(thisFrame)

        afterMiddleImage = self.__buildNextImagePart(thisFrame.getFrameID(), afterMiddleFrameID, thisFrame.getImgObj().height())
        return afterMiddleImage

    def __getFrameIDForRightTopImage(self, thisFrame):
        thisFrameHeightMM = self.__seeFloorGeometry.heightMM(int(thisFrame.getFrameID()))
        afterMiddleFrameID = self.__seeFloorGeometry.getFrame(thisFrameHeightMM / 2, thisFrame.getFrameID())
        return afterMiddleFrameID

    def __constructRightPrev_old(self, thisFrame, beforeMiddleFrameID):
        # type: (Frame) -> Image

        beforeMiddleImage = self.__buildPrevImagePart(thisFrame.getFrameID(), beforeMiddleFrameID, thisFrame.getImgObj().height())
        return beforeMiddleImage

    def getFrameIDForRightBottomImage(self, thisFrame):
        thisFrameHeightMM = self.__seeFloorGeometry.heightMM(int(thisFrame.getFrameID()))
        beforeMiddleFrameID = self.__seeFloorGeometry.getFrame(-thisFrameHeightMM / 2, thisFrame.getFrameID())
        return beforeMiddleFrameID

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

    def __scaleAndSchiftOtherFrameToMatchThisFrame(self, thisFrameID, otherFrameID, imgCopy):
        # type: (int, int, Image) -> Image
        width = imgCopy.width()

        scalingFactor = self.__calculateImageScalingFactor(thisFrameID, otherFrameID)
        xShift = self.__xDriftBetweenFrames(thisFrameID, otherFrameID)
        scaledImage = self.__resizeImage(imgCopy, int(imgCopy.height() * scalingFactor), int(imgCopy.width() * scalingFactor))

        if scalingFactor > 1:
            xShiftedImage = self.__shiftImageHorizontally(scaledImage, int(xShift))
            imageToReturn = xShiftedImage.adjustWidthWithoutRescaling(width)
        else:
            tmp2 = scaledImage.adjustWidthWithoutRescaling(width)
            imageToReturn = self.__shiftImageHorizontally(tmp2, int(xShift))
        return imageToReturn


    def __calculateImageScalingFactor(self, thisFrameID, otherFrameID):
        distanceThis = self.__seeFloorGeometry.getRedDotsData().getDistancePixels(thisFrameID)
        distancePrev = self.__seeFloorGeometry.getRedDotsData().getDistancePixels(otherFrameID)
        scalingFactor = distanceThis / distancePrev
        return scalingFactor

    def __xDriftBetweenFrames(self, thisFrameID, nextFrameID):

        xDriftMM = self.__seeFloorGeometry.getXDriftMM(thisFrameID,nextFrameID)
        mmPerPixel = self.__seeFloorGeometry.getRedDotsData().getMMPerPixel(thisFrameID)
        xDrift = int(xDriftMM/mmPerPixel)

        driftRaw = self.__seeFloorGeometry.getDriftData().driftBetweenFrames(thisFrameID, nextFrameID)
        print ("in __xDriftBetweenFrames: thisFrameID", thisFrameID, "nextFrameID", nextFrameID, "driftRaw", driftRaw.x, "xDrift", xDrift, "xDriftMM", xDriftMM)
        return xDrift

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

    def __glueTogether(self, image, nextSubImage, prevSubImage):
        # type: (Image, Image, Image) -> Image
        res = np.concatenate((nextSubImage.asNumpyArray(), image.asNumpyArray()))
        res2 = np.concatenate((res, prevSubImage.asNumpyArray()))
        return Image(res2)


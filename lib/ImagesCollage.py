from pandas.compat.numpy import np

import cv2

from lib.Frame import Frame
from lib.FrameDecorators import DecoMarkedCrabs, DecoGridLines, FrameDecorator
from lib.Image import Image
from lib.common import Point, Box, Vector


class ImagesCollage:
    def __init__(self, videoStream, seeFloorGeometry, crabsData):
        self.__videoStream = videoStream
        self.__seeFloorGeometry = seeFloorGeometry
        self.__crabsData = crabsData

    def attachNeighbourFrames(self, thisFrame, neighboursHeight):
        # type: (Frame, Int) -> np

        prevFrame = self.__getPrevFrame(thisFrame)
        nextFrame = self.__getNextFrame(thisFrame)

        image = thisFrame.getImgObj()
        image.drawFrameID(thisFrame.getFrameID())

        prevSubImage = self.__buildPrevImagePart(thisFrame, prevFrame, neighboursHeight)
        nextSubImage = self.__buildNextImagePart(thisFrame, nextFrame, neighboursHeight)

        mainCollage = self.__glueTogether(image, nextSubImage, prevSubImage)

        #resize leftCollage
        newWidth = mainCollage.width()
        newHeight = mainCollage.height()
        leftCollage = self.__resizeImage(mainCollage, newHeight, newWidth)

        collageHeight = thisFrame.getImgObj().height() + neighboursHeight * 2

        rightCollage = self.constructRightCollage(thisFrame, nextFrame, prevFrame, collageHeight)
        filler = Image.empty(collageHeight, 100, 0).asNumpyArray()

        withImageOnTheRight = np.concatenate((leftCollage.asNumpyArray(), filler, rightCollage.asNumpyArray()), axis=1)
        return withImageOnTheRight

    def __resizeImage(self, mainCollage, newHeight, newWidth):
        # type: (Image, int, int) -> Image
        mainCollageNP = cv2.resize(mainCollage.asNumpyArray(), dsize=(newWidth, newHeight),
                                   interpolation=cv2.INTER_CUBIC)
        return Image(mainCollageNP)

    def __getNextFrame(self, thisFrame):
        # type: (Frame) -> Frame
        nextFrameID = self.__seeFloorGeometry.jumpToSeefloorSlice(thisFrame.getFrameID(), +1)
        nextFrame = self.__constructFrame(nextFrameID, thisFrame)
        return nextFrame


    def __getPrevFrame(self, thisFrame):
        # type: (Frame) -> Frame
        prevFrameID = self.__seeFloorGeometry.jumpToSeefloorSlice(thisFrame.getFrameID(), -1)
        prevFrame = self.__constructFrame(prevFrameID, thisFrame)
        return prevFrame

    def __constructFrame(self, newFrameID, thisFrame):
        # type: (int, Frame) -> FrameDecorator

        thisFrameID = thisFrame.getFrameID()
        newFrame = Frame(newFrameID, self.__videoStream)

        driftData = self.__seeFloorGeometry.getDriftData()
        frameDeco = DecoMarkedCrabs(newFrame, driftData, self.__crabsData)

        gridMidPoint = self.__seeFloorGeometry.getRedDotsData().midPoint(thisFrameID)
        drift = self.__seeFloorGeometry.getDriftData().driftBetweenFrames(thisFrameID, newFrameID)
        newPoint = gridMidPoint.translateBy(drift)

        frameDeco2 = DecoGridLines(frameDeco, self.__seeFloorGeometry.getRedDotsData(), newPoint)
        return frameDeco2

    def constructRightCollage(self, thisFrame, nextFrame, prevFrame, mainCollageHeight):
        # type: (Frame, Frame, int) -> Image
        beforeMiddleImage = self.__constructRightPrev(thisFrame, prevFrame)
        afterMiddleImage = self.__constructRightNext(thisFrame, nextFrame)

        rightCollageHeight = beforeMiddleImage.height() + afterMiddleImage.height()
        fillerHeight = (mainCollageHeight - rightCollageHeight) / 2
        fillerImage = Image.empty(fillerHeight, thisFrame.getImgObj().width(), 0).asNumpyArray()

        collageNP = np.concatenate((fillerImage, afterMiddleImage.asNumpyArray(), beforeMiddleImage.asNumpyArray(), fillerImage))
        return Image(collageNP)

    def __constructRightNext(self, thisFrame, nextFrame):
        # type: (Frame, Frame) -> Image
        nextFrameID = int(nextFrame.getFrameID())
        afterMiddleFrameID = int(thisFrame.getFrameID()) + int((nextFrameID - int(thisFrame.getFrameID())) / 2)

        afterMiddleFrame = self.__constructFrame(afterMiddleFrameID, thisFrame)
        afterMiddleImage = afterMiddleFrame.getImgObj()
        afterMiddleImage.drawFrameID(str(afterMiddleFrameID))
        return afterMiddleImage

    def __constructRightPrev(self, thisFrame, prevFrame):
        # type: (Frame, Frame) -> Image
        prevFrameID = int(prevFrame.getFrameID())
        beforeMiddleFrameID = prevFrameID + int((int(thisFrame.getFrameID()) - prevFrameID) / 2)
        beforeMiddleFrame = self.__constructFrame(beforeMiddleFrameID, thisFrame)
        beforeMiddleImage = beforeMiddleFrame.getImgObj()
        beforeMiddleImage.drawFrameID(str(beforeMiddleFrameID))
        return beforeMiddleImage


    def __buildPrevImagePart(self, thisFrame, prevFrame, height):
        # type: (FrameDecorator, FrameDecorator, int) -> Image
        subImage = prevFrame.getImgObj().topPart(height)

        xDrift = self.__xDriftBetweenFrames(thisFrame.getFrameID(), prevFrame.getFrameID())
        shiftedImage = self.__shiftImageHorizontally(subImage, xDrift)

        scalingFactor = self.__calculateImageScalingFactor(thisFrame, prevFrame)
        origHeight = shiftedImage.height()
        newHeight = int(origHeight * scalingFactor)
        origWidth = shiftedImage.width()
        newWidth = int(origWidth * scalingFactor)
        scaledImage = self.__resizeImage(shiftedImage, newHeight, newWidth)

        if scalingFactor <1:
            paddedOnTheBottom = scaledImage.padOnBottom(origHeight - newHeight)
            imageToReturn = paddedOnTheBottom.padSidesToMakeWider((origWidth - newWidth))
        else:
            widthToCutOutLeft=int((newWidth-origWidth)/2)
            areaToCut = Box(Point(widthToCutOutLeft,0), Point(widthToCutOutLeft+origWidth,origHeight))
            imageToReturn = scaledImage.subImage(areaToCut)

        imageToReturn.drawFrameID(prevFrame.getFrameID())
        return imageToReturn

    def __buildNextImagePart(self, thisFrame, nextFrame, height):
        subImage = nextFrame.getImgObj().bottomPart(height)

        xDrift = self.__xDriftBetweenFrames(thisFrame.getFrameID(), nextFrame.getFrameID())
        shiftedImage = self.__shiftImageHorizontally(subImage, xDrift)

        #TODO: Reimplement the section below so that horizontal padding is not necessary. scale image, then cut bottom part.
        scalingFactor = self.__calculateImageScalingFactor(thisFrame, nextFrame)
        origHeight = shiftedImage.height()
        newHeight = int(origHeight * scalingFactor)
        origWidth = shiftedImage.width()
        newWidth = int(origWidth * scalingFactor)
        scaledImage = self.__resizeImage(shiftedImage,newHeight,newWidth)

        if scalingFactor <1:
            paddedOnTop = scaledImage.padOnTop(origHeight-newHeight)
            imageToReturn = paddedOnTop.padSidesToMakeWider((origWidth - newWidth))
        else:
            widthToCutOutLeft = int((newWidth - origWidth) / 2)
            areaToCut = Box(Point(widthToCutOutLeft, newHeight-origHeight), Point(widthToCutOutLeft + origWidth, newHeight))
            imageToReturn = scaledImage.subImage(areaToCut)

        imageToReturn.drawFrameID(nextFrame.getFrameID())
        return imageToReturn

    def __calculateImageScalingFactor(self, thisFrame, otherFrame):
        distanceThis = self.__seeFloorGeometry.getRedDotsData().getDistancePixels(thisFrame.getFrameID())
        distancePrev = self.__seeFloorGeometry.getRedDotsData().getDistancePixels(otherFrame.getFrameID())
        scalingFactor = distanceThis / distancePrev
        return scalingFactor


    def __xDriftBetweenFrames(self, thisFrameID, nextFrameID):
        drift = self.__seeFloorGeometry.getDriftData().driftBetweenFrames(thisFrameID, nextFrameID)
        xDrift = int(drift.x)
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


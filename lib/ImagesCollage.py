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
        collageHeight = thisFrame.getImgObj().height() + neighboursHeight * 2

        prevFrame = self.__getPrevFrame(thisFrame)
        nextFrame = self.__getNextFrame(thisFrame)

        image = thisFrame.getImgObj()
        image.drawFrameID(thisFrame.getFrameID())

        prevSubImage = self.__buildPrevImagePart(thisFrame, prevFrame, neighboursHeight)
        nextSubImage = self.__buildNextImagePart(thisFrame, nextFrame, neighboursHeight)

        print ("prevSubImage hight", prevSubImage.height(), "width", prevSubImage.width())
        print ("nextSubImage hight", nextSubImage.height(), "width", nextSubImage.width())


        mainCollage = self.__glueTogether(image, nextSubImage, prevSubImage)


        #resize leftCollage
        newWidth = mainCollage.width()
        newHeight = mainCollage.height()
        leftCollage = self.__resizeImage(mainCollage, newHeight, newWidth)

        print ("mainCollage hight", newHeight, "width", newWidth)

        rightCollage = self.constructRightCollage(thisFrame, nextFrame, prevFrame, collageHeight)
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

    def __getNextFrame(self, thisFrame):
        # type: (Frame) -> Frame
        nextFrameID = self.__seeFloorGeometry.getNextFrame(thisFrame.getFrameID()) #.jumpToSeefloorSlice(thisFrame.getFrameID(), +1)
        nextFrame = self.__constructFrame(nextFrameID, thisFrame)
        return nextFrame


    def __getPrevFrame(self, thisFrame):
        # type: (Frame) -> Frame
        prevFrameID = self.__seeFloorGeometry.getPrevFrame(thisFrame.getFrameID()) # .jumpToSeefloorSlice(thisFrame.getFrameID(), -1)
        prevFrame = self.__constructFrame(prevFrameID, thisFrame)
        return prevFrame

    def __constructFrame(self, newFrameID, thisFrame):
        # type: (int, Frame) -> FrameDecorator

        thisFrameID = thisFrame.getFrameID()
        newFrame = Frame(newFrameID, self.__videoStream)

        frameDeco = DecoMarkedCrabs(newFrame, self.__seeFloorGeometry)

        gridMidPoint = self.__seeFloorGeometry.getRedDotsData().midPoint(thisFrameID)
        drift = self.__seeFloorGeometry.getDriftData().driftBetweenFrames(thisFrameID, newFrameID)
        newPoint = gridMidPoint.translateBy(drift)

        frameDeco2 = DecoGridLines(frameDeco, self.__seeFloorGeometry.getRedDotsData(), newPoint)
        frameDeco3 = DecoRedDots(frameDeco2,self.__seeFloorGeometry.getRedDotsData())
        return frameDeco3

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
        scalingFactor = self.__calculateImageScalingFactor(thisFrame, prevFrame)

        subImage = prevFrame.getImgObj().topPart(int(height/scalingFactor))
        print ("subImage height", subImage.height(),subImage.width())

        xDrift = self.__xDriftBetweenFrames(thisFrame.getFrameID(), prevFrame.getFrameID())
        #TODO: try first scaling image and then shifting horizontaly. This way we will avoid unnecessary black part on one side

        origHeight = subImage.height()
        newHeight = height
        origWidth = subImage.width()
        newWidth = int(origWidth * scalingFactor)
        scaledImageTmp = self.__resizeImage(subImage, newHeight, newWidth)
        print ("scaledImageTmp height", scaledImageTmp.height(),scaledImageTmp.width())

        scaledImage = self.__shiftImageHorizontally(scaledImageTmp, xDrift)

        print ("scaledImage height", scaledImage.height(),scaledImage.width())

        if scalingFactor <1:
            imageToReturn = scaledImage.padSidesToMakeWider(origWidth - newWidth)
        else:
            widthToCutOutLeft=int((newWidth-origWidth)/2)
            areaToCut = Box(Point(widthToCutOutLeft,0), Point(widthToCutOutLeft+origWidth, height))
            imageToReturn = scaledImage.subImage(areaToCut)
            print ("imageToReturn 10 height", imageToReturn.height(),imageToReturn.width())

        if imageToReturn.height()<height:
            imageToReturn = imageToReturn.padOnBottom(height-imageToReturn.height())

        imageToReturn.drawFrameID(prevFrame.getFrameID())
        return imageToReturn

    def __buildPrevImagePart_works(self, thisFrame, prevFrame, height):
        # type: (FrameDecorator, FrameDecorator, int) -> Image
        scalingFactor = self.__calculateImageScalingFactor(thisFrame, prevFrame)

        subImage = prevFrame.getImgObj().topPart(int(height/scalingFactor))

        xDrift = self.__xDriftBetweenFrames(thisFrame.getFrameID(), prevFrame.getFrameID())
        #TODO: try first scaling image and then shifting horizontaly. This way we will avoid unnecessary black part on one side
        shiftedImage = self.__shiftImageHorizontally(subImage, xDrift)

        origHeight = shiftedImage.height()
        newHeight = int(origHeight * scalingFactor)
        origWidth = shiftedImage.width()
        newWidth = int(origWidth * scalingFactor)
        scaledImage = self.__resizeImage(shiftedImage, newHeight, newWidth)

        if scalingFactor <1:
            imageToReturn = scaledImage.padSidesToMakeWider(origWidth - newWidth)
        else:
            widthToCutOutLeft=int((newWidth-origWidth)/2)
            areaToCut = Box(Point(widthToCutOutLeft,0), Point(widthToCutOutLeft+origWidth, height))
            imageToReturn = scaledImage.subImage(areaToCut)

        if imageToReturn.height()<height:
            imageToReturn = imageToReturn.padOnBottom(height-imageToReturn.height())

        imageToReturn.drawFrameID(prevFrame.getFrameID())
        return imageToReturn


    def __buildNextImagePart(self, thisFrame, nextFrame, height):
        # type: (FrameDecorator, FrameDecorator, int) -> Image

        scalingFactor = self.__calculateImageScalingFactor(thisFrame, nextFrame)
        xDrift = self.__xDriftBetweenFrames(thisFrame.getFrameID(), nextFrame.getFrameID())

        if scalingFactor<1:
            xShiftDueToScaling = Frame.FRAME_WIDTH*(1-scalingFactor)/2
        else:
            xShiftDueToScaling = 0


        xShift = (xShiftDueToScaling+xDrift)

        print ("__buildNextImagePart: scalingFactor", scalingFactor)
        print ("__buildNextImagePart: xDrift", xDrift)
        print ("__buildNextImagePart: xShiftDueToScaling", xShiftDueToScaling)
        print ("__buildNextImagePart: xShift", xShift)
        origWidth = nextFrame.getImgObj().width()
        newWidth = int(origWidth * scalingFactor)


        subImage = nextFrame.getImgObj().bottomPart(int(height/scalingFactor))
        print ("__buildNextImagePart: subImage 10 height", subImage.height(), subImage.width())

        scaledImageTmp = self.__resizeImage(subImage,height,newWidth)
        print ("__buildNextImagePart: scaledImageTmp 10 height", scaledImageTmp.height(), scaledImageTmp.width())

        scaledImage = self.__shiftImageHorizontally(scaledImageTmp, int(xShift))
        print ("__buildNextImagePart: scaledImage 10 height", scaledImage.height(), scaledImage.width())

        if scalingFactor >1:
            print "__buildNextImagePart: scaling factor is above 1"
            widthToCutOutLeft = int((newWidth - origWidth)/2)
            areaToCut = Box(Point(widthToCutOutLeft, scaledImage.height()-height), Point(widthToCutOutLeft + origWidth, height))
            #areaToCut = Box(Point(0, scaledImage.height()-height), Point(origWidth, height))
            imageToReturn = scaledImage.subImage(areaToCut)

        else:
            print "__buildNextImagePart: scaling factor is less then 1"
            # imageToReturn = scaledImage.padSidesToMakeWider(origWidth - newWidth)
            imageToReturn = scaledImage


        print ("__buildNextImagePart: imageToReturn  height", imageToReturn.height(), imageToReturn.width())

        if imageToReturn.width()<origWidth:
            print ("__buildNextImagePart: padding width", origWidth-imageToReturn.width())
            if xShift < 0:
                print ("__buildNextImagePart: padding to the right")
                imageToReturn = imageToReturn.padRight(origWidth-imageToReturn.width())
            else:
                print ("__buildNextImagePart: padding to the left")
                imageToReturn = imageToReturn.padLeft(origWidth-imageToReturn.width())

        if imageToReturn.height()<height:
            print "__buildNextImagePart: padding height"
            imageToReturn = imageToReturn.padOnTop(height-imageToReturn.height())

        imageToReturn.drawFrameID(nextFrame.getFrameID())
        return imageToReturn

    def __buildNextImagePart_works(self, thisFrame, nextFrame, height):
        # type: (FrameDecorator, FrameDecorator, int) -> Image
        scalingFactor = self.__calculateImageScalingFactor(thisFrame, nextFrame)

        subImage = nextFrame.getImgObj().bottomPart(int(height/scalingFactor))

        xDrift = self.__xDriftBetweenFrames(thisFrame.getFrameID(), nextFrame.getFrameID())
        shiftedImage = self.__shiftImageHorizontally(subImage, xDrift)

        origHeight = shiftedImage.height()
        newHeight = int(origHeight * scalingFactor)
        origWidth = shiftedImage.width()
        newWidth = int(origWidth * scalingFactor)
        scaledImage = self.__resizeImage(shiftedImage,newHeight,newWidth)

        if scalingFactor <1:
            imageToReturn = scaledImage.padSidesToMakeWider(origWidth - newWidth)
        else:
            widthToCutOutLeft = int((newWidth - origWidth) / 2)
            areaToCut = Box(Point(widthToCutOutLeft, scaledImage.height()-height), Point(widthToCutOutLeft + origWidth, height))
            imageToReturn = scaledImage.subImage(areaToCut)

        if imageToReturn.height()<height:
            imageToReturn = imageToReturn.padOnTop(height-imageToReturn.height())

        imageToReturn.drawFrameID(nextFrame.getFrameID())
        return imageToReturn

    def __buildPrevImagePart_orig(self, thisFrame, prevFrame, height):
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

    def __buildNextImagePart_orig(self, thisFrame, nextFrame, height):
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


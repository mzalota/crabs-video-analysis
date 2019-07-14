from math import ceil, floor

from lib.Feature import Feature
from lib.Frame import Frame
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from lib.MyTimer import MyTimer
from lib.SeeFloorSection import SeeFloorSection
from lib.common import Box, Point, Vector



class CrabUI:
    def __init__(self, folderStruct, videoStream, driftData, frameID, crabPoint):
        self.__folderStruct = folderStruct
        self.__videoStream = videoStream
        self.__driftData = driftData
        self.__boxSize = 200
        self.__crabFeature = Feature(self.__driftData, frameID, crabPoint, self.__boxSize)

    def showCrabWindow(self):

        crabFeature = self.__crabFeature

        thisFrameID = crabFeature.getInitFrameID()
        middleFrameID = crabFeature.getMiddleGoodFrameID()
        firstFrameID = crabFeature.getFirstGoodFrameID()
        lastFrameID = crabFeature.getLastGoodFrameID()

        crabImageThis = self.__crabImageOnFrame(thisFrameID)
        crabImageFirst = self.__crabImageOnFrame(firstFrameID)
        crabImageLast = self.__crabImageOnFrame(lastFrameID)
        crabImageMiddle = self.__crabImageOnFrame(middleFrameID)

        leftHalfOfImageToShow = crabImageMiddle.concatenateToTheBottom(crabImageFirst) #image from middleFrameID is in top-left corner above image from firstFrameID
        rightHalfOfImageToShow = crabImageLast.concatenateToTheBottom(crabImageThis)  #image from thisFrameID is in bottom-right corner below image from lastFrameID
        imageToShow = leftHalfOfImageToShow.concatenateToTheRight(rightHalfOfImageToShow)

        return self.__showCrabWindow(imageToShow)

        #self.findViewsOfTheSameCrab(boxAroundCrab, thisFrameID)

    def __crabImageOnFrame(self, frameID):

        frameImage = self.__videoStream.readImageObj(frameID)

        box_around_crab_on_that_frame = self.__crabFeature.getCoordinateInFrame(frameID).boxAroundPoint(self.__boxSize)
        crabImage = frameImage.subImage(box_around_crab_on_that_frame)
        crabImage = crabImage.growImage(self.__boxSize, self.__boxSize)

        crabImage.drawFrameID(frameID)
        return crabImage


    def getCrabLocation(self):
        if self.__user_clicked_in_right_half():
            xOffset = -self.__boxSize
        else:
            xOffset = 0

        if self.__user_clicked_in_bottom_half():
            yOffset = -self.__boxSize
        else:
            yOffset = 0

        offsetOfCrabImageFrom0x0 = Vector(xOffset, yOffset)
        return self.__crabCoordinatesOnItsFrame(self.getFrameIDOfCrab(), offsetOfCrabImageFrom0x0)

    def getCrabLocation_bck(self):
        if self.__user_clicked_in_right_half() and self.__user_clicked_in_bottom_half():
            # user marked crab is on "imageThis", which is the bottom right image
            offsetOfCrabImageFrom0x0 = Vector(-self.__boxSize, -self.__boxSize)

        if self.__user_clicked_in_left_half() and self.__user_clicked_in_bottom_half():
            # user marked crab is on "imageFirst", which is bottom left image
            offsetOfCrabImageFrom0x0 = Vector(0, -self.__boxSize)

        if self.__user_clicked_in_right_half() and self.__user_clicked_in_top_half():
            # user marked crab is on "imageLast", which is top right image
            offsetOfCrabImageFrom0x0 = Vector(-self.__boxSize, 0)

        if self.__user_clicked_in_left_half() and self.__user_clicked_in_top_half():
            # user marked crab is on "imageMiddle", which is top left image
            offsetOfCrabImageFrom0x0 = Vector(0, 0)

        #return self.__crabCoordinatesOnItsFrame(self.getFrameIDOfCrab(), offsetOfCrabImageFrom0x0)

    def getFrameIDOfCrab(self):
        if self.__user_clicked_in_right_half() and self.__user_clicked_in_bottom_half():
            # user marked crab is on "imageThis", which is the bottom right image
            return self.__crabFeature.getInitFrameID()

        if self.__user_clicked_in_left_half() and self.__user_clicked_in_bottom_half():
            # user marked crab is on "imageFirst", which is bottom left image
            return self.__crabFeature.getFirstGoodFrameID()

        if self.__user_clicked_in_right_half() and self.__user_clicked_in_top_half():
            # user marked crab is on "imageLast", which is top left image
            return self.__crabFeature.getLastGoodFrameID()

        if self.__user_clicked_in_left_half() and self.__user_clicked_in_top_half():
            # user marked crab is on "imageMiddle", which is top left image
            return self.__crabFeature.getMiddleGoodFrameID()

    def __user_clicked_in_left_half(self):
        return (not self.__user_clicked_in_right_half())

    def __user_clicked_in_right_half(self):
        if(self.__line_marked_by_user.topLeft.x >= self.__boxSize):
            return True
        else:
            return False

    def __user_clicked_in_top_half(self):
        return (not self.__user_clicked_in_bottom_half())

    def __user_clicked_in_bottom_half(self):
        if self.__line_marked_by_user.topLeft.y >= self.__boxSize:
            return True
        else:
            return False

    def __showCrabWindow(self, imageToShow):

        crabWin = ImageWindow.createWindow("crabImage", Box(Point(0, 0), Point(800, 800)))

        crabWin.showWindowAndWaitForTwoClicks(imageToShow.asNumpyArray())
        crabWin.closeWindow()

        if crabWin.userClickedMouseTwice():
            self.__line_marked_by_user = crabWin.featureBox
            return True
        else:
            return False

    def __crabCoordinatesOnItsFrame(self, frameID, offsetOfCrabImageOnCrabWindow):

        boxAroundCrabOnItsFrame = self.__crabFeature.getCoordinateInFrame(frameID).boxAroundPoint(self.__boxSize)
        lineNormalizedTo0x0 = self.__line_marked_by_user.translateBy(offsetOfCrabImageOnCrabWindow)
        lineCoordinatesOnItsFrame = lineNormalizedTo0x0.translateCoordinateToOuter(boxAroundCrabOnItsFrame.topLeft)
        return  lineCoordinatesOnItsFrame


    def saveCrabToFile(self, crabOnSeeFloor, frameID):
        crabImage1 = crabOnSeeFloor.getImageOnFrame(frameID)
        frameNumberString = str(frameID).zfill(6)
        imageFileName = "crab" + frameNumberString + ".jpg"
        imageFilePath = self.__folderStruct.getFramesDirpath() + "/" + imageFileName
        crabImage1.writeToFile(imageFilePath)


    def findViewsOfTheSameCrab(self, boxAroundCrab, frameID):
        frame = Frame(frameID, self.__videoStream)
        crabOnSeeFloor = SeeFloorSection(frame, boxAroundCrab)
        crabOnSeeFloor.setThreshold(0.8)
        crabOnSeeFloor.findInAllFrames()
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID())
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 1)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 2)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 3)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 4)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 5)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 6)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 7)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 8)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 9)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 10)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 11)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 12)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 13)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 14)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 15)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 16)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 17)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 18)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 19)
        self.saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 20)
        crabOnSeeFloor.showSubImage()
        #crabOnSeeFloor.closeWindow()

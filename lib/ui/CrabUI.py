from lib.data.CrabsData import CrabsData
from lib.Feature import Feature
from lib.ImageWindow import ImageWindow
from lib.common import Box, Point, Vector


class CrabUI:
    def __init__(self, crabsData, videoStream, driftData, frameID, crabPoint):
        self.__videoStream = videoStream
        self.__driftData = driftData
        self.__crabsData = crabsData
        self.__boxSize = 300
        # self.__boxSize = 200
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

        lineWasSelected =  self.__showCrabWindow(imageToShow)
        if lineWasSelected:
            self.__save_to_file()

        return lineWasSelected
        #self.findViewsOfTheSameCrab(boxAroundCrab, thisFrameID)

    def __save_to_file(self):
        crabOnFrameID = self.getFrameIDOfCrab()
        crabBox = self.getCrabLocation()

        appended_row = self.__crabsData.add_crab_data(crabOnFrameID, crabBox)
        print ("writing crab to file", appended_row)

    def __crabImageOnFrame(self, frameID):

        frameImage = self.__videoStream.readImageObj(frameID)

        box_around_crab_on_that_frame = self.__crabFeature.getCoordinateInFrame(frameID).boxAroundPoint(self.__boxSize)
        crabImage = frameImage.subImage(box_around_crab_on_that_frame)
        crabImage = crabImage.growByPaddingBottomAndRight(self.__boxSize, self.__boxSize)

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


    #def saveCrabToFile(self, crabOnSeeFloor, frameID):
    #    crabImage1 = crabOnSeeFloor.getImageOnFrame(frameID)
    #    frameNumberString = str(frameID).zfill(6)
    #    imageFileName = "crab" + frameNumberString + ".jpg"
    #    imageFilePath = self.__folderStruct.getFramesDirpath() + "/" + imageFileName
    #    crabImage1.writeToFile(imageFilePath)

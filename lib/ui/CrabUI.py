from lib.infra.FolderStructure import FolderStructure
from lib.VideoStream import VideoStream
from lib.seefloor import SeeFloor
from lib.data.CrabsData import CrabsData
from lib.Feature import Feature
from lib.ui.ImageWindow import ImageWindow
from lib.model.Box import Box
from lib.model.Vector import Vector
from lib.model.Point import Point
from lib.model.Crab import Crab


class CrabUI:
    def __init__(self,
                 crabsData: CrabsData,
                 videoStream: VideoStream,
                 seeFloor: SeeFloor,
                 folderStruct: FolderStructure,
                 frameID: int,
                 crabPoint: Point):
        self.__videoStream = videoStream
        self.__crabsData = crabsData
        self.__folderStruct = folderStruct
        self.__boxSize = 300
        self.__crabFeature = Feature(seeFloor, frameID, crabPoint, self.__boxSize)

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
        crabOnFrameID = self.__getFrameIDOfCrab()
        crabBox = self.__getCrabLocation()
        crab = Crab(crabOnFrameID, crabBox.topLeft, crabBox.bottomRight)

        appended_row = self.__crabsData.add_crab_entry(crab)
        print("writing crab to file", appended_row)

        self.__crabsData.save_file(self.__folderStruct)

    def __crabImageOnFrame(self, frameID):

        frameImage = self.__videoStream.read_image_obj(frameID)

        point = self.__crabFeature.getCoordinateInFrame(frameID)
        box_around_crab_on_that_frame = Box.boxAroundPoint(point, self.__boxSize)
        crabImage = frameImage.subImage(box_around_crab_on_that_frame)
        crabImage = crabImage.growByPaddingBottomAndRight(self.__boxSize, self.__boxSize)

        crabImage.drawFrameID(frameID)
        return crabImage

    def __getCrabLocation(self) -> Box:
        if self.__user_clicked_in_right_half():
            xOffset = -self.__boxSize
        else:
            xOffset = 0

        if self.__user_clicked_in_bottom_half():
            yOffset = -self.__boxSize
        else:
            yOffset = 0

        offsetOfCrabImageFrom0x0 = Vector(xOffset, yOffset)
        return self.__crabCoordinatesOnItsFrame(self.__getFrameIDOfCrab(), offsetOfCrabImageFrom0x0)

    def __getFrameIDOfCrab(self):
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

    def __crabCoordinatesOnItsFrame(self, frameID, offsetOfCrabImageOnCrabWindow) -> Box:

        point = self.__crabFeature.getCoordinateInFrame(frameID)
        boxAroundCrabOnItsFrame = Box.boxAroundPoint(point, self.__boxSize)
        lineNormalizedTo0x0 = self.__line_marked_by_user.translateBy(offsetOfCrabImageOnCrabWindow)
        lineCoordinatesOnItsFrame = lineNormalizedTo0x0.translateCoordinateToOuter(boxAroundCrabOnItsFrame.topLeft)
        return  lineCoordinatesOnItsFrame


    #def saveCrabToFile(self, crabOnSeeFloor, frameID):
    #    crabImage1 = crabOnSeeFloor.getImageOnFrame(frameID)
    #    frameNumberString = str(frameID).zfill(6)
    #    imageFileName = "crab" + frameNumberString + ".jpg"
    #    imageFilePath = self.__folderStruct.getFramesDirpath() + "/" + imageFileName
    #    crabImage1.writeToFile(imageFilePath)

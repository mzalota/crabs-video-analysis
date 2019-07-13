from math import ceil, floor

from lib.Feature import Feature
from lib.Frame import Frame
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from lib.SeeFloorSection import SeeFloorSection
from lib.common import Box, Point, Vector

class CrabUI:
    def __init__(self, folderStruct, videoStream, driftData):
        self.__folderStruct = folderStruct
        self.__videoStream = videoStream
        self.__driftData = driftData

    def getCrabWidth(self, crabPoint, frameID):

        crabFeature = Feature(self.__driftData, frameID, crabPoint)
        firstFrameID, lastFrameID = crabFeature.firstAndLastGoodCrabImages(200)

        if firstFrameID == lastFrameID:
            #The crab is not properly visible on any of the frames. pick some "good enough" frames
            middleFrameID = firstFrameID
            firstFrameID = int(ceil(middleFrameID - (middleFrameID - crabFeature.getFirstFrameID() ) / 2))
            lastFrameID = int(ceil(crabFeature.getLastFrameID() - (crabFeature.getLastFrameID() - middleFrameID) / 2))
        else:
            middleFrameID = int(ceil(lastFrameID - (lastFrameID - firstFrameID) / 2))

        boxAroundCrabThis = self.__boxAroundCrabOnItsFrame(crabFeature, frameID)
        boxAroundCrabFirst = self.__boxAroundCrabOnItsFrame(crabFeature, firstFrameID)
        boxAroundCrabLast = self.__boxAroundCrabOnItsFrame(crabFeature, lastFrameID)
        boxAroundCrabMiddle = self.__boxAroundCrabOnItsFrame(crabFeature, middleFrameID)

        crabImageThis = self.__crabImageOnFrame(boxAroundCrabThis, frameID)
        crabImageFirst = self.__crabImageOnFrame(boxAroundCrabFirst, firstFrameID)
        crabImageLast = self.__crabImageOnFrame(boxAroundCrabLast, lastFrameID)
        crabImageMiddle = self.__crabImageOnFrame(boxAroundCrabMiddle, middleFrameID)
        markedLine = self.__showCrabWindow(crabImageFirst, crabImageLast, crabImageMiddle, crabImageThis)

        #self.findViewsOfTheSameCrab(boxAroundCrab, frameID)

        if markedLine.topLeft.x >=200 and markedLine.topLeft.y>=200:
            #user marked crab is on "imageThis", which is the bottom right image
            offsetOfCrabImageFrom0x0 = Vector(-200, -200)
            crabOnItsFrame = self.__crabCoordinatesOnItsFrame(boxAroundCrabThis, markedLine, offsetOfCrabImageFrom0x0)
            frameIDOfCrab = frameID

        if markedLine.topLeft.x <200 and markedLine.topLeft.y>=200:
            #user marked crab is on "imageFirst", which is bottom left image
            offsetOfCrabImageFrom0x0 = Vector(0, -200)
            crabOnItsFrame = self.__crabCoordinatesOnItsFrame(boxAroundCrabFirst, markedLine, offsetOfCrabImageFrom0x0)
            frameIDOfCrab = firstFrameID

        if markedLine.topLeft.x >=200 and markedLine.topLeft.y<200:
            #user marked crab is on "imageLast", which is top right image
            offsetOfCrabImageFrom0x0 = Vector(-200, 0)
            crabOnItsFrame = self.__crabCoordinatesOnItsFrame(boxAroundCrabLast, markedLine, offsetOfCrabImageFrom0x0)
            frameIDOfCrab = lastFrameID

        if markedLine.topLeft.x <200 and markedLine.topLeft.y<200:
            #user marked crab is on "imageMiddle", which is top left image
            offsetOfCrabImageFrom0x0 = Vector(0, 0)
            crabOnItsFrame = self.__crabCoordinatesOnItsFrame(boxAroundCrabMiddle, markedLine, offsetOfCrabImageFrom0x0)
            frameIDOfCrab = middleFrameID

        return frameIDOfCrab, crabOnItsFrame

    def __showCrabWindow(self, crabImageFirst, crabImageLast, crabImageMiddle, crabImageThis):
        leftImageToShow = crabImageMiddle.concatenateToTheBottom(crabImageFirst)
        rightImageToShow = crabImageLast.concatenateToTheBottom(crabImageThis)
        imageToShow = leftImageToShow.concatenateToTheRight(rightImageToShow)

        crabWin = ImageWindow.createWindow("crabImage", Box(Point(0, 0), Point(800, 800)))
        crabWin.showWindowAndWaitForTwoClicks(imageToShow.asNumpyArray())
        crabWin.closeWindow()

        markedLine = crabWin.featureBox
        return markedLine

    def __crabCoordinatesOnItsFrame(self, boxAroundCrabOnItsFrame, lineMarkedByUser, offsetOfCrabImageOnCrabWindow):
        lineNormalizedTo0x0 = lineMarkedByUser.translateBy(offsetOfCrabImageOnCrabWindow)
        lineCoordinatesOnItsFrame = lineNormalizedTo0x0.translateCoordinateToOuter(boxAroundCrabOnItsFrame.topLeft)
        return  lineCoordinatesOnItsFrame

    def __crabImageOnFrame(self, boxAroundCrab, frameID):
        frameImage = self.__videoStream.readImageObj(frameID)
        crabImage = frameImage.subImage(boxAroundCrab)
        crabImage = crabImage.growImage(200, 200)
        crabImage.drawFrameID(frameID)
        return crabImage

    def __boxAroundCrabOnItsFrame(self, crabFeature, frameID):
        crabPointOnItsFrame = crabFeature.getCoordinateInFrame(frameID)
        #drift = self.__driftData.driftBetweenFrames(frameID, firstFrameID)
        #crabPointOnItsFrame = crabPoint.translateBy(drift)

        boxAroundCrab = crabPointOnItsFrame.boxAroundPoint(200)
        return boxAroundCrab

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

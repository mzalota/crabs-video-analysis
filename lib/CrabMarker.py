from math import ceil, floor

from lib.DriftData import DriftData
from lib.Feature import Feature
from lib.Frame import Frame
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from lib.SeeFloorSection import SeeFloorSection
from lib.common import Box, Point, Vector


class UserWantsToQuitException(Exception):
    pass

class CrabMarker:
    def __init__(self,imageWin, folderStruct, videoStream):
        self.__imageWin = imageWin
        self.__folderStruct = folderStruct
        self.__videoStream = videoStream
        self.__driftData = DriftData.createFromFile(folderStruct.getDriftsFilepath())


    def processImage(self, image, frameID):
        origImage = image.copy()
        foundCrabs = list()
        mustExit = False
        while not mustExit:
            keyPressed = self.__imageWin.showWindowAndWaitForClick(image)
            #print ("pressed button", keyPressed)

            if keyPressed == ord("n") or keyPressed == ImageWindow.KEY_ARROW_DOWN or keyPressed == ImageWindow.KEY_ARROW_RIGHT or keyPressed == ImageWindow.KEY_SPACE:
                # process next frame
                mustExit = True
            elif keyPressed == ord("r"):
                # print "Pressed R button" - reset. Remove all marked crabs
                foundCrabs = list()
                image = origImage.copy()
            elif keyPressed == ord("q"):
                # print "Pressed Q button" quit
                message = "User pressed Q button"
                raise UserWantsToQuitException(message)
            else:
                crabBox = self.__getCrabWidth(image, frameID)
                foundCrabs.append(crabBox)
            # print("foundCrab", str(crabBox), crabBox.diagonal(), str(crabBox.centerPoint()))

        return foundCrabs

    def __getCrabWidth(self, image, frameID):
        mainImage = Image(image)
        crabPoint = self.__imageWin.featureCoordiate

        crabFeature = Feature(self.__driftData, frameID, crabPoint)
        firstFrameID, lastFrameID = crabFeature.firstAndLastGoodCrabImages(200)
        #print ("determened frames: first, last", firstFrameID, lastFrameID)

        if firstFrameID == lastFrameID:
            middleFrameID = firstFrameID
            firstFrameID = int(ceil(middleFrameID - (middleFrameID - crabFeature.getFirstFrameID() ) / 2))
            lastFrameID = int(ceil(crabFeature.getLastFrameID() - (crabFeature.getLastFrameID() - middleFrameID) / 2))
        else:
            middleFrameID = int(ceil(lastFrameID - (lastFrameID - firstFrameID) / 2))

        #print ("frames used for display: first, middle, last", firstFrameID, middleFrameID, lastFrameID)

        crabImageFirst, boxAroundCrabFirst = self.showCrab(crabPoint, firstFrameID, frameID)
        crabImageLast, boxAroundCrabLast = self.showCrab(crabPoint, lastFrameID, frameID)
        crabImageMiddle, boxAroundCrabMiddle = self.showCrab(crabPoint, middleFrameID, frameID)

        boxAroundCrab = crabPoint.boxAroundPoint(200)
        crabImage = mainImage.subImage(boxAroundCrab)
        crabImage.drawFrameID(frameID)


        #self.findViewsOfTheSameCrab(boxAroundCrab, frameID)

        leftImageToShow = crabImageMiddle.concatenateToTheBottom(crabImageFirst)
        rightImageToShow = crabImageLast.concatenateToTheBottom(crabImage)
        imgToShow = leftImageToShow.concatenateToTheRight(rightImageToShow)

        crabWin = ImageWindow.createWindow("crabImage", Box(Point(0, 0), Point(800, 800)))
        crabWin.showWindowAndWaitForTwoClicks(imgToShow.asNumpyArray())
        crabWin.closeWindow()

        markedLine = crabWin.featureBox
        print ("markedLine", str(markedLine))

        if markedLine.topLeft.x >=200 and markedLine.topLeft.y>=200:
            #user marked crab is on "imageThis"
            crabThisOnMainWindow = markedLine.translateCoordinateToOuter(boxAroundCrab.topLeft)
            crabTopLeft = crabThisOnMainWindow.topLeft.translateBy(Vector(-200,-200))
            crabBottomRight = crabThisOnMainWindow.bottomRight.translateBy(Vector(-200,-200))
            crabOnMainWindow = Box(crabTopLeft, crabBottomRight)

        if markedLine.topLeft.x <200 and markedLine.topLeft.y<200:
            #user marked crab is on "imageMiddle"
            crabMiddleOnMainWindow = markedLine.translateCoordinateToOuter(boxAroundCrabMiddle.topLeft)
            drift = self.__driftData.driftBetweenFrames(middleFrameID, frameID)

            crabTopLeft = crabMiddleOnMainWindow.topLeft.translateBy(drift)
            crabBottomRight = crabMiddleOnMainWindow.bottomRight.translateBy(drift)

            print ("drift, crabMiddleOnMainWindow", frameID, middleFrameID, str(drift), str(crabMiddleOnMainWindow), str(crabTopLeft), str(crabBottomRight))
            crabOnMainWindow = Box(crabTopLeft, crabBottomRight)

        print ("crabOnMainWindow", str(crabOnMainWindow))


        mainImage.drawLine(crabOnMainWindow.topLeft, crabOnMainWindow.bottomRight)

        return crabOnMainWindow

    def showCrab(self, crabPoint, firstFrameID, frameID):
        firstFrameImage = self.__videoStream.readImageObj(firstFrameID)
        firstFrameImage.drawFrameID(firstFrameID)

        drift = self.__driftData.driftBetweenFrames(frameID, firstFrameID)
        crabPointFirst = crabPoint.translateBy(drift)
        boxAroundCrab = crabPointFirst.boxAroundPoint(200)
        crabImage = firstFrameImage.subImage(boxAroundCrab)
        crabImage = crabImage.growImage(200, 200)
        crabImage.drawFrameID(firstFrameID)

        return crabImage, boxAroundCrab

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

from math import ceil, floor

from lib.DriftData import DriftData
from lib.Feature import Feature
from lib.Frame import Frame
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from lib.SeeFloorSection import SeeFloorSection
from lib.common import Box, Point


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
        middleFrameID = int(ceil(lastFrameID - (lastFrameID - firstFrameID) / 2))

        print ("frames: first, middle, last", firstFrameID, middleFrameID, lastFrameID)

        crabWin2, crabImage2 = self.showCrab(crabPoint, firstFrameID, frameID)
        crabWin3, crabImage3 = self.showCrab(crabPoint, lastFrameID, frameID)
        crabWin4, crabImage4 = self.showCrab(crabPoint, middleFrameID, frameID)

        boxAroundCrab = crabPoint.boxAroundPoint(200)
        crabImage = mainImage.subImage(boxAroundCrab)
        crabImage.drawFrameID(frameID)
        #self.findViewsOfTheSameCrab(boxAroundCrab, frameID)

        leftImageToShow = crabImage4.concatenateToTheBottom(crabImage2)
        rightImageToShow = crabImage3.concatenateToTheBottom(crabImage)
        imgToShow = leftImageToShow.concatenateToTheRight(rightImageToShow)

        #topImageToShow = crabImage.concatenateToTheRight(crabImage2)
        #bottomImageToShow = crabImage3.concatenateToTheRight(crabImage4)
        #imgToShow = topImageToShow.concatenateToTheBottom(bottomImageToShow)

        crabWin = ImageWindow.createWindow("crabImage", Box(Point(0, 0), Point(600, 600)))
        crabWin.showWindowAndWaitForTwoClicks(imgToShow.asNumpyArray())
        crabWin.closeWindow()

        crabWin2.closeWindow()
        crabWin3.closeWindow()
        crabWin4.closeWindow()
        #frame2Win.closeWindow()
        #frame3Win.closeWindow()
        #frame4Win.closeWindow()

        crabOnMainWindow = crabWin.featureBox.translateCoordinateToOuter(boxAroundCrab.topLeft)
        mainImage.drawLine(crabOnMainWindow.topLeft, crabOnMainWindow.bottomRight)

        return crabOnMainWindow

    def showCrab(self, crabPoint, firstFrameID, frameID):
        firstFrameImage = self.__videoStream.readImageObj(firstFrameID)
        firstFrameImage.drawFrameID(firstFrameID)

        drift = self.__driftData.driftBetweenFrames(frameID, firstFrameID)
        crabPointFirst = crabPoint.translateBy(drift)
        boxAroundCrabFirst = crabPointFirst.boxAroundPoint(200)
        crabImage2 = firstFrameImage.subImage(boxAroundCrabFirst)
        crabImage2.drawFrameID(firstFrameID)
        print ("h w", crabImage2.height(), crabImage2.width())
        print ("details", str(boxAroundCrabFirst), str(crabPointFirst), str(crabPoint), str(drift))
        # crabWin2 = ImageWindow.createWindow("crabImage2", Box(Point(0, 0), Point(boxAroundCrabFirst.width(), boxAroundCrabFirst.hight())))
        crabWin2 = ImageWindow.createWindow("crabImage"+str(firstFrameID), Box(Point(0, 0), Point(600, 600)))
        nnnp = crabImage2.asNumpyArray()
        # print ("size" , nnnp.size())
        # print (nnnp)
        crabWin2.showWindow(nnnp)
        #frame2Win = ImageWindow.createWindow("wholeImage"+str(firstFrameID), Box(Point(0, 0),Point(960, 540)))
        #frame2Win.showWindow(firstFrameImage.asNumpyArray())
        return crabWin2, crabImage2 #, frame2Win

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

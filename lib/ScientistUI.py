from lib.CrabUI import CrabUI
from lib.DriftData import DriftData
from lib.Image import Image
from lib.ImageWindow import ImageWindow


class UserWantsToQuitException(Exception):
    pass

class ScientistUI:
    def __init__(self, imageWin, folderStruct, videoStream, driftData):
        self.__imageWin = imageWin
        self.__folderStruct = folderStruct
        self.__videoStream = videoStream
        self.__driftData = driftData

        self.__crabNumber = 0

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
                crabPoint = self.__imageWin.featureCoordiate

                #self.__crabUI.showCrabWindow(crabPoint, frameID)

                crabUI = CrabUI(self.__folderStruct, self.__videoStream, self.__driftData, frameID, crabPoint)
                lineWasSelected = crabUI.showCrabWindow()

                if lineWasSelected:
                    crabOnFrameID = crabUI.getFrameIDOfCrab()
                    crabBox = crabUI.getCrabLocation()

                    foundCrabs.append((self.__crabNumber, crabOnFrameID, crabBox))

                    #draw an X on where the User clicked.
                    mainImage = Image(image)
                    mainImage.drawCross(crabPoint)

                    #self.__drawLineOnCrab(crabBox, crabOnFrameID, frameID, mainImage)

                    self.__crabNumber += 1

        return foundCrabs

    def __drawLineOnCrab(self, crabBox, crabOnFrameID, frameID, mainImage):
        # draw user-marked line on the main image. but first translate the coordinates to this frame
        drift = self.__driftData.driftBetweenFrames(crabOnFrameID, frameID)
        crabBoxTopLeft = crabBox.topLeft.translateBy(drift)
        crabBoxBottomRight = crabBox.bottomRight.translateBy(drift)
        mainImage.drawLine(crabBoxTopLeft, crabBoxBottomRight)

from lib.DriftData import DriftData
from lib.Image import Image
from lib.ImageWindow import ImageWindow


class UserWantsToQuitException(Exception):
    pass

class ScientistUI:
    def __init__(self, imageWin, crabUI):
        self.__imageWin = imageWin
        self.__crabNumber = 0
        self.__crabUI = crabUI

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
                crabOnFrameID, crabBox = self.__crabUI.getCrabWidth(crabPoint, frameID)

                foundCrabs.append((self.__crabNumber, crabOnFrameID, crabBox))

                #draw an X on where the User clicked.
                mainImage = Image(image)
                mainImage.drawCross(crabPoint)

                self.__crabNumber += 1

        return foundCrabs

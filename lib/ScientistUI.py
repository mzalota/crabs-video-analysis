from lib.CrabUI import CrabUI
from lib.DriftData import DriftData
from lib.Frame import Frame
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from datetime import datetime
import pandas as pd
import cv2
import os

class UserWantsToQuitException(Exception):
    pass

class ScientistUI:
    def __init__(self, imageWin, folderStruct, videoStream, driftData):
        self.__imageWin = imageWin
        self.__folderStruct = folderStruct
        self.__videoStream = videoStream
        self.__driftData = driftData

        columns = ['dir', 'filename', 'crabNumber', 'crabWidthPixels', 'crabLocationX', 'crabLocationY', 'crabWidthLine']
        self.__crabsDF = pd.DataFrame(columns)
        self.__crabNumber = 0

    def processVideo(self,logger):

        filepaths = self.__folderStruct.getFramesFilepaths()

        for filepath in filepaths:
            filename = os.path.basename(filepath)
            if not filename.endswith(".jpg"):
                print("Skipping some non JPG file", filepath)
                continue

            image = cv2.imread(filepath)

            frameID = Frame.deconstructFilename(filename)
            try:
                self.processImage(image, frameID, logger)
            except UserWantsToQuitException as error:
                # print repr(error)
                print("User requested to quit on frame: " + str(frameID))
                break




        logger.closeFile()
        # crabsDF.to_csv(folderStruct.getCrabsFilepath(), sep='\t')

    def processImage(self, image, frameID, logger):
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

        self.writeCrabsInfoToFile(foundCrabs, logger)
        return foundCrabs

    def __drawLineOnCrab(self, crabBox, crabOnFrameID, frameID, mainImage):
        # draw user-marked line on the main image. but first translate the coordinates to this frame
        drift = self.__driftData.driftBetweenFrames(crabOnFrameID, frameID)
        crabBoxTopLeft = crabBox.topLeft.translateBy(drift)
        crabBoxBottomRight = crabBox.bottomRight.translateBy(drift)
        mainImage.drawLine(crabBoxTopLeft, crabBoxBottomRight)

    def writeCrabsInfoToFile(self, foundCrabs, logger, ):
        crabsDF = self.__crabsDF
        framesDir = self.__folderStruct.getFramesDirpath()
        filename = "blabla-filename.maxim"

        for crabTuple in foundCrabs:
            crabNumber = crabTuple[0]
            frameID = crabTuple[1]
            crabCoordinate = crabTuple[2]
            crabsDF = crabsDF.append(
                {'dir': framesDir, 'filename': filename, 'frameID': frameID, 'crabNumber': crabNumber,
                 'crabWidthPixels': crabCoordinate.diagonal(),
                 'crabLocationX': crabCoordinate.centerPoint().x, 'crabLocationY': crabCoordinate.centerPoint().y, 'crabWidthLine': crabCoordinate},
                ignore_index=True)

            row = list()
            row.append(framesDir)
            row.append(filename)
            row.append(frameID)
            row.append(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
            row.append(crabNumber)
            row.append(crabCoordinate.diagonal())
            row.append(crabCoordinate.centerPoint().x)
            row.append(crabCoordinate.centerPoint().y)
            row.append(str(crabCoordinate.centerPoint()))
            row.append(str(crabCoordinate))

            print ("row", row)

            logger.writeToFile(row)
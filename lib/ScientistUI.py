from lib.CrabUI import CrabUI
from lib.DriftData import DriftData
from lib.Frame import Frame
from lib.FramesStitcher import FramesStitcher
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from datetime import datetime
import pandas as pd
import cv2
import os
import traceback


class UserWantsToQuitException(Exception):
    pass

class ScientistUI:
    def __init__(self, imageWin, folderStruct, videoStream, driftData):
        # type: (ImageWindow, FolderStructure, VideoStream, DriftData) -> ScientistUI
        self.__imageWin = imageWin
        self.__folderStruct = folderStruct
        self.__videoStream = videoStream
        self.__driftData = driftData

        column_names = ['dir', 'filename', 'frameID', 'createdOn', 'crabNumber', "crabWidthPixels", "crabLocationX",
                        'crabLocationY',
                        'crabCoordinatePoint', 'cranbCoordinateBox']

        self.__crabsDF = pd.read_csv(folderStruct.getCrabsFilepath(), delimiter="\t", na_values="(null)", names=column_names)  # 24 errors


        #columns = ['dir', 'filename', 'crabNumber', 'crabWidthPixels', 'crabLocationX', 'crabLocationY', 'crabWidthLine']
        #self.__crabsDF = pd.DataFrame(columns)

        self.__crabNumber = 0

    def processVideo(self,logger):

        if False:
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

        frame_id = self.__driftData.minFrameID()
        while True:
            print ("processing frame ID", int(frame_id))

            try:
                frame = Frame(frame_id, self.__videoStream)
                #image = frame.getImage()
                keyPressed = self.processImage(frame.getImgObj(), frame_id, logger)

            except UserWantsToQuitException as error:
                print repr(error)
                print("User requested to quit on frame: ", str(frame_id))
                break

            except Exception as error:
                print ("Failed to read next frame from video: ",frame_id )
                print(repr(error))
                traceback.print_exc()
                break

            frame_id = self.__determine_next_frame(frame_id, keyPressed)

        logger.closeFile()
        # crabsDF.to_csv(folderStruct.getCrabsFilepath(), sep='\t')

    def __determine_next_frame(self, frame_id, keyPressed):
        if keyPressed == ImageWindow.KEY_ARROW_DOWN or keyPressed == ImageWindow.KEY_SPACE or keyPressed == ord("n"):
            # show next frame
            pixels_to_jump = FramesStitcher.FRAME_HEIGHT

        elif keyPressed == ImageWindow.KEY_ARROW_UP:
            # show previous frame
            pixels_to_jump = -FramesStitcher.FRAME_HEIGHT

        elif keyPressed == ImageWindow.KEY_ARROW_RIGHT:
            # scroll 1/4 of a frame forward
            pixels_to_jump = int(FramesStitcher.FRAME_HEIGHT / 4)

        elif keyPressed == ImageWindow.KEY_ARROW_LEFT:
            # scroll 1/4 of a frame backward
            pixels_to_jump = - int(FramesStitcher.FRAME_HEIGHT / 4)

        elif keyPressed == ImageWindow.KEY_PAGE_DOWN:
            # scroll 1/4 of a frame backward
            pixels_to_jump = FramesStitcher.FRAME_HEIGHT * 10
        elif keyPressed == ImageWindow.KEY_PAGE_UP:
            # scroll 1/4 of a frame backward
            pixels_to_jump = -FramesStitcher.FRAME_HEIGHT * 10

        else:
            print ("Ignoring the fact that user pressed button:", keyPressed)  # , chr(keyPressed))
            return frame_id

        new_frame_id = self.__driftData.getNextFrame(pixels_to_jump, frame_id)

        if new_frame_id < self.__driftData.minFrameID():
            new_frame_id = self.__driftData.minFrameID()

        if new_frame_id >= self.__driftData.maxFrameID():
            new_frame_id = self.__driftData.maxFrameID()

        return int(new_frame_id)

    def processImage(self, mainImage, frameID, logger):
        origImage = mainImage.asNumpyArray().copy()
        foundCrabs = list()
        mustExit = False
        while not mustExit:
            #mainImage = Image(image)
            mainImage.drawFrameID(int(frameID))
            keyPressed = self.__imageWin.showWindowAndWaitForClick(mainImage.asNumpyArray())
            #print ("pressed button", keyPressed, chr(ImageWindow.KEY_MOUSE_CLICK_EVENT), ImageWindow.KEY_MOUSE_CLICK_EVENT)

            if keyPressed == ord("r"):
                # print "Pressed R button" - reset. Remove all marked crabs
                foundCrabs = list()
                mainImage = Image(origImage.copy())
            elif keyPressed == ord("q"):
                # print "Pressed Q button"
                message = "User pressed Q button"
                raise UserWantsToQuitException(message)
            elif keyPressed == ImageWindow.KEY_MOUSE_CLICK_EVENT:
                crabPoint = self.__imageWin.featureCoordiate

                #self.__crabUI.showCrabWindow(crabPoint, frameID)

                crabUI = CrabUI(self.__folderStruct, self.__videoStream, self.__driftData, frameID, crabPoint)
                lineWasSelected = crabUI.showCrabWindow()

                if lineWasSelected:
                    crabOnFrameID = crabUI.getFrameIDOfCrab()
                    crabBox = crabUI.getCrabLocation()

                    foundCrabs.append((self.__crabNumber, crabOnFrameID, crabBox))

                    #draw an X on where the User clicked.
                    mainImage.drawCross(crabPoint)

                    #self.__drawLineOnCrab(crabBox, crabOnFrameID, frameID, mainImage)
                    #self.__manualDF.to_csv(filepath, sep='\t', index=False)

                    self.__crabNumber += 1
            else:
                #print ("Ignoring the fact that user pressed button:", keyPressed)#, chr(keyPressed))
                mustExit = True

        self.writeCrabsInfoToFile(foundCrabs, logger)

        return keyPressed

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
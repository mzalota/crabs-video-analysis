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
                        'crabLocationY', 'crabCoordinatePoint', 'cranbCoordinateBox']

        self.__crabsDF = pd.read_csv(folderStruct.getCrabsFilepath(), delimiter="\t", na_values="(null)",header=None, names=column_names)  # 24 errors

        #drop header row if it exists
        if (self.__crabsDF.iloc[0][0] == 'dir'):
            self.__crabsDF = self.__crabsDF[1:].reset_index(drop=True)


        self.__crabNumber = 0

    def processVideo(self):

        frame_id = self.__driftData.minFrameID()
        while True:
            print ("processing frame ID", int(frame_id))

            try:
                frame = Frame(frame_id, self.__videoStream)
                #image = frame.getImage()
                keyPressed = self.processImage(frame.getImgObj(), frame_id)

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


    def __determine_next_frame(self, frame_id, keyPressed):

        if keyPressed == ImageWindow.KEY_ARROW_RIGHT:
            # scroll 50 frames forward
            new_frame_id = frame_id+50
            return new_frame_id

        if keyPressed == ImageWindow.KEY_ARROW_LEFT:
            # scroll 50 frames backward
            new_frame_id = frame_id-50
            return new_frame_id

        if keyPressed == ImageWindow.KEY_END:
            # Go to the very last frame
            return self.__driftData.maxFrameID()

        if keyPressed == ImageWindow.KEY_HOME:
            # Go to the very first frame
            return self.__driftData.minFrameID()


        if keyPressed == ImageWindow.KEY_ARROW_DOWN or keyPressed == ImageWindow.KEY_SPACE or keyPressed == ord("n"):
            # show next frame
            pixels_to_jump = FramesStitcher.FRAME_HEIGHT
        elif keyPressed == ImageWindow.KEY_ARROW_UP:
            # show previous frame
            pixels_to_jump = -FramesStitcher.FRAME_HEIGHT
        elif keyPressed == ImageWindow.KEY_PAGE_DOWN:
            #Jump 10 screens forward
            pixels_to_jump = FramesStitcher.FRAME_HEIGHT * 10
        elif keyPressed == ImageWindow.KEY_PAGE_UP:
            #Jump 10 screens backward
            pixels_to_jump = -(FramesStitcher.FRAME_HEIGHT * 10)
        else:
            print ("Ignoring the fact that user pressed button:", keyPressed)  # , chr(keyPressed))
            return frame_id

        new_frame_id = self.__driftData.getNextFrame(pixels_to_jump, frame_id)

        if new_frame_id < self.__driftData.minFrameID():
            new_frame_id = self.__driftData.minFrameID()

        if new_frame_id >= self.__driftData.maxFrameID():
            new_frame_id = self.__driftData.maxFrameID()

        return int(new_frame_id)

    def processImage(self, mainImage, frameID):
        origImage = mainImage.asNumpyArray().copy()
        mustExit = False
        while not mustExit:
            mainImage.drawFrameID(int(frameID))
            keyPressed = self.__imageWin.showWindowAndWaitForClick(mainImage.asNumpyArray())
            #print ("pressed button", keyPressed, chr(ImageWindow.KEY_MOUSE_CLICK_EVENT), ImageWindow.KEY_MOUSE_CLICK_EVENT)

            if keyPressed == ord("r"):
                # print "Pressed R button" - reset. Remove all marked crabs
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

                    #draw an X on where the User clicked.
                    mainImage.drawCross(crabPoint)

                    #self.__drawLineOnCrab(crabBox, crabOnFrameID, frameID, mainImage)
                    self.__add_crab_to_DF(crabOnFrameID, crabBox)
                    self.__crabsDF.to_csv(self.__folderStruct.getCrabsFilepath(), sep='\t', index=False)
            else:
                #print ("Ignoring the fact that user pressed button:", keyPressed)#, chr(keyPressed))
                mustExit = True

        return keyPressed

    def __drawLineOnCrab(self, crabBox, crabOnFrameID, frameID, mainImage):
        # draw user-marked line on the main image. but first translate the coordinates to this frame
        drift = self.__driftData.driftBetweenFrames(crabOnFrameID, frameID)
        crabBoxTopLeft = crabBox.topLeft.translateBy(drift)
        crabBoxBottomRight = crabBox.bottomRight.translateBy(drift)
        mainImage.drawLine(crabBoxTopLeft, crabBoxBottomRight)


    def __add_crab_to_DF(self, frameID, crabCoordinate):
        framesDir = self.__folderStruct.getVideoFilepath()

        row_to_append = {'dir': framesDir,
                         'filename': "blabla.filename",
                         'frameID': frameID,
                         'createdOn': datetime.now().strftime('%Y-%m-%d_%H:%M:%S'),
                         'crabNumber': "0",
                         'crabWidthPixels': crabCoordinate.diagonal(),
                         'crabLocationX': crabCoordinate.centerPoint().x,
                         'crabLocationY': crabCoordinate.centerPoint().y,
                         'crabCoordinatePoint': str(crabCoordinate.centerPoint()),
                         'cranbCoordinateBox': str(crabCoordinate)
                         }

        print ("writing crab to file", row_to_append)
        self.__crabsDF = self.__crabsDF.append( row_to_append, ignore_index=True)

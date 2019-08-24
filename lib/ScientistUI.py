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

    def processVideo(self):

        frame_id = self.__driftData.minFrameID()
        while True:
            print ("processing frame ID", int(frame_id))

            try:
                frame = Frame(frame_id, self.__videoStream)
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

    def processImage(self, mainImage, frame_id):
        mustExit = False
        while not mustExit:

            if frame_id == self.__driftData.minFrameID():
                frame_name = str(int(frame_id))+" (First)"
            elif frame_id == self.__driftData.maxFrameID():
                frame_name = str(int(frame_id))+" (Last)"
            else:
                frame_name = int(frame_id)

            mainImage.drawFrameID(frame_name)
            keyPressed = self.__imageWin.showWindowAndWaitForClick(mainImage.asNumpyArray())
            #print ("pressed button", keyPressed, chr(ImageWindow.KEY_MOUSE_CLICK_EVENT), ImageWindow.KEY_MOUSE_CLICK_EVENT)

            if keyPressed == ord("q"):
                # print "Pressed Q button"
                message = "User pressed Q button"
                raise UserWantsToQuitException(message)

            elif keyPressed == ImageWindow.KEY_MOUSE_CLICK_EVENT:
                crabPoint = self.__imageWin.featureCoordiate

                #self.__crabUI.showCrabWindow(crabPoint, frameID)

                crabUI = CrabUI(self.__folderStruct, self.__videoStream, self.__driftData, frame_id, crabPoint)

                lineWasSelected = crabUI.showCrabWindow()
                if lineWasSelected:
                    #draw an X on where the User clicked.
                    mainImage.drawCross(crabPoint)
                    #self.__drawLineOnCrab(crabBox, crabOnFrameID, frameID, mainImage)

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


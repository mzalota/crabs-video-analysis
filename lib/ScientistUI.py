from lib.CrabUI import CrabUI
from lib.CrabsData import CrabsData
from lib.DriftData import DriftData
from lib.Feature import Feature
from lib.Frame import Frame
from lib.FramesStitcher import FramesStitcher
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from datetime import datetime
import pandas as pd
import cv2
import os
import traceback

from lib.MyTimer import MyTimer
from lib.common import Point


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
            timer = MyTimer()
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
            timer.lap("processVideo")

    def __determine_next_frame(self, frame_id, keyPressed):

        if keyPressed == ImageWindow.KEY_ARROW_DOWN:
            # scroll 50 frames forward
            new_frame_id = frame_id+50
            return new_frame_id

        if keyPressed == ImageWindow.KEY_ARROW_UP:
            # scroll 50 frames backward
            new_frame_id = frame_id-50
            return new_frame_id

        if keyPressed == ImageWindow.KEY_END:
            # Go to the very last frame
            return self.__driftData.maxFrameID()

        if keyPressed == ImageWindow.KEY_HOME:
            # Go to the very first frame
            return self.__driftData.minFrameID()


        if keyPressed == ImageWindow.KEY_ARROW_RIGHT or keyPressed == ImageWindow.KEY_SPACE or keyPressed == ord("n"):
            # show next frame
            pixels_to_jump = FramesStitcher.FRAME_HEIGHT
        elif keyPressed == ImageWindow.KEY_ARROW_LEFT:
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
            markCrabsTimer = MyTimer()

            if frame_id == self.__driftData.minFrameID():
                frame_name = str(int(frame_id))+" (First)"
            elif frame_id == self.__driftData.maxFrameID():
                frame_name = str(int(frame_id))+" (Last)"
            else:
                frame_name = int(frame_id)

            #markCrabsTimer.lap("processImage: step 10")
            mainImage.drawFrameID(frame_name)

            #markCrabsTimer.lap("processImage: step 20")
            self.markCrabsOnImage(mainImage, frame_id)
            markCrabsTimer.lap("markCrabsTimer")

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
                #if lineWasSelected:
                    #draw an X on where the User clicked.
                    #mainImage.drawCross(crabPoint)
                    #self.__drawLineOnCrab(crabBox, crabOnFrameID, frameID, mainImage)

            else:
                #print ("Ignoring the fact that user pressed button:", keyPressed)#, chr(keyPressed))
                mustExit = True


        return keyPressed

    def markCrabsOnImage(self, mainImage, frame_id):
        #crabsOnFrame = list()
        #crabsOnFrame.append(Point(500, 500))
        #crabsOnFrame.append(Point(600, 900))

        nextFrame = self.__driftData.getNextFrame(FramesStitcher.FRAME_HEIGHT,frame_id)
        prevFrame = self.__driftData.getNextFrame(-FramesStitcher.FRAME_HEIGHT,frame_id)

        print("in markCrabsOnImage", frame_id,nextFrame, prevFrame)

        crabsData = CrabsData(self.__folderStruct)
        markedCrabs = crabsData.crabsBetweenFrames(prevFrame,nextFrame)

        for markedCrab in markedCrabs:
            #print ('markedCrab', markedCrab)
            timer = MyTimer("crabsOnFrame")

            frame_number = markedCrab['frameNumber']

            crabLocation = Point(markedCrab['crabLocationX'], markedCrab['crabLocationY'])

            crabFeature = Feature(self.__driftData, frame_number, crabLocation, 5)
            #timer.lap("Step 150")
            crabLocation = crabFeature.getCoordinateInFrame(frame_id)

            #print ('crabLocation', str(crabLocation))

            mainImage.drawCross(crabLocation)

            timer.lap("crab: "+str(frame_number))


    def __drawLineOnCrab(self, crabBox, crabOnFrameID, frameID, mainImage):
        # draw user-marked line on the main image. but first translate the coordinates to this frame
        drift = self.__driftData.driftBetweenFrames(crabOnFrameID, frameID)
        crabBoxTopLeft = crabBox.topLeft.translateBy(drift)
        crabBoxBottomRight = crabBox.bottomRight.translateBy(drift)
        mainImage.drawLine(crabBoxTopLeft, crabBoxBottomRight)


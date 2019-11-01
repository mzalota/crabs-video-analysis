from lib.BadFramesData import BadFramesData
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
from lib.UserInput import UserInput
from lib.common import Point
from lib.SeeFloor import SeeFloor

class ScientistUI:
    __badFramesJump = 50 # how many frames to mark as bad when user presses B key

    def __init__(self, imageWin, folderStruct, videoStream, driftData):
        # type: (ImageWindow, FolderStructure, VideoStream, DriftData) -> ScientistUI
        self.__imageWin = imageWin
        self.__folderStruct = folderStruct
        self.__videoStream = videoStream
        self.__driftData = driftData

        self.__badFramesData = BadFramesData.createFromFile(folderStruct)
        self.__seeFloor = SeeFloor(driftData, self.__badFramesData, None)

    def processVideo(self):

        frame_id = self.__driftData.minFrameID()
        while True:
            print ("processing frame ID", int(frame_id))

            try:
                frame = Frame(frame_id, self.__videoStream)
            except Exception as error:
                print ("Failed to read next frame from video: ",frame_id )
                print(repr(error))
                traceback.print_exc()
                break

            #keyPressed = self._showFrame(frame.getImgObj(), frame_id)
            keyPressed = self.showFrame(frame)
            user_input = UserInput(keyPressed)

            if user_input.is_quit_command():
                # print "Pressed Q button"
                print("User requested to quit on frame: ", str(frame_id))
                break

            if user_input.is_mouse_click(): # keyPressed == ImageWindow.KEY_MOUSE_CLICK_EVENT:
                crabPoint = self.__imageWin.featureCoordiate
                crabUI = CrabUI(self.__folderStruct, self.__videoStream, self.__driftData, frame_id, crabPoint)
                crabUI.showCrabWindow()
                continue

            if user_input.is_bad_frame_command():
                print "Pressed B (bad frame) button"
                end_frame_id = frame_id + self.__badFramesJump
                self.__badFramesData.add_badframes(frame_id, end_frame_id)
                self.__badFramesData.save_to_file()
                self.__seeFloor.setBadFramesData(self.__badFramesData)

            new_frame_id = self.__determine_next_frame_id(frame_id, keyPressed)

            #elif keyPressed == ImageWindow.KEY_RIGHT_MOUSE_CLICK_EVENT:
            #    markedPoint = self.__imageWin.featureCoordiate
            #    print ("now need to mark coordinate ",str(markedPoint))
            #    new_frame_id = frame_id + 50

            frame_id = new_frame_id


    #TODO: Figure out why pressing Right button and then left button does not return you to the same frame ID
    def __determine_next_frame_id(self, frame_id, keyPressed):
        user_input = UserInput(keyPressed)
        if user_input.is_bad_frame_command():
            new_frame_id = frame_id + self.__badFramesJump + 1
        else:
            new_frame_id = self.__process_jump_key(frame_id, user_input)
            if new_frame_id is None:
                print ("Ignoring the fact that user pressed button:", keyPressed)  # , chr(keyPressed))
                new_frame_id = frame_id

        if new_frame_id > self.__driftData.maxFrameID():
            new_frame_id = self.__driftData.maxFrameID()

        if new_frame_id < self.__driftData.minFrameID():
            new_frame_id = self.__driftData.minFrameID()

        return new_frame_id

    def __process_jump_key(self, frame_id, user_input):

        if user_input.is_small_step_forward():
            # scroll 7 frames forward
            new_frame_id = frame_id+7
            return new_frame_id

        if user_input.is_small_step_backward():
            # scroll 7 frames backward
            new_frame_id = frame_id-7
            return new_frame_id

        if user_input.is_key_arrow_down():
            # scroll 50 frames forward
            new_frame_id = frame_id+50
            return new_frame_id

        if user_input.is_key_arrow_up():
            # scroll 50 frames backward
            new_frame_id = frame_id-50
            return new_frame_id

        if user_input.is_key_end():
            # Go to the very last seefloor slice
            return self.__seeFloor.maxFrameID()

        if user_input.is_key_home():
            # Go to the very first seefloor slice
            return self.__seeFloor.minFrameID()

        if user_input.is_next_seefloor_slice_command():
            # show next seefloor slices
            return self.__seeFloor.jumpToSeefloorSlice(frame_id, 1)

        if user_input.is_key_arrow_left():
            # show previous seefloor slices
            return self.__seeFloor.jumpToSeefloorSlice(frame_id, -1)

        if user_input.is_key_page_down():
            #Jump 10 steps forward
            return self.__seeFloor.jumpToSeefloorSlice(frame_id, 10)

        if user_input.is_key_page_up():
            #Jump 10 steps backward
            return self.__seeFloor.jumpToSeefloorSlice(frame_id, -10)

        return None


    def showFrame(self, frame):
        # type: (Frame) -> String

        mainImage = frame.getImgObj()
        frame_id = frame.getFrameID()
        markCrabsTimer = MyTimer()

        self.__drawFrameID(frame_id, mainImage)
        #markCrabsTimer.lap("processImage: step 20")

        self.__markCrabsOnImage(mainImage, frame_id)
        markCrabsTimer.lap("markCrabsTimer")

        keyPressed = self.__imageWin.showWindowAndWaitForClick(mainImage.asNumpyArray())

        #print ("keyPressed:", keyPressed)#, chr(keyPressed))
        return keyPressed


    def __drawFrameID(self, frame_id, mainImage):
        if frame_id == self.__driftData.minFrameID():
            frame_name = str(int(frame_id)) + " (First)"
        elif frame_id == self.__driftData.maxFrameID():
            frame_name = str(int(frame_id)) + " (Last)"
        elif self.__badFramesData.is_bad_frame(frame_id):
            frame_name = str(int(frame_id)) + " (Bad)"
        else:
            frame_name = int(frame_id)
        mainImage.drawFrameID(frame_name)

    def __markCrabsOnImage(self, mainImage, frame_id):
        nextFrame = self.__driftData.getNextFrame(FramesStitcher.FRAME_HEIGHT,frame_id)
        prevFrame = self.__driftData.getNextFrame(-FramesStitcher.FRAME_HEIGHT,frame_id)

        #print("in markCrabsOnImage", frame_id,nextFrame, prevFrame)

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

            #timer.lap("crab: "+str(frame_number))
from lib.Image import Image
from lib.common import Point
from lib.data.BadFramesData import BadFramesData
from lib.data.MarkersData import MarkersData
from lib.data.RedDotsManualData import RedDotsManualData
from lib.data.SeeFloorNoBadBlocks import SeeFloorNoBadBlocks
from lib.ui.CrabUI import CrabUI
from lib.data.CrabsData import CrabsData
from lib.data.DriftData import DriftData
from lib.Frame import Frame
from lib.ImageWindow import ImageWindow
from lib.ImagesCollage import ImagesCollage
from lib.data.RedDotsData import RedDotsData
from cv2 import cv2

import traceback
from lib.FrameDecorators import FrameDecoFactory

from lib.MyTimer import MyTimer
from lib.UserInput import UserInput
from lib.data.SeeFloor import SeeFloor
from lib.ui.RedDotsUI import RedDotsUI


class ScientistUI:
    __badFramesJump = 50 # how many frames to mark as bad when user presses B key
    CONTRAST_UP = (2, 10)
    CONTRAST_DOWN = (0.7, -10)
    CONTRAST_NORMAL = (1, 0)

    def __init__(self, imageWin, folderStruct, videoStream, driftData):
        # type: (ImageWindow, FolderStructure, VideoStream, DriftData) -> ScientistUI

        self.__zoom = False
        self.__contrastLevel = self.CONTRAST_NORMAL
        self.__imageWin = imageWin
        self.__folderStruct = folderStruct
        self.__videoStream = videoStream
        self.__driftData = driftData

        self.__badFramesData = BadFramesData.createFromFolderStruct(folderStruct)
        self.__redDotsManualData = RedDotsManualData(folderStruct)
        self.__seeFloor = SeeFloor.createFromFolderStruct(folderStruct)
        self.__seeFloorNoBadBlocks = SeeFloorNoBadBlocks.createFromFolderStruct(folderStruct)
        self.__crabData = CrabsData(self.__folderStruct)
        self.__redDotsUI = RedDotsUI(self.__videoStream)
        self.__markersData = MarkersData(folderStruct)
        self.__marker_id = 0


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

            keyPressed = self.showFrame(frame)
            user_input = UserInput(keyPressed)

            if keyPressed == ord("1"): # value is 49
                print ("pressed key 1")
                self.__marker_id = 1

            if keyPressed == ord("2"): # value is 50
                print ("pressed key 2")
                self.__marker_id = 2

            if keyPressed == ord("0"):
                print ("pressed key 0")
                self.__marker_id = 0

            if user_input.is_command_quit():
                print("User requested to quit on frame: ", str(frame_id))
                break

            if user_input.is_command_zoom():
                self.__change_zoom()
                continue

            if user_input.is_command_contrast():
                self.__change_contrast()
                continue

            if user_input.is_command_fix_red_dot():
                self.__show_red_dot_ui(frame_id)
                continue

            if user_input.is_mouse_click():
                if self.__marker_id == 0:
                    self.__show_crab_ui(frame_id)
                else:
                    markerPoint = self.__imageWin.featureCoordiate
                    print("recording a marker at point", str(markerPoint))
                    self.__markersData.add_mark(frame_id,markerPoint, self.__marker_id)
                    self.__markersData.save_to_file()
                    #self.__badFramesData.add_badframes(frame_id, self.__marker_id)
                    #self.__badFramesData.save_to_file()
                continue

            if user_input.is_command_bad_frame():
                self.__mark_as_bad_frame(frame_id)

            new_frame_id = self.__determine_next_frame_id(frame_id, keyPressed)

            if keyPressed == ImageWindow.KEY_RIGHT_MOUSE_CLICK_EVENT:
                markedPoint = self.__imageWin.featureCoordiate
                print ("now need to mark coordinate ",str(markedPoint))

            frame_id = new_frame_id

    def __change_zoom(self):
        # toggle Zoom flag
        if self.__zoom == True:
            self.__zoom = False
        else:
            self.__zoom = True

    def __mark_as_bad_frame(self, frame_id):
        print "Pressed B (bad frame) button"
        end_frame_id = frame_id + self.__badFramesJump
        self.__badFramesData.add_badframes(frame_id, end_frame_id)
        self.__badFramesData.save_to_file()
        self.__seeFloor.setBadFramesData(self.__badFramesData)

    def __show_crab_ui(self, frame_id):
        crabPoint = self.__imageWin.featureCoordiate
        crabUI = CrabUI(self.__crabData, self.__videoStream, self.__driftData, frame_id, crabPoint)
        crabUI.showCrabWindow()

    def __show_red_dot_ui(self, frame_id):
        frame_id_redDots = self.__redDotsUI.showUI(frame_id)
        print "catching frame_id_redDots"
        if frame_id_redDots is not None:
            redDots = self.__redDotsUI.selectedRedDots()
            self.__redDotsManualData.addManualDots(frame_id_redDots, redDots)
            # TODO: rerun interpolate, and make sure all xyzData objects are refreshed.
        self.__redDotsUI.closeWindow()

    def __change_contrast(self):
        print ("detected press C")
        if self.__contrastLevel == self.CONTRAST_NORMAL:
            self.__contrastLevel = self.CONTRAST_UP
        elif self.__contrastLevel == self.CONTRAST_UP:
            self.__contrastLevel = self.CONTRAST_DOWN
        elif self.__contrastLevel == self.CONTRAST_DOWN:
            self.__contrastLevel = self.CONTRAST_NORMAL

    def showFrame(self, frame):
        # type: (Frame) -> String

        markCrabsTimer = MyTimer("ScientistUI.showFrame()")

        frameImagesFactory = FrameDecoFactory(self.__seeFloor, self.__badFramesData, self.__crabData, self.__markersData, self.__videoStream)

        if self.__zoom:
            collage = ImagesCollage( frameImagesFactory, self.__seeFloorNoBadBlocks)
            imageToShow = collage.constructCollage(frame.getFrameID(), Frame.FRAME_HEIGHT / 2)
        else:
            imageToShow = self.__constructFrameImage(frameImagesFactory, frame)

        imageToShow = self.__adjustImageBrightness(imageToShow)

        markCrabsTimer.lap("imageToShow")
        keyPressed = self.__imageWin.showWindowAndWaitForClick(imageToShow.asNumpyArray())

        #print ("keyPressed:", keyPressed)#, chr(keyPressed))
        return keyPressed

    def __adjustImageBrightness(self, imageToShow):
        # type: (Image) -> Image
        if self.__contrastLevel == self.CONTRAST_DOWN:
            imageToShow = imageToShow.changeBrightness(self.CONTRAST_DOWN[0], self.CONTRAST_DOWN[1])
        if self.__contrastLevel == self.CONTRAST_UP:
            imageToShow = imageToShow.changeBrightness(self.CONTRAST_UP[0], self.CONTRAST_UP[1])
        return imageToShow

    def __constructFrameImage(self, frameImagesFactory, frameDeco):
        frameDeco = frameImagesFactory.getFrameDecoFrameID(frameDeco)
        frameDeco = frameImagesFactory.getFrameDecoRedDots(frameDeco)
        frameDeco = frameImagesFactory.getFrameDecoMarkedCrabs(frameDeco)
        frameDeco = frameImagesFactory.getFrameDecoMarkers(frameDeco)
        return frameDeco.getImgObj().copy()

    #TODO: Figure out why pressing Right button and then left button does not return you to the same frame ID
    def __determine_next_frame_id(self, frame_id, keyPressed):
        user_input = UserInput(keyPressed)
        if user_input.is_command_bad_frame():
            new_frame_id = frame_id + self.__badFramesJump + 1
        else:
            new_frame_id = self.__process_navigation_key_press(frame_id, user_input)
            if new_frame_id is None:
                print ("Ignoring the fact that user pressed button:", keyPressed)  # , chr(keyPressed))
                new_frame_id = frame_id

        if new_frame_id > self.__driftData.maxFrameID():
            new_frame_id = self.__driftData.maxFrameID()

        if new_frame_id < self.__driftData.minFrameID():
            new_frame_id = self.__driftData.minFrameID()

        return new_frame_id

    def __process_navigation_key_press(self, frame_id, user_input):

        if user_input.is_large_step_forward():
            # scroll 7 frames forward
            new_frame_id = frame_id+500
            return new_frame_id

        if user_input.is_large_step_backward():
            # scroll 7 frames forward
            new_frame_id = frame_id-500
            return new_frame_id

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
            #return self.__seeFloor.getNextFrame(frame_id)
            return self.__seeFloor.jumpToSeefloorSlice(frame_id, 0.8)

        if user_input.is_key_arrow_left():
            # show previous seefloor slices
            #return self.__seeFloor.getPrevFrame(frame_id)
            return self.__seeFloor.jumpToSeefloorSlice(frame_id, -0.8)

        if user_input.is_key_page_down():
            #Jump 10 steps forward
            return self.__seeFloor.jumpToSeefloorSlice(frame_id, 10)

        if user_input.is_key_page_up():
            #Jump 10 steps backward
            return self.__seeFloor.jumpToSeefloorSlice(frame_id, -10)

        return None

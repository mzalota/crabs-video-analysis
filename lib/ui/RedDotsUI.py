import cv2

from lib.Frame import Frame
from lib.ImageWindow import ImageWindow
from lib.data.RedDotsData import RedDotsData
from lib.UserInput import UserInput
from lib.common import Box, Point
from lib.data.RedDotsManualData import RedDotsManualData
from lib.data.RedDotsRawData import RedDotsRawData


class RedDotsUI:
    # we expect Red Dots to be alwas withing these Coordinates. If red dots wander outside, then these coordinates shoud be expanded
    #__zoomBox = Box(Point(800, 400), Point(1300, 700))
    __zoomBox = Box(Point(400, 200), Point(1500, 900))

    def __init__(self, videoStream):
        # type: (VideoStream) -> RedDotsUI
        self.__videoStream = videoStream
        self.__imageZoomWin = ImageWindow("zoomImg", Point(100, 100))

    def selectedRedDots(self):
        redDotsInCoordinatesOfZoomWin = self.__imageZoomWin.featureBox
        redDots = redDotsInCoordinatesOfZoomWin.translateCoordinateToOuter(self.__zoomBox.topLeft)
        print("redDotsInCoordinatesOfZoomWin", str(redDotsInCoordinatesOfZoomWin),"redDots", str(redDots))
        return redDots

    def closeWindow(self):
        self.__imageZoomWin.closeWindow()

    def showUI(self, frameID, gapSize = None):

        while True:
            image = self.__videoStream.readImageObj(frameID)

            zoomImage = image.subImage(self.__zoomBox)
            zoomImage.drawFrameID(frameID)

            if gapSize is not None:
                gapText = "Gap: " + str(int(gapSize))
                box = Box(Point(zoomImage.width()-180,zoomImage.height()-50),Point(zoomImage.width(), zoomImage.height()))
                zoomImage.drawTextInBox(box, gapText)

            keyPressed = self.__imageZoomWin.showWindowAndWaitForTwoClicks(zoomImage.asNumpyArray())
            user_input = UserInput(keyPressed)

            if user_input.is_command_quit():
                message = "User pressed Q button"
                print message
                return None

            if user_input.is_mouse_click():
                return frameID

            if user_input.is_key_arrow_down():
                # show frame +2 away
                frameID = frameID + 2

            elif user_input.is_key_arrow_up():
                # show frame -2 away
                frameID = frameID - 2

            elif user_input.is_key_arrow_right():
                # show frame +20 away
                frameID = frameID + 20

            elif user_input.is_key_arrow_left():
                # show frame -20 away
                frameID = frameID - 20
            else:
                print ("invalid Key pressed:", keyPressed)

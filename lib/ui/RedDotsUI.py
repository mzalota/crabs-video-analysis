import cv2

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

    def __init__(self, folderStruct, videoStream):
        # type: (FolderStructure, VideoStream) -> RedDotsUI
        self.__folderStruct = folderStruct
        self.__videoStream = videoStream

    def showUI(self):
        redDotsManualData = RedDotsManualData(self.__folderStruct)
        #redDotsRawData = RedDotsRawData(self.__folderStruct)
        #rawRedDotsData = RedDotsData(self.__folderStruct)

        imageZoomWin = ImageWindow("zoomImg", Point(100, 100))

        frameID = redDotsManualData.getMiddleOfBiggestGap()
        while True:
            print ("frame", frameID)

            image = self.__videoStream.readImageObj(frameID)
            # image.drawFrameID(frameID)
            # frame = Frame(frameID, videoStream)

            # imageWin.showWindow(image.asNumpyArray())

            zoomImage = image.subImage(self.__zoomBox)
            zoomImage.drawFrameID(frameID)

            keyPressed = imageZoomWin.showWindowAndWaitForTwoClicks(zoomImage.asNumpyArray())
            user_input = UserInput(keyPressed)

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

            elif user_input.is_quit_command():
                # print "Pressed Q button" quit
                message = "User pressed Q button"
                print message
                break
            else:
                # user clicked with a mouse, presumably
                self.__processRedDots(frameID, imageZoomWin.featureBox, redDotsManualData)

                frameID = redDotsManualData.getMiddleOfBiggestGap()

        cv2.destroyAllWindows()

    def __processRedDots(self, frameID, redDotsInCoordinatesOfZoomWin, redDotsManualData):

        redDots = redDotsInCoordinatesOfZoomWin.translateCoordinateToOuter(self.__zoomBox.topLeft)

        redDotsManualData.addManualDots(frameID, redDots)
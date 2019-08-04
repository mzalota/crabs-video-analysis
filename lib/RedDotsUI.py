import cv2

from lib.ImageWindow import ImageWindow
from lib.RedDotsData import RedDotsData
from lib.common import Box, Point


class RedDotsUI:
    # we expect Red Dots to be alwas withing these Coordinates. If red dots wander outside, then these coordinates shoud be expanded
    #__zoomBox = Box(Point(800, 400), Point(1300, 700))
    __zoomBox = Box(Point(400, 200), Point(1500, 900))

    def __init__(self, folderStruct, videoStream):
        # type: (FolderStructure, VideoStream) -> object
        self.__folderStruct = folderStruct
        self.__videoStream = videoStream

    def showUI(self):

        rawRedDotsData = RedDotsData(self.__folderStruct)

        imageZoomWin = ImageWindow("zoomImg", Point(100, 100))

        frameID = rawRedDotsData.getMiddleOfBiggestGap()
        while True:
            print ("frame", frameID)

            image = self.__videoStream.readImageObj(frameID)
            # image.drawFrameID(frameID)
            # frame = Frame(frameID, videoStream)

            # imageWin.showWindow(image.asNumpyArray())

            zoomImage = image.subImage(self.__zoomBox)
            zoomImage.drawFrameID(frameID)

            keyPressed = imageZoomWin.showWindowAndWaitForTwoClicks(zoomImage.asNumpyArray())

            if keyPressed == ImageWindow.KEY_ARROW_DOWN or keyPressed == ImageWindow.KEY_SPACE or keyPressed == ord("n"):
                # show frame +20 away
                frameID = frameID + 20

            elif keyPressed == ImageWindow.KEY_ARROW_UP:
                # show frame -20 away
                frameID = frameID - 20

            elif keyPressed == ImageWindow.KEY_ARROW_RIGHT:
                # show frame +2 away
                frameID = frameID + 2

            elif keyPressed == ImageWindow.KEY_ARROW_LEFT:
                # show frame -2 away
                frameID = frameID - 2

            elif keyPressed == ord("q"):
                # print "Pressed Q button" quit
                message = "User pressed Q button"
                # mustExit = True
                print message
                break
                # raise UserWantsToQuitException(message)
            else:
                # user clicked with a mouse, presumably
                self.__processRedDots(frameID, imageZoomWin.featureBox, rawRedDotsData)

                frameID = rawRedDotsData.getMiddleOfBiggestGap()

        cv2.destroyAllWindows()

    def __processRedDots(self, frameID, redDotsInCoordinatesOfZoomWin, rawRedDotsData):

        redDots = redDotsInCoordinatesOfZoomWin.translateCoordinateToOuter(self.__zoomBox.topLeft)

        rawRedDotsData.addManualDots(frameID, redDots)
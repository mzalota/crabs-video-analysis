import cv2
from pyautogui import press

from common import Point,Box


class ImageWindow:
    featureCoordiate = None
    featureBox = None
    __windowPositionAndDimensionsInitialized = False

    def __init__ (self,windowName, position):
        self.__windowName = windowName
        self.__windowPosition = position
        self.__windowPositionAndDimensionsInitialized = False
        self.__windowWidth = 900
        self.__windowHight = 600
        #cv2.startWindowThread()

    @staticmethod
    def createWindow(windowName, windowBox):
        # type: (String, Box) -> ImageWindow
        win = ImageWindow(windowName, windowBox.topLeft)
        win.__windowWidth = windowBox.width()
        win.__windowHight = windowBox.hight()
        return win

    def waitForMouseClick(self):
        cv2.setMouseCallback(self.__windowName, self.click_and_crop)
        # cv2.setMouseCallback("mainWithRedDots", click_and_crop)
        print "Click on a new feature"
        cv2.waitKey(0)

    def click_and_crop(self, event, x, y, flags, param):
        self.wasClicked(event, x, y)

    def wasClicked(self, event, x, y):
        # check to see if the left mouse button was released
        if event == cv2.EVENT_LBUTTONDOWN:
            self.featureCoordiate = Point(x, y)
            self.featureBox = self.featureCoordiate.boxAroundPoint(100)
            #cv2.rectangle(image, (max(x - 50, 1), max(y - 50, 1)), (x + 50, y + 50), (255, 0, 0), 2)
            print "keyPress A"
            press('a')

    def showWindow(self, image):
        if not self.__windowPositionAndDimensionsInitialized:
            cv2.namedWindow(self.__windowName, cv2.WINDOW_NORMAL)  # WINDOW_AUTOSIZE
            cv2.resizeWindow(self.__windowName, self.__windowWidth, self.__windowHight)
            cv2.moveWindow(self.__windowName, self.__windowPosition.x, self.__windowPosition.y)
            self.__windowPositionAndDimensionsInitialized = True
        cv2.imshow(self.__windowName, image)

    def showWindowAndWaitForClick(self, image):
        self.showWindow(image)
        self.waitForMouseClick()

    def showWindowAndWait(self, image, delay):
        self.showWindow(image)
        cv2.waitKey(delay)

    def closeWindow(self):
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.destroyWindow(self.__windowName)
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)
        print "trying to close window " + self.__windowName

import cv2
from pyautogui import press

from Image import Image
from common import Point,Box


class ImageWindow:
    featureCoordiate = None
    featureBox = None
    __windowPositionAndDimensionsInitialized = False

    KEY_HOME = 2359296
    KEY_END = 2293760
    KEY_PAGE_UP = 2162688
    KEY_PAGE_DOWN = 2228224
    KEY_ARROW_DOWN = 2621440
    KEY_ARROW_UP = 2490368
    KEY_ARROW_RIGHT = 2555904
    KEY_ARROW_LEFT = 2424832
    KEY_SPACE = 32

    KEY_MOUSE_CLICK_EVENT = 97
    KEY_RIGHT_MOUSE_CLICK_EVENT = 65
    KEY_A = 97

    def __init__ (self,windowName, position):
        self.__windowName = windowName
        self.__windowPosition = position
        self.__windowPositionAndDimensionsInitialized = False
        self.__windowWidth = 960 #900
        self.__windowHight = 540 #600
        #cv2.startWindowThread()

    @staticmethod
    def createWindow(windowName, windowBox):
        # type: (String, Box) -> ImageWindow
        win = ImageWindow(windowName, windowBox.topLeft)
        win.__windowWidth = windowBox.width()
        win.__windowHight = windowBox.hight()
        return win

    def __waitForMouseClick(self):
        # type: () -> int
        self.__mouseButtomWasClicked = False
        cv2.setMouseCallback(self.__windowName, self.__click_event_handler)
        keyPressed = cv2.waitKeyEx(0)
        return keyPressed

    def __click_event_handler(self, event, x, y, flags, param):
        self.__wasClicked(event, x, y)

    def __wasClicked(self, event, x, y):
        # check to see if the left mouse button was released
        #print ("__wasClicked",event)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.featureCoordiate = Point(x, y)
            self.__mouseButtomWasClicked = True

            # just pretend a key button 'a'  was pressed, so that cv2 framework returns from cv2.waitKeyEx() function
            press(chr(self.KEY_MOUSE_CLICK_EVENT))

        if event == cv2.EVENT_RBUTTONDOWN:
            self.featureCoordiate = Point(x, y)
            self.__mouseButtomWasClicked = True

            # just pretend a key button 'a'  was pressed, so that cv2 framework returns from cv2.waitKeyEx() function
            press(chr(self.KEY_RIGHT_MOUSE_CLICK_EVENT))

    def userClickedMouse(self):
        return self.__mouseButtomWasClicked

    def userClickedMouseTwice(self):
        if self.featureBox is not None:
            return True
        else:
            return False

    def showWindow(self, image):
        # type: (numpy)

        if not self.__windowPositionAndDimensionsInitialized:
            cv2.namedWindow(self.__windowName, cv2.WINDOW_NORMAL)  # WINDOW_AUTOSIZE
            cv2.resizeWindow(self.__windowName, self.__windowWidth, self.__windowHight)
            cv2.moveWindow(self.__windowName, self.__windowPosition.x, self.__windowPosition.y)
            self.__windowPositionAndDimensionsInitialized = True
        cv2.imshow(self.__windowName, image)

    def showWindowAndWaitForClick(self, image):
        # type: (numpy) -> int

        self.showWindow(image)
        return self.__waitForMouseClick()

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
        #print "trying to close window " + self.__windowName

    def showWindowAndWaitForTwoClicks(self, image):

        keyPress = self.showWindowAndWaitForClick(image)
        if not self.userClickedMouse():
            return keyPress

        point1 = self.featureCoordiate

        img = Image(image)
        img.drawBoxOnImage(point1.boxAroundPoint(3))

        keyPress = self.showWindowAndWaitForClick(image)
        if not self.userClickedMouse():
            return keyPress

        point2 = self.featureCoordiate

        if point1.x<=point2.x:
            self.featureBox = Box(point1, point2)
        else:
            #second Click was to the left of the first. Reverse the two points
            self.featureBox = Box(point2, point1)

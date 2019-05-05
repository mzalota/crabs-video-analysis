import uuid

import cv2

from Frame import Frame
from Image import Image
from ImageWindow import ImageWindow
from common import Box, Point, Vector


class SeeFloorSection:
    __threshold_for_matching = 0.6

    def __init__(self,frame, box):
        self.__initialize()
        self.__startingBox = box
        self.pluckFeature(frame, box.topLeft)

    def __initialize(self):
        self.__id = str(uuid.uuid4().fields[-1])[:5]
        self.__frameIDs = list()
        self.__frames = dict()
        self.__topLeftPoints = dict()
        self.__startingBox = None
        self.__subImageWin = None

    def closeWindow(self):
        self.showSubImage()
        self.__subImageWin.closeWindow()

    def __getWindowName(self):
        return self.__id

    def __defaultBoxAroundFeature(self):
        box = Box(self.__getTopLeft(),
                      Point(self.__getTopLeft().x + self.__startingBox.width(),
                            self.__getTopLeft().y + self.__startingBox.hight()))
        return box

    def __getTopLeft(self):
        if len(self.__topLeftPoints)<1:
            return None
        lastPoint = self.__topLeftPoints[max(self.__topLeftPoints.keys())]
        return lastPoint

    def showSubImage(self):
        img = self.getImage()
        if self.__subImageWin is None:
            self.__subImageWin = ImageWindow.createWindow(self.__getWindowName(), self.__defaultBoxAroundFeature())
        if img is not None:
            self.__subImageWin.showWindow(img)

    def pluckFeature(self, frame, topLeftPoint):
        # type: (Frame, Point) -> None
        self.__topLeftPoints[frame.getFrameID()] = topLeftPoint #append
        self.__frames[frame.getFrameID()] = frame
        self.__frameIDs.append(frame.getFrameID())

    def getDrift(self):
        numOfFrames = len(self.__topLeftPoints)
        if numOfFrames <= 1:
            return None

        lastFrame = self.__frameIDs[numOfFrames-1]
        beforeLastFrame = self.__frameIDs[numOfFrames-2]
        lastPoint = self.__topLeftPoints[lastFrame]
        beforeLastPoint = self.__topLeftPoints[beforeLastFrame]
        driftVector = Vector(lastPoint.x-beforeLastPoint.x, lastPoint.y-beforeLastPoint.y)
        if (driftVector.isZeroVector()):
            return None

        return driftVector
        #return lastPoint.distanceTo(beforeLastPoint)

    def drawFeatureOnFrame(self, image):
        #TODO: refactor image numpy array into Image class
        box = self.__defaultBoxAroundFeature()
        image.drawBoxOnImage(box)
        image.drawTextInBox(box,self.__id)

    def getImage(self):
        if len(self.__frames)<1:
            return None

        img = self.__getLastFrame().getImgObj()
        #img = Image(image)
        return img.subImage(self.__defaultBoxAroundFeature()).asNumpyArray()

    def __getLastFrame(self):
        return self.__frames[max(self.__frames.keys())]

    def getLocation(self):
        box = self.__defaultBoxAroundFeature()
        return box.topLeft.calculateMidpoint (box.bottomRight)

    def findFeature(self, frame):
        # type: (Frame) -> Point
        newLocation = self.__findSubImage(frame.getImage(), self.getImage())
        if newLocation:
            self.pluckFeature(frame,newLocation)
        return newLocation

    def __findSubImage(self, image, subImage):
        if subImage is None:
            return None

        # Algorithm is described here: https: // www.geeksforgeeks.org / template - matching - using - opencv - in -python /

        # Convert image and subImage to grayscale
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        subImage_gray = cv2.cvtColor(subImage, cv2.COLOR_BGR2GRAY)

        # Perform match operations.
        res = cv2.matchTemplate(img_gray, subImage_gray, cv2.TM_CCOEFF_NORMED)

        #determine which rechtangle on the image is the best fit for subImage (has the highest correlation)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        self.__correlation = max_val

        if max_val < self.__threshold_for_matching:
            # If the best matching box still has correlation below the "threshold" then declare defeat -> we could not find a match for subImage on this image
            return None

        # get w and h, so that we can reconstruct the box
        d, w, h = subImage.shape[::-1]
        topLeft = Point(max_loc[0], max_loc[1])
        Point(topLeft.x + w, topLeft.y + h)

        return topLeft

    @staticmethod
    def infoHeaders():
        row = []
        row.append("featureId")
        row.append("featureX")
        row.append("featureY")
        return row

    def infoAboutFeature(self):
        row = []
        row.append(self.__id)
        row.append(self.getLocation().x)
        row.append(self.getLocation().y)

        return row

    def getID(self):
        # type: () -> String
        return self.__id
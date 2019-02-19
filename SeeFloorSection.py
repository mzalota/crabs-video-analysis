import uuid

import cv2

from ImageWindow import ImageWindow
from common import Box, Point, subImage, calculateMidpoint, distanceBetweenPoints


class SeeFloorSection:
    __threshold_for_matching = 0.6

    @staticmethod
    def createFeature(frame, box):
        #feature = SeeFloorSection(box.width())
        feature = SeeFloorSection()
        feature.__startingBox = box
        feature.pluckFeature(frame, box.topLeft)
        feature.__subImageWin = ImageWindow.createWindow(feature.__getWindowName(), box)
        return feature

    def __init__(self):
        self.__initialize()

    def __initialize(self):
        self.__id = str(uuid.uuid4().fields[-1])[:5]
        self.__frameIDs = list()
        self.__images = dict()
        self.__topLeftPoints = dict()
        self.__startingBox = None

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

    def __defaultBoxAroundFeatur2(self):
        offsetY = 100
        offsetX = 200
        point = self.__getTopLeft()
        return Box(Point(max(point.x - offsetX, 1), max(point.y - offsetY, 1)),
                   Point(point.x + offsetX, point.y + offsetY))

    def showSubImage(self):
        img = self.getImage()
        if img is not None:
            self.__subImageWin.showWindow(img)

    def pluckFeature(self, frame, topLeftPoint):
        # type: (object, object) -> object
        self.__topLeftPoints[frame.getFrameID()] = topLeftPoint #append
        image = subImage(frame.getImage(), self.__defaultBoxAroundFeature())
        self.__images[frame.getFrameID()] = image.copy()
        self.__frameIDs.append(frame.getFrameID())



    def getDrift(self):
        numOfFrames = len(self.__topLeftPoints)
        if numOfFrames > 1:
            lastFrame = self.__frameIDs[numOfFrames-1]
            beforeLastFrame = self.__frameIDs[numOfFrames-2]
            lastPoint = self.__topLeftPoints[lastFrame]
            beforeLastPoint = self.__topLeftPoints[beforeLastFrame]
            return distanceBetweenPoints(lastPoint,beforeLastPoint)
        return None

    def drawFeatureOnFrame(self, image):
        box = self.__defaultBoxAroundFeature()
        cv2.rectangle(image, (box.topLeft.x, box.topLeft.y), (box.bottomRight.x, box.bottomRight.y), (0, 255, 0), 2)
        self.__addIDText(box, image)

    def __addIDText(self, box, image):
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (box.topLeft.x, box.topLeft.y + 27)
        fontScale = 1
        fontColor = (0, 255, 0)
        lineType = 2
        cv2.putText(image, self.__id,
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)

    def getImage(self):
        if len(self.__images)<1:
            return None
        return self.__images[max(self.__images.keys())]

    def getLocation(self):
        box = self.__defaultBoxAroundFeature()
        return calculateMidpoint(box.topLeft, box.bottomRight)

    def findFeature(self, frame):
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
import uuid

import cv2

from lib.Frame import Frame
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from common import Box, Point, Vector


class SeeFloorSection:
    #__threshold_for_matching = 0.6

    def setThreshold(self,newThresholdForMatching):
        self.__threshold_for_matching = newThresholdForMatching

    def __init__(self,frame, box):
        self.setThreshold(0.6)
        self.__initialize()
        self.__startingBox = box
        self.__pluckFeature(frame, box.topLeft)

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

    def __boxAroundFeatureForFrame(self,frameID):
        topLeftPoint = self.__getTopLeftForFrame(frameID)
        box = Box(topLeftPoint,
                  Point(topLeftPoint.x + self.__startingBox.width(),
                        topLeftPoint.y + self.__startingBox.hight()))
        return box

    def __getTopLeft_old(self):
        if len(self.__topLeftPoints)<1:
            return None
        lastPoint = self.__topLeftPoints[max(self.__topLeftPoints.keys())]
        return lastPoint

    def __getTopLeft(self):
        return self.__getTopLeftForFrame(self.getMaxFrameID())

    def __getTopLeftForFrame(self, frameID):
        if len(self.__topLeftPoints)<1:
            return None

        if frameID not in (self.__topLeftPoints):
            return None

        return self.__topLeftPoints[frameID]

    def showSubImage_old(self):
        if self.__subImageWin is None:
            self.__subImageWin = ImageWindow.createWindow(self.__getWindowName(), self.__defaultBoxAroundFeature())

        frameID = self.__getLastFrame().getFrameID()
        img = self.getImage()
        if img is not None:
            img.drawFrameID(frameID)
            self.__subImageWin.showWindow(img.asNumpyArray())

    def showSubImage(self):
        frameID = self.getMaxFrameID()
        return self.showSubImageForFrame(frameID)

    def showSubImageForFrame(self, frameID):
        if self.__subImageWin is None:
            self.__subImageWin = ImageWindow.createWindow(self.__getWindowName(), self.__defaultBoxAroundFeature())

        img = self.getImageOnFrame(frameID)
        if img is not None:
            img.drawFrameID(frameID)
            self.__subImageWin.showWindow(img.asNumpyArray())



    def __pluckFeature(self, frame, topLeftPoint):
        # type: (Frame, Point) -> None
        self.__topLeftPoints[frame.getFrameID()] = topLeftPoint #append
        self.__frames[frame.getFrameID()] = frame
        self.__frameIDs.append(frame.getFrameID())

    def getDrift(self):
        # type: () -> Vector
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

    def drawFeatureOnFrame(self, image):
        box = self.__defaultBoxAroundFeature()
        image.drawBoxOnImage(box)
        image.drawTextInBox(box,self.__id)

    def getImage_old(self):
        # type: () -> Image
        if len(self.__frames)<1:
            return None

        #frameID = self.__getLastFrame().getFrameID()
        img = self.__getLastFrame().getImgObj()
        #img.drawFrameID(frameID)
        return img.subImage(self.__defaultBoxAroundFeature())

    def getImage(self):
        # type: () -> Image
        return self.getImageOnFrame(self.getMaxFrameID())

    def getImageOnFrame(self,frameID):
        # type: () -> Image
        if len(self.__frames)<1:
            return None

        if frameID not in (self.__frames):
            return None

        frame = self.__frames[frameID]
        imgObj = frame.getImgObj()
        img = imgObj.subImage(self.__boxAroundFeatureForFrame(frameID))
        return img

    def __getLastFrame(self):
        return self.__frames[self.getMaxFrameID()]

    def getLocation(self):
        box = self.__defaultBoxAroundFeature()
        return box.topLeft.calculateMidpoint (box.bottomRight)

    def findFeature(self, frame):
        # type: (Frame) -> Point
        newLocation = self.__findSubImage(frame.getImgObj().asNumpyArray(), self.getImage().asNumpyArray())
        if newLocation:
            self.__pluckFeature(frame, newLocation)
        return newLocation

    def findInAllFrames(self):
        startingFrameID = self.__getLastFrame().getFrameID()
        for i in range(1,50,1):
            nextFrameID = int(startingFrameID) + i
            print ("nextFrameID", nextFrameID, startingFrameID, i)
            nextFrame = Frame(nextFrameID, self.__getLastFrame().getVideoStream())
            newLocation = self.findFeature(nextFrame)
            if newLocation is None:
                break
            print ("frame", newLocation, self.infoAboutFeature())
            self.showSubImage()

        '''  
        for i in range(1,-200,-5):
            nextFrameID = int(startingFrameID) + i
            print ("nextFrameID", nextFrameID, startingFrameID, i)
            nextFrame = Frame(nextFrameID, self.__getLastFrame().getVideoStream())
            newLocation = self.findFeature(nextFrame)
            if newLocation is None:
                break
            print ("frame", newLocation, self.infoAboutFeature())
        '''


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
        row.append("numberOfFrameIDs")
        row.append("numberOfFrames")
        row.append("numberOfTopLeftPoints")
        row.append("maxFrameID")
        row.append("minFrameID")
        row.append("correlation")
        return row

    def infoAboutFeature(self):
        row = []
        row.append(self.__id)
        row.append(self.getLocation().x)
        row.append(self.getLocation().y)
        row.append(len(self.__frameIDs))
        row.append(len(self.__frames))
        row.append(len(self.__topLeftPoints))
        row.append(self.getMaxFrameID())
        row.append(self.getMinFrameID())
        row.append(self.__correlation)

        return row

    def getID(self):
        # type: () -> String
        return self.__id

    def getMaxFrameID(self):
        # type: () -> String
        return max(self.__frameIDs)

    def getMinFrameID(self):
        # type: () -> String
        return min(self.__frameIDs)

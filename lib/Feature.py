from lib.Frame import Frame
from lib.common import Point, Box


class Feature:

    def __init__(self, driftData, frameID, location):
        self.__driftData = driftData
        self.__frameID = frameID
        self.__location = location

        #self.__firstFrameID = frameID
        #self.__lastFrameID = frameID

        self.__determineFirstAndLastFrameID()
        #print ("firstFrameID and lastFrameID", self.__firstFrameID, self.__lastFrameID)

    def getInitFrameID(self):
        return self.__frameID

    def getInitFrameCoordinate(self):
        return self.__location

    def getFirstFrameID(self):
        return self.__firstFrameID

    def getLastFrameID(self):
        return self.__lastFrameID

    def getCoordinateInFrameAAA(self, frameID):
        # type: (String) -> Point
        drift = self.__driftData.driftBetweenFrames(self.__frameID, frameID)
        return self.__location.translateBy(drift)

    def firstAndLastGoodCrabImages(self, boxSize):
        self.__frameIDOfFirstGoodImage = 0
        self.__frameIDOfLastGoodImage = 0
        self.__maximumAreaFrameID = self.__frameID

        self.__getValues(self.__firstFrameID, self.__lastFrameID, boxSize)
        #print ("maximumAreaFrameIDDown", self.__maximumAreaFrameID, self.__maximumArea)
        #print ("frameIDOfFirstGoodImage and frameIDOfLastGoodImage", self.__frameIDOfFirstGoodImage, self.__frameIDOfLastGoodImage)

        if (self.__frameIDOfFirstGoodImage > 0 and self.__frameIDOfLastGoodImage >0):
            return self.__frameIDOfFirstGoodImage, self.__frameIDOfLastGoodImage
        else:
            return self.__maximumAreaFrameID, self.__maximumAreaFrameID

    def __determineFirstAndLastFrameID(self):
        nextFrameID = self.__frameID
        while (True):
            nextFrameID = nextFrameID + 1
            newPoint = self.getCoordinateInFrame(nextFrameID)
            # print("drift:", frameID, str(crabPoint), nextFrameID, str(newPoint), str(drift), visibleBoxArea.area(), str(visibleBoxArea))
            if (newPoint.x <= 0 or newPoint.y <= 0):
                #print("drift:",  nextFrameID, str(newPoint))
                self.__lastFrameID = nextFrameID - 1
                break

            if (newPoint.x >= Frame.FRAME_WIDTH or newPoint.y >= Frame.FRAME_HEIGHT):
                #print("drift:",  nextFrameID, str(newPoint))
                self.__lastFrameID = nextFrameID - 1
                break

        nextFrameID = self.__frameID
        while (True):
            nextFrameID = nextFrameID - 1
            newPoint = self.getCoordinateInFrame(nextFrameID)
            # print("drift:", frameID, str(crabPoint), nextFrameID, str(newPoint), str(drift), visibleBoxArea.area(), str(visibleBoxArea))
            if (newPoint.x <= 0 or newPoint.y <= 0):
                #print("drift:",  nextFrameID, str(newPoint))
                self.__firstFrameID = nextFrameID + 1
                break

            if (newPoint.x >= Frame.FRAME_WIDTH or newPoint.y >= Frame.FRAME_HEIGHT):
                #print("drift:",  nextFrameID, str(newPoint))
                self.__firstFrameID = nextFrameID + 1
                break

    def __getValues(self, minFrameID, maxFrameID, boxSize):
        nextFrameID = minFrameID

        self.__maximumArea = 0
        firstGoodImageFound = False
        while (nextFrameID<=maxFrameID):
            visibleBoxArea = self.__constructVisibleArea(nextFrameID, boxSize)

            if (visibleBoxArea.area() > self.__maximumArea):
                self.__maximumAreaFrameID = nextFrameID
                self.__maximumArea = visibleBoxArea.area()
            # print("drift:", frameID, str(crabPoint), nextFrameID, str(newPoint), str(drift), visibleBoxArea.area(), str(visibleBoxArea))

            if visibleBoxArea.area() >= boxSize * boxSize:
                # print "thats your last good image of crab"
                self.__frameIDOfLastGoodImage = nextFrameID
                if not firstGoodImageFound:
                    self.__frameIDOfFirstGoodImage = nextFrameID
                    firstGoodImageFound = True

            nextFrameID = nextFrameID + 1


    def __constructVisibleArea(self, nextFrameID, boxSize):
        offset = int(boxSize / 2)
        newPoint = self.getCoordinateInFrame(nextFrameID)
        topleft = Point(max(newPoint.x - offset, 0), max(newPoint.y - offset, 0))
        bottomRight = Point(min(newPoint.x + offset, Frame.FRAME_WIDTH), min(newPoint.y + offset, Frame.FRAME_HEIGHT))
        visibleBoxArea = Box(topleft, bottomRight)
        return visibleBoxArea


    def getCoordinateInFrame(self, frameID):
        # type: (String) -> Point
        drift = self.__driftData.driftBetweenFrames(self.__frameID, frameID)
        newPoint = self.__location.translateBy(drift)
        return newPoint
from lib.Frame import Frame
from lib.common import Point, Box


class Feature:

    def __init__(self,driftData, frameID, location):
        self.__driftData = driftData

        self.__frameIDOfLastGoodImage = 0
        self.__frameIDOfFirstGoodImage = 0

        self.__lastFrameID = frameID
        self.__firstFrameID = frameID
        self.__maximumAreaFrameID = frameID

        self.__location = location

    def firstAndLastGoodCrabImages(self, frameID):

        self.__goingUp(frameID, frameID)
        self.__goingDown(frameID, frameID)

        #print ("firstFrameID and lastFrameID", self.firstFrameID, self.lastFrameID)
        maximumAreaFrameIDUp = self.__goingUp(frameID, self.__firstFrameID)
        #print ("maximumAreaFrameIDUp", maximumAreaFrameIDUp)
        maximumAreaFrameIDDown = self.__goingDown(frameID, self.__lastFrameID)

        print ("maximumAreaFrameIDDown", maximumAreaFrameIDDown)
        print ("frameIDOfFirstGoodImage and frameIDOfLastGoodImage", self.__frameIDOfFirstGoodImage, self.__frameIDOfLastGoodImage)

    def __goingUp(self, frameID, nextFrameID):
        maximumAreaFrameID = 0
        maximumArea = 0
        while (True):
            nextFrameID = nextFrameID + 1
            drift = self.__driftData.driftBetweenFrames(frameID, nextFrameID)
            newPoint = self.__location.translateBy(drift)
            topleft = Point(max(newPoint.x - 100, 0), max(newPoint.y - 100, 0))

            bottomRight = Point(min(newPoint.x + 100, Frame.FRAME_WIDTH), min(newPoint.y + 100, Frame.FRAME_HEIGHT))
            visibleBoxArea = Box(topleft, bottomRight)
            if (visibleBoxArea.area() > maximumArea):
                maximumAreaFrameID = nextFrameID
                maximumArea = visibleBoxArea.area()

            # print("drift:", frameID, str(crabPoint), nextFrameID, str(newPoint), str(drift), visibleBoxArea.area(), str(visibleBoxArea))
            if (newPoint.x <= 0 or newPoint.y <= 0):
                self.__lastFrameID = nextFrameID - 1
                break

            if (newPoint.x >= Frame.FRAME_WIDTH or newPoint.y >= Frame.FRAME_HEIGHT):
                self.__lastFrameID = nextFrameID - 1
                break

            if visibleBoxArea.area() >= 200 * 200:
                # print "thats your last good image of crab"
                self.__frameIDOfLastGoodImage = nextFrameID

        return maximumAreaFrameID

    def __goingDown(self, frameID, nextFrameID):
        maximumArea = 0
        maximumAreaFrameID = 0
        while (True):
            nextFrameID = nextFrameID - 1
            drift = self.__driftData.driftBetweenFrames(frameID, nextFrameID)
            newPoint = self.__location.translateBy(drift)
            topleft = Point(max(newPoint.x - 100, 0), max(newPoint.y - 100, 0))

            bottomRight = Point(min(newPoint.x + 100, Frame.FRAME_WIDTH), min(newPoint.y + 100, Frame.FRAME_HEIGHT))
            visibleBoxArea = Box(topleft, bottomRight)
            if (visibleBoxArea.area() > maximumArea):
                maximumAreaFrameID = nextFrameID
                maximumArea = visibleBoxArea.area()
            # print("drift:", frameID, str(crabPoint), nextFrameID, str(newPoint), str(drift), visibleBoxArea.area(), str(visibleBoxArea))
            if (newPoint.x <= 0 or newPoint.y <= 0):
                self.__firstFrameID = nextFrameID + 1
                break

            if (newPoint.x >= Frame.FRAME_WIDTH or newPoint.y >= Frame.FRAME_HEIGHT):
                self.__firstFrameID = nextFrameID + 1
                break

            if visibleBoxArea.area() >= 200 * 200:
                # print "thats your last good image of crab"
                self.__frameIDOfFirstGoodImage = nextFrameID

        return maximumAreaFrameID
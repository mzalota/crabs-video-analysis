from math import ceil

from lib.Frame import Frame
from lib.MyTimer import MyTimer
from lib.common import Point, Box


#TODO: SeeFloorSection and Feature classes are very similar. The concepts are not clearly defined/separated. Refactor!

class Feature:
    #__maximumAreaFrameID
    #__frameIDOfFirstGoodImage
    #__frameIDOfLastGoodImage
    #__firstFrameID
    #__lastFrameID

    #__frameID
    #__location

    #__driftData

    def __init__(self, driftData, frameID, location, boxSize):
        # type: (DriftData, int, Point, int) -> Feature
        self.__driftData = driftData
        self.__frameID = frameID
        self.__location = location

        #timer = MyTimer("Feature constructor")

        if frameID > driftData.maxFrameID():
            raise ValueError("Frame Number above maximum. Passed frame: "+str(frameID)+". Maximum frame: "+str(int(driftData.maxFrameID())))
        if frameID < driftData.minFrameID():
            raise ValueError("Frame Number below minimum. Passed frame: "+str(frameID)+". Minimum frame: "+str(int(driftData.minFrameID())))

        #self.__firstFrameID = frameID
        #self.__lastFrameID = frameID
        #timer.lap("shag 40")

        self.__determineFirstAndLastFrameID()
        #print ("firstFrameID and lastFrameID", self.__firstFrameID, self.__lastFrameID)
        #timer.lap("shag 50")

        self.__firstAndLastGoodCrabImages(boxSize)
        #timer.lap("shag 60")


    def getInitFrameID(self):
        return self.__frameID

    def getInitFrameCoordinate(self):
        return self.__location

    def getFirstFrameID(self):
        return self.__firstFrameID

    def getLastFrameID(self):
        return self.__lastFrameID

    def getFirstGoodFrameID(self):
        # type: () -> Point
        if (self.isNeverFullyVisible()):
            num_of_frames_between_middle_and_first = self.getMiddleGoodFrameID() - self.getFirstFrameID()
            return int(ceil(self.getMiddleGoodFrameID() - num_of_frames_between_middle_and_first/2))
        else:
            return self.__frameIDOfFirstGoodImage

    def getLastGoodFrameID(self):
        # type: () -> Point
        if (self.isNeverFullyVisible()):
            num_of_frames_between_middle_and_last = self.getLastFrameID() - self.getMiddleGoodFrameID()
            return int(ceil(self.getLastFrameID() - num_of_frames_between_middle_and_last/ 2))
        else:
            return self.__frameIDOfLastGoodImage

    def getMiddleGoodFrameID(self):
        # type: () -> Point
        if (self.isNeverFullyVisible()):
            return self.__maximumAreaFrameID
        else:
            num_of_frames_between_first_good_and_last_good = self.getLastGoodFrameID() - self.getFirstGoodFrameID()
            return int(ceil(self.getLastGoodFrameID() - num_of_frames_between_first_good_and_last_good/2))


    def isNeverFullyVisible(self):
        return self.__frameIDOfLastGoodImage <= 0 or self.__frameIDOfFirstGoodImage <= 0

    def __firstAndLastGoodCrabImages(self, boxSize):
        self.__frameIDOfFirstGoodImage = 0
        self.__frameIDOfLastGoodImage = 0
        self.__maximumAreaFrameID = self.__frameID

        #timer = MyTimer("In Feature::__firstAndLastGoodCrabImages")

        self.__getValues(self.__firstFrameID, self.__lastFrameID, boxSize)
        #print ("maximumAreaFrameIDDown", self.__maximumAreaFrameID, self.__maximumArea)
        #print ("frameIDOfFirstGoodImage and frameIDOfLastGoodImage", self.__frameIDOfFirstGoodImage, self.__frameIDOfLastGoodImage)
        #timer.lap("after get values")

        if (self.__frameIDOfFirstGoodImage > 0 and self.__frameIDOfLastGoodImage >0):
            return self.__frameIDOfFirstGoodImage, self.__frameIDOfLastGoodImage
        else:
            return self.__maximumAreaFrameID, self.__maximumAreaFrameID

    def __determineFirstAndLastFrameID(self):
        nextFrameID = self.__frameID
        #timer = MyTimer("in Feature::__determineFirstAndLastFrameID")

        loop_counter =0
        while (True):
            nextFrameID = nextFrameID + 1
            if nextFrameID > self.__driftData.maxFrameID():
                self.__lastFrameID = self.__driftData.maxFrameID()
                break

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
            loop_counter += 1

        #timer.lap("after first while: "+str(loop_counter))

        loop_counter =0
        nextFrameID = self.__frameID
        while (True):
            nextFrameID = nextFrameID - 1

            if nextFrameID < self.__driftData.minFrameID():
                self.__firstFrameID = self.__driftData.minFrameID()
                break

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

            loop_counter += 1
        #timer.lap("after second while: "+str(loop_counter))

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

        #timer = MyTimer("__constructVisibleArea")
        offset = int(boxSize / 2)
        newPoint = self.getCoordinateInFrame(nextFrameID)
        #timer.lap("calling Drift Data")
        topleft = Point(max(newPoint.x - offset, 0), max(newPoint.y - offset, 0))
        bottomRight = Point(min(newPoint.x + offset, Frame.FRAME_WIDTH), min(newPoint.y + offset, Frame.FRAME_HEIGHT))
        visibleBoxArea = Box(topleft, bottomRight)

        #timer.lap()
        return visibleBoxArea


    def getCoordinateInFrame(self, frameID):
        # type: (String) -> Point
        drift = self.__driftData.driftBetweenFrames(self.__frameID, frameID)
        newPoint = self.__location.translateBy(drift)
        return newPoint
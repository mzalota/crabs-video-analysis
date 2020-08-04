from abc import ABCMeta, abstractmethod

from lib.Configuration import Configuration
from lib.data.BadFramesData import BadFramesData
from lib.Frame import Frame
from lib.data.CrabsData import CrabsData
from lib.data.MarkersData import MarkersData
from lib.data.SeeFloor import SeeFloor
from lib.VideoStream import VideoStream
from lib.common import Point, Vector, Box


class FrameDecoFactory:

    def __init__(self, seeFloorGeometry, badFramesData, crabsData, markersData, videoStream):
        # type: (SeeFloor, BadFramesData, VideoStream) -> FrameDecoFactory
        self.__videoStream = videoStream
        self.__seeFloorGeometry = seeFloorGeometry
        self.__badFramesData = badFramesData
        self.__crabsData = crabsData
        self.__markersData = markersData

    def getFrame(self, frameID):
        # type: (int) -> FrameDecorator
        return Frame(frameID, self.__videoStream)

    def getFrameDecoGridLines(self, frameDeco, referenceFrameID):
        # type: (FrameDecorator, int) -> DecoGridLines
        frameID = frameDeco.getFrameID()

        centerPointForGrid = self.__centerPointForGrid(frameID, referenceFrameID)
        return DecoGridLines(frameDeco, self.__seeFloorGeometry.getRedDotsData(), centerPointForGrid)

    def __centerPointForGrid(self, frameID, referenceFrameID):
        gridMidPoint = self.__seeFloorGeometry.getRedDotsData().midPoint(referenceFrameID)
        # TODO: change drift calculation to use Seefloor (based on MM) instead of driftData (which uses pixels)
        drift = self.__seeFloorGeometry.getDriftData().driftBetweenFrames(referenceFrameID, frameID)
        newPoint = gridMidPoint.translateBy(drift)
        return newPoint

    def getFrameDecoRedDots(self, frameDeco):
        # type: (FrameDecorator) -> DecoRedDots
        return DecoRedDots(frameDeco, self.__seeFloorGeometry.getRedDotsData())

    def getFrameDecoMarkedCrabs(self, frameDeco):
        # type: (FrameDecorator) -> DecoMarkedCrabs
        return DecoMarkedCrabs(frameDeco, self.__seeFloorGeometry, self.__crabsData)

    def getFrameDecoMarkers(self, frameDeco):
        # type: (FrameDecorator) -> DecoMarkersAbstract
        return DecoMarkersWithNumbers(frameDeco, self.__seeFloorGeometry, self.__markersData)
        #return DecoMarkersWithSymbols(frameDeco, self.__seeFloorGeometry, self.__markersData)

    def getFrameDecoFrameID(self, frameDeco):
        # type: (FrameDecorator) -> DecoFrameID
        return DecoFrameID(frameDeco, self.__seeFloorGeometry.getDriftData(), self.__badFramesData)

class FrameDecorator(object):

    def __init__(self, frameDeco):
        # type: (FrameDecorator) -> FrameDecorator
        self.frameDeco = frameDeco

    def getFrameID(self):
        return self.frameDeco.getFrameID()

    #def getImgObj(self):
    #    # type: () -> Image
    #    return self.frameDeco.getImgObj()

class DecoGridLines(FrameDecorator):

    def __init__(self, frameDeco, redDotsData, startPoint):
        FrameDecorator.__init__(self, frameDeco)
        self.__redDotsData = redDotsData
        self.__startPoint = startPoint

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj().copy()
        frame_id = self.frameDeco.getFrameID()

        distancePix = int(self.__redDotsData.getDistancePixels(frame_id))

        #draw 8 grid squares along X and Y axis.
        for i in range(-4, 4):
            #draw 9 X-lines. One through midpoint between red dots (i=0) and then 4 north-west and 4 south-east
            point = self.__startPoint.translateBy(Vector(i*distancePix, i*distancePix))
            self.__drawGridX(imgObj, point, 0)
        return imgObj

    def __drawGridX(self, imgObj, startingPoint, distancePix):
        verticalTop = Point(startingPoint.x + distancePix, 0)
        verticalBottom = Point(startingPoint.x + distancePix, imgObj.height())
        horisontalLeft = Point(0, startingPoint.y + distancePix)
        horisontalRight = Point(imgObj.width(), startingPoint.y + distancePix)

        imgObj.drawLine(verticalTop, verticalBottom, thickness=3, color=(255, 255, 0))
        imgObj.drawLine(horisontalLeft, horisontalRight, thickness=3, color=(255, 255, 0))

class DecoMarkers_orig(FrameDecorator):

    def __init__(self, frameDeco, seefloorGeometry, markersData):
        # type: (FrameDecorator, SeeFloor, MarkersData) -> DecoMarkers
        FrameDecorator.__init__(self, frameDeco)
        self.__seefloorGeometry = seefloorGeometry
        self.__markersData = markersData

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()
        self.__paintMarkersOnImage(imgObj, self.getFrameID())
        return imgObj

    def __paintMarkersOnImage(self, mainImage, frame_id):
        #timer = MyTimer("MarkersOnFrame")
        markers = self.__markersOnFrame(frame_id)
        if markers is None:
            return

        #timer.lap("drawing markers on frame: " + str(frame_id))
        for marker in markers:
            #print ('marker', marker)
            frame_number = marker['frameNumber']
            marker_id = marker['markerId']

            orig_location = Point(marker['locationX'], marker['locationY'])
            location = self.__seefloorGeometry.translatePointCoordinate(orig_location, frame_number, frame_id)

            self.__drawMarkerOnImage(mainImage, marker_id, location)

        # timer.lap("Number of markers" + str(len(markers)))

    def __drawMarkerOnImage(self, mainImage, marker_id, location):
        config = Configuration()
        color = config.color_for_marker(marker_id)
        if marker_id % 2 == 0:
            # even markers are crosses
            mainImage.drawCross(location, color=color)
        else:
            # odd markers are squares
            box = Box(location.translateBy(Vector(-9, -9)), location.translateBy(Vector(9, 9)))
            mainImage.drawBoxOnImage(box, color=color, thickness=4)

    def __markersOnFrame(self, frame_id):
        # type: (int) -> dict
        prev_frame_id = self.__seefloorGeometry.getPrevFrameMM(frame_id)
        next_frame_id = self.__seefloorGeometry.getNextFrameMM(frame_id)
        return self.__markersData.marksBetweenFrames(prev_frame_id, next_frame_id)


class DecoMarkersAbstract(FrameDecorator):
    __metaclass__ = ABCMeta

    def __init__(self, frameDeco, seefloorGeometry, markersData):
        # type: (FrameDecorator, SeeFloor, MarkersData) -> DecoMarkers
        FrameDecorator.__init__(self, frameDeco)
        self.__seefloorGeometry = seefloorGeometry
        self.__markersData = markersData

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()
        self.__paintMarkersOnImage(imgObj, self.getFrameID())
        return imgObj

    @abstractmethod
    def _drawMarkerOnImage(self, mainImage, marker_id, location):
        pass

    def __paintMarkersOnImage(self, mainImage, frame_id):
        #timer = MyTimer("MarkersOnFrame")
        markers = self.__markersOnFrame(frame_id)
        if markers is None:
            return

        #timer.lap("drawing markers on frame: " + str(frame_id))
        for marker in markers:
            #print ('marker', marker)
            frame_number = marker['frameNumber']
            marker_id = marker['markerId']

            orig_location = Point(marker['locationX'], marker['locationY'])
            location = self.__seefloorGeometry.translatePointCoordinate(orig_location, frame_number, frame_id)

            self._drawMarkerOnImage(mainImage, marker_id, location)

        # timer.lap("Number of markers" + str(len(markers)))

    def __markersOnFrame(self, frame_id):
        # type: (int) -> dict
        prev_frame_id = self.__seefloorGeometry.getPrevFrameMM(frame_id)
        next_frame_id = self.__seefloorGeometry.getNextFrameMM(frame_id)
        return self.__markersData.marksBetweenFrames(prev_frame_id, next_frame_id)


class DecoMarkersWithNumbers(DecoMarkersAbstract):

    def _drawMarkerOnImage(self, mainImage, marker_id, location):
        textBox = self.__determineLocationOfTextBox(location)
        print("marker_id", marker_id, "marker textBox", str(textBox), "location", str(location))
        mainImage.drawTextInBox(textBox, marker_id, color=Configuration.COLOR_LIGHT_BLUE)
        mainImage.drawCross(location, color=Configuration.COLOR_LIGHT_BLUE)

    def __determineLocationOfTextBox(self, location):
        boxHeight = 25
        boxWidth = 50

        if location.y < boxHeight:
            translateYBy = 5
        else:
            translateYBy = (boxHeight + 5)* (-1)

        if location.x < boxWidth:
            translateXBy = 5
        else:
            translateXBy = (boxWidth + 5) * (-1)

        topLeftOfTextBox = location.translateBy(Vector(translateXBy, translateYBy))
        bottomRightOfTextBox = topLeftOfTextBox.translateBy(Vector(boxWidth, boxHeight))
        textBox = Box(topLeftOfTextBox, bottomRightOfTextBox)
        return textBox


class DecoMarkersWithSymbols(DecoMarkersAbstract):

    def _drawMarkerOnImage(self, mainImage, marker_id, location):
        if not str(marker_id).isdigit():
            mainImage.drawCross(location, color=Configuration.COLOR_RED)
            return

        config = Configuration()
        color = config.color_for_marker(int(marker_id))
        if int(marker_id) % 2 == 0:
            # even markers are crosses
            mainImage.drawCross(location, color=color)
        else:
            # odd markers are squares
            box = Box(location.translateBy(Vector(-9, -9)), location.translateBy(Vector(9, 9)))
            mainImage.drawBoxOnImage(box, color=color, thickness=4)




class DecoMarkedCrabs(FrameDecorator):

    def __init__(self, frameDeco, seefloorGeometry, crabsData):
        # type: (FrameDecorator, SeeFloor, CrabsData) -> DecoMarkedCrabs
        FrameDecorator.__init__(self, frameDeco)
        self.__seefloorGeometry = seefloorGeometry
        self.__crabsData = crabsData

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()
        self.__markCrabsOnImage(imgObj, self.getFrameID())
        return imgObj

    def __markCrabsOnImage(self, mainImage, frame_id):
        #timer = MyTimer("crabsOnFrame")
        markedCrabs = self.__crabsOnFrame(frame_id)
        #timer.lap("frame_number: " + str(frame_id))
        for markedCrab in markedCrabs:

            #print ('markedCrab', markedCrab)
            frame_number = markedCrab['frameNumber']

            crabLocationOrig = Point(markedCrab['crabLocationX'], markedCrab['crabLocationY'])

            crabLocation2 = self.__seefloorGeometry.translatePointCoordinate(crabLocationOrig, frame_number,frame_id)
            mainImage.drawCross(crabLocation2, color=(255, 0, 0))

            #print("crabLocation Old", str(crabLocation), "new", str(crabLocation2), "orig", str(crabLocationOrig))
        #timer.lap("Number of crabs" + str(len(markedCrabs)))

    def __crabsOnFrame(self, frame_id):
        # type: (int) -> dict
        prev_frame_id = self.__seefloorGeometry.getPrevFrameMM(frame_id)
        next_frame_id = self.__seefloorGeometry.getNextFrameMM(frame_id)
        markedCrabs = self.__crabsData.crabsBetweenFrames(prev_frame_id, next_frame_id)
        return markedCrabs



class DecoRedDots(FrameDecorator):
    def __init__(self, frameDeco, redDotsData):
        # type: (FrameDecorator, RedDotsData) -> DecoRedDots
        FrameDecorator.__init__(self, frameDeco)
        self.__redDotsData = redDotsData

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()

        redDot1 = self.__redDotsData.getRedDot1(self.getFrameID())
        imgObj.drawCross(redDot1,5, color=(0, 0, 255))

        redDot2 = self.__redDotsData.getRedDot2(self.getFrameID())
        imgObj.drawCross(redDot2,5, color=(0, 0, 255))

        return imgObj


class DecoFrameID(FrameDecorator):
    def __init__(self, frameDeco, driftData, badFramesData):
        # type: (FrameDecorator, DriftData, badFramesData) -> DecoFrameID
        FrameDecorator.__init__(self, frameDeco)
        self.__driftData = driftData
        self.__badFramesData = badFramesData

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()

        frame_name = self.__drawFrameID(self.getFrameID())

        imgObj.drawFrameID(frame_name)
        return imgObj

    def __drawFrameID(self, frame_id):
        # type: (int) -> str
        if frame_id == self.__driftData.minFrameID():
            frame_name = str(int(frame_id)) + " (First)"
        elif frame_id == self.__driftData.maxFrameID():
            frame_name = str(int(frame_id)) + " (Last)"
        elif self.__badFramesData.is_bad_frame(frame_id):
            frame_name = str(int(frame_id)) + " (Bad)"
        else:
            frame_name = int(frame_id)
        return frame_name

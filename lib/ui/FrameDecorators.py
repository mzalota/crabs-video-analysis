from __future__ import annotations

from typing import List, Dict

from lib.imageProcessing.Camera import Camera
from lib.Frame import Frame
from lib.model.Image import Image
from lib.VideoStream import VideoStream
from lib.model.Box import Box
from lib.model.Vector import Vector
from lib.model.Point import Point
from lib.data import RedDotsData
from lib.data.BadFramesData import BadFramesData
from lib.data.CrabsData import CrabsData
from lib.data.MarkersData import MarkersData
from lib.seefloor.SeeFloor import SeeFloor
from lib.imageProcessing.Analyzer import Analyzer
from lib.imageProcessing.Rectificator import Rectificator
from lib.model.Crab import Crab
from lib.ui.MarkersConfiguration import MarkersConfiguration


class FrameDecoFactory:

    def __init__(self, seeFloorGeometry: SeeFloor, badFramesData: BadFramesData, crabsData: CrabsData, markersData: MarkersData, videoStream: VideoStream) -> FrameDecoFactory:
        self.__videoStream = videoStream
        self.__seeFloorGeometry = seeFloorGeometry
        self.__badFramesData = badFramesData
        self.__crabsData = crabsData
        self.__markersData = markersData

    def getFrameDecoRawImage(self, frame_id: int) -> DecoRawImage:
        # type: (FrameDecorator) -> DecoFrameID
        return DecoRawImage(frame_id, self.__videoStream)

    def getFrameDecoUndistortedImage(self, frame_id: int) -> DecoUndistortedImage:
        return DecoUndistortedImage(frame_id, self.__videoStream)

    def getFrameDecoRectifiedImage(self, frame_id: int) -> DecoRectifiedImage:
        return DecoRectifiedImage(frame_id, self.__videoStream)

    # ---
    def getFrameDecoGridLines(self, frameDeco : FrameDecorator, referenceFrameID : int) -> DecoGridLines:
        frameID = frameDeco.getFrameID()

        centerPointForGrid = self.__centerPointForGrid(frameID, referenceFrameID)
        return DecoGridLines(frameDeco, self.__seeFloorGeometry.getRedDotsData(), centerPointForGrid)

    def __centerPointForGrid(self, frameID, referenceFrameID):
        gridMidPoint = self.__seeFloorGeometry.getRedDotsData().midPoint(referenceFrameID)
        return self.__seeFloorGeometry.translatePointCoordinate(gridMidPoint, referenceFrameID, frameID)

    def getFrameDecoRedDots(self, frameDeco: FrameDecorator) -> DecoRedDots:
        return DecoRedDots(frameDeco, self.__seeFloorGeometry.getRedDotsData())

    def getFrameDecoMarkedCrabs(self, frameDeco: FrameDecorator) -> DecoMarkedCrabs:
        return DecoMarkedCrabs(frameDeco, self.__seeFloorGeometry, self.__crabsData)

    def getFrameDecoMarkers(self, frameDeco: FrameDecorator) -> DecoMarkersWithNumbers:
        return DecoMarkersWithNumbers(frameDeco, self.__seeFloorGeometry, self.__markersData)

    def getFrameDecoFrameID(self, frameDeco: FrameDecorator) -> DecoFrameID:
        return DecoFrameID(frameDeco, self.__seeFloorGeometry, self.__badFramesData)

    def getFrameDecoFocusHazeBrigtness(self, frameDeco: FrameDecorator) -> DecoFocusHazeBrightness:
        return DecoFocusHazeBrightness(frameDeco, self.__seeFloorGeometry)

    def getFrameDecoAdjustDrift(self, frameDeco: FrameDecorator, start_point: Point, start_frame_id: int) -> DecoAdjustDrift:
        return DecoAdjustDrift(frameDeco, self.__seeFloorGeometry, start_point, start_frame_id)



#Every FrameDecorator object must implement getImgObj()
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

class DecoMarkersWithNumbers(FrameDecorator):
    # __metaclass__ = ABCMeta

    def __init__(self, frameDeco, seefloorGeometry, markersData):
        # type: (FrameDecorator, SeeFloor, MarkersData) -> DecoMarkers
        FrameDecorator.__init__(self, frameDeco)
        self.__seefloorGeometry = seefloorGeometry
        self.__markersData = markersData
        self.__is_undistorted = False

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()
        self.__paintMarkersOnImage(imgObj, self.getFrameID())
        return imgObj

    def draw_undistorted(self):
        self.__is_undistorted = True

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

            if self.__is_undistorted:
                camera = Camera.create()
                location = camera.undistort_point(location)

            self._drawMarkerOnImage(mainImage, marker_id, location)

        # timer.lap("Number of markers" + str(len(markers)))

    def __markersOnFrame(self, frame_id: int) -> Dict:
        prev_frame_id = self.__seefloorGeometry.getPrevFrame(frame_id)
        next_frame_id = self.__seefloorGeometry.getNextFrame(frame_id)
        print("__markersOnFrame: frame_id",frame_id, "prev_frame_id", prev_frame_id, "next_frame_id", next_frame_id)
        return self.__markersData.marksBetweenFrames(prev_frame_id, next_frame_id)


    def _drawMarkerOnImage(self, mainImage, marker_id, location):
        textBox = self.__determineLocationOfTextBox(location)
        #print("marker_id", marker_id, "marker textBox", str(textBox), "location", str(location))
        mainImage.drawTextInBox(textBox, marker_id, color=MarkersConfiguration.COLOR_LIGHT_BLUE)
        mainImage.drawCross(location, color=MarkersConfiguration.COLOR_LIGHT_BLUE)

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

class DecoRawImage(FrameDecorator):
    def __init__(self, frame_id: int, videoStream: VideoStream) -> DecoRawImage:
        FrameDecorator.__init__(self, Frame(frame_id, videoStream))
        self.__videoStream = videoStream

    def getImgObj(self):
        # type: () -> Image
        return self.__videoStream.read_image_obj(self.getFrameID())

class DecoUndistortedImage(FrameDecorator):
    def __init__(self, frame_id: int, videoStream: VideoStream) -> DecoUndistortedImage:
        FrameDecorator.__init__(self, Frame(frame_id, videoStream))
        self.__videoStream = videoStream

    def getImgObj(self):
        # type: () -> Image
        return self.__videoStream.read_image_undistorted(self.getFrameID())


class DecoRectifiedImage(FrameDecorator):
    def __init__(self, frame_id: int, videoStream: VideoStream) -> DecoRectifiedImage:
        FrameDecorator.__init__(self, Frame(frame_id, videoStream))
        self.__videoStream = videoStream

    def getImgObj(self):
        # type: () -> Image
        Rect = Rectificator(self.__videoStream, self.getFrameID(), True)
        res_img = Rect.generate_rectified_image(self.frameDeco.getImgObj())
        if res_img is None:
            print("Rectification Did not Work")
            return self.__videoStream.read_image_obj(self.getFrameID())
        return res_img


class DecoMarkedCrabs(FrameDecorator):

    def __init__(self, frameDeco, seefloorGeometry, crabsData):
        # type: (FrameDecorator, SeeFloor, CrabsData) -> DecoMarkedCrabs
        FrameDecorator.__init__(self, frameDeco)
        self.__seefloorGeometry = seefloorGeometry
        self.__crabsData = crabsData
        self.__is_undistorted = False

    def draw_undistorted(self):
        self.__is_undistorted = True

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()
        self.__markCrabsOnImage(imgObj, self.getFrameID())
        return imgObj

    def __markCrabsOnImage(self, mainImage: Image, frame_id_image: int):
        #timer = MyTimer("crabsOnFrame")
        markedCrabs = self.__crabs_visible_on_frame(frame_id_image)

        for markedCrab in markedCrabs:
            frame_id_crab_orig = markedCrab.frame_id()
            crabLocationOrig = markedCrab.center()

            crab_location_image = self.__seefloorGeometry.translatePointCoordinate(crabLocationOrig, frame_id_crab_orig, frame_id_image)
            if self.__is_undistorted:
                camera = Camera.create()
                crab_location_image = camera.undistort_point(crab_location_image)

            mainImage.drawCross(crab_location_image, color=(255, 0, 0))

        #timer.lap("Number of crabs" + str(len(markedCrabs)))

    def __crabs_visible_on_frame(self, frame_id: int) -> List[Crab]:
        prev_frame_id = self.__seefloorGeometry.getPrevFrame(frame_id)
        next_frame_id = self.__seefloorGeometry.getNextFrame(frame_id)
        markedCrabs = self.__crabsData.crabs_between_frames(prev_frame_id, next_frame_id)
        return markedCrabs


class DecoAdjustDrift(FrameDecorator):
    def __init__(self, frameDeco, seefloorGeometry, start_point, start_frame_id):
        # type: (FrameDecorator, SeeFloor,  Point, int) -> DecoAdjustDrift
        FrameDecorator.__init__(self, frameDeco)
        self.__seefloorGeometry = seefloorGeometry
        self.__start_point = start_point
        self.__start_frame_id = start_frame_id

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()

        new_location = self.__seefloorGeometry.translatePointCoordinate(self.__start_point, self.__start_frame_id, self.getFrameID())
        #print ("trying to mark manual drift", new_location, self.getFrameID(), self.__start_frame_id)
        imgObj.drawCrossVertical(new_location, size=12)
        return imgObj

class DecoRedDots(FrameDecorator):
    def __init__(self, frameDeco: FrameDecorator, redDotsData: RedDotsData) -> DecoRedDots:
        FrameDecorator.__init__(self, frameDeco)
        self.__redDotsData = redDotsData
        self.__is_undistorted = False

    def draw_undistorted(self):
        self.__is_undistorted = True

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()

        redDot1 = self.__redDotsData.getRedDot1(self.getFrameID())
        redDot2 = self.__redDotsData.getRedDot2(self.getFrameID())

        if self.__is_undistorted:
            camera = Camera.create()
            redDot1 = camera.undistort_point(redDot1)
            redDot2 = camera.undistort_point(redDot2)

        imgObj.drawCross(redDot1,5, color=(0, 0, 255))
        imgObj.drawCross(redDot2, 5, color=(0, 0, 255))

        return imgObj

class DecoFrameID(FrameDecorator):
    def __init__(self, frameDeco, seeFloor, badFramesData):
        # type: (FrameDecorator, SeeFloor, badFramesData) -> DecoFrameID
        FrameDecorator.__init__(self, frameDeco)
        self.__seeFloor = seeFloor
        self.__badFramesData = badFramesData

    def getImgObj(self) -> Image:
        imgObj = self.frameDeco.getImgObj()

        frame_name = self.__drawFrameID(self.getFrameID())

        imgObj.drawFrameID(frame_name)
        return imgObj

    def __drawFrameID(self, frame_id):
        # type: (int) -> str
        if frame_id == self.__seeFloor.minFrameID():
            frame_name = str(int(frame_id)) + " (First)"
        elif frame_id == self.__seeFloor.maxFrameID():
            frame_name = str(int(frame_id)) + " (Last)"
        elif self.__badFramesData.is_bad_frame(frame_id):
            frame_name = str(int(frame_id)) + " (Bad)"
        else:
            frame_name = int(frame_id)
        return frame_name


class DecoFocusHazeBrightness(FrameDecorator):
    def __init__(self, frameDeco, seeFloor):
        # type: (FrameDecorator, SeeFloor) -> DecoFrameID
        FrameDecorator.__init__(self, frameDeco)
        self.__seeFloor = seeFloor

    def getImgObj(self):
        # type: () -> Image
        imgObj = self.frameDeco.getImgObj()
        analyzer = Analyzer(imgObj)
        hase_text = str(round(analyzer.getHazeRatio(), 1))
        focus_text = str(round(analyzer.getFocusRatio(), 1))
        brightness_text = str(round(analyzer.getBrightnessRatio(), 1))
        height_mm = self.__seeFloor.getRedDotsData().get_camera_height_mm(self.getFrameID())
        height_text = str(round(height_mm/1000, 2))+"m"

        title_width = 180
        top_left_point = Point(imgObj.width()-140-title_width, 0)
        text_box = Box(top_left_point, top_left_point.translate_by_xy(100, 100))

        imgObj.drawTextInBox(text_box, "Hase:")
        imgObj.drawTextInBox(text_box.translate_by_xy(title_width, 0), hase_text)

        text_box = text_box.translate_by_xy(0, 50)
        imgObj.drawTextInBox(text_box, "Focus:")
        imgObj.drawTextInBox(text_box.translate_by_xy(title_width, 0), focus_text)

        text_box = text_box.translate_by_xy(0, 50)
        imgObj.drawTextInBox(text_box, "Brightness:")
        imgObj.drawTextInBox(text_box.translate_by_xy(title_width, 0), brightness_text)

        text_box = text_box.translate_by_xy(0, 50)
        imgObj.drawTextInBox(text_box, "Height:")
        imgObj.drawTextInBox(text_box.translate_by_xy(title_width, 0), height_text)

        return imgObj

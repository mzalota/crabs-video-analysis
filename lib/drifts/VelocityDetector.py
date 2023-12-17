from __future__ import annotations

import math
from typing import List

import numpy

from lib.Frame import Frame
from lib.VideoStream import VideoStreamException
from lib.drifts.FeatureMatcher import FeatureMatcher
from lib.infra.MyTimer import MyTimer
from lib.model.Box import Box
from lib.model.Image import Image
from lib.model.Point import Point
from lib.model.Vector import Vector
from lib.ui.ImageWindow import ImageWindow


class ToMoveToFeatureMatcher:
    def __isAbsoluteValueMoreThanTwiceBig(self, thisValue, medianValue):
        if math.fabs(thisValue) > math.fabs(medianValue) * 2:
            return True
        else:
            return False

    def excludeOutliers(self, driftsOld):
        if len(driftsOld) <= 0:
            return None

        medianLength = Vector.medianLengthOfVectorArray(driftsOld)

        driftsNew = list()
        for drift in driftsOld:
            #if drift.isZeroVector():
            #    continue

            if drift.y > 150:
                # the ship is not going to move that fast
                continue

            if drift.y < -30:
                # the ship is not going to move backward faster that -30...
                continue

            # print "medianLength "+str(medianLength)+ " drift.length() "+str(drift.length())+ " div two "+ str(medianLength / 2)
            if (self.__isAbsoluteValueMoreThanTwiceBig(drift.length(), medianLength)):
                continue

            driftsNew.append(drift)

        return driftsNew

    def _getMedianDriftVector_toMove(self, drifts: List) ->Vector:

        withoutOutliers = self.excludeOutliers(drifts)
        if not withoutOutliers:
            return None

        if len(withoutOutliers) <= 0:
            return None

        driftX = list()
        driftY = list()
        for drift in withoutOutliers:
            #if not drift.isZeroVector():
            driftX.append(drift.x)
            driftY.append(drift.y)

        medianXDrift = numpy.median(driftX)
        medianYDrift = numpy.median(driftY)
        return Vector(medianXDrift, medianYDrift)


class VelocityDetector(ToMoveToFeatureMatcher):
    def __init__(self, is_debug: bool = False):
        self._timer = MyTimer("VelocityDetector")
        self.__is_debug = is_debug

    def runLoop(self, frameID: int, stepSize: int, logger, videoStream):
        self.__createFeatureMatchers(Frame.is_high_resolution(videoStream.frame_height()))

        if self.__is_debug:
            self.__ui_window = ImageWindow("mainWindow", Point(700, 200))

        prevFrameID = frameID
        success = True
        while success:
            if frameID > videoStream.num_of_frames():
                break

            if (prevFrameID == frameID):
                print("this is the first frame in the video stream")
                self._write_out_empty_row(frameID, logger)
                prevFrameID = frameID
                frameID += stepSize
                continue

            frame = Frame(frameID, videoStream)
            try:
                #try to read frame from video stream
                current_image = frame.getImgObj()
            except VideoStreamException as error:
                print("WARN: Cannot read frame id:" + str(frameID) + ", skipping to next")
                # print(repr(error))
                self._write_out_empty_row(frameID, logger)
                self.reset_all_fm()
                prevFrameID = frameID
                frameID += stepSize
                continue

            framePrev = Frame(prevFrameID, videoStream)
            try:
                #try to read frame from video stream
                prev_image = framePrev.getImgObj()
            except VideoStreamException as error:
                print("WARN: Cannot read previous frame id:" + str(prevFrameID) + ", skipping current frame "+str(frameID)+" to next")
                # print(repr(error))
                self._write_out_empty_row(frameID, logger)
                self.reset_all_fm()
                prevFrameID = frameID
                frameID += stepSize
                continue

            if current_image.is_identical_to(prev_image):
                print("WARN: the image in this frame, "+str(frameID)+", is identical to image in previous frame, "+str(prevFrameID))
                self._write_out_empty_row(frameID, logger)
                self.reset_all_fm()
                prevFrameID = frameID
                frameID += stepSize
                continue

            drifts = self.detectVelocity(frame)
            self._write_out_drift_row(frameID, logger, drifts)
            driftVector = self.__getMedianDriftVector(drifts)

            if self.__is_debug:
                self.__show_ui_window(self._fm.values(), frame.getImgObj(), driftVector)

            prevFrameID = frameID
            frameID += stepSize

        if self.__is_debug:
            self.__ui_window.closeWindow()


    def _write_out_drift_row(self, frameID, logger, drifts: List):
        driftVector = self.__getMedianDriftVector(drifts)
        if driftVector is None:
            self._write_out_empty_row(frameID, logger, drifts)
            return

        driftsRow = self.infoAboutDrift(frameID, drifts)
        print(driftsRow)
        logger.writeToFile(driftsRow)

    def _write_out_empty_row(self, frameID, logger, drifts=list()):
        driftsRow = self.emptyRow(frameID, drifts)
        print(driftsRow)
        logger.writeToFile(driftsRow)

    def __show_ui_window(self, feature_matchers, img: Image, drift_vector_median: Vector):
        for feature_matcher in feature_matchers:
            section = feature_matcher.seefloor_section()
            if (section is None):
                # we did not initialize the seefloor_section in this feature_matcher yet
                continue

            if feature_matcher.detectionWasReset():
                color = (0, 255, 255)  # draw box in yellow color when it is reset
            else:
                color = (0, 255, 0)  # green

            #TODO: why are we calling section if FeaturMatcher was reset?
            box_to_draw = section.box_around_feature()
            img.drawBoxOnImage(box_to_draw, color=color, thickness=4)

            #draw drift vector in the middle of the box
            if not feature_matcher.drift_is_valid():
                continue

            if not section.detection_was_successful():
                continue

            drift_vector = section.get_detected_drift()
            img.drawDriftVectorOnImage(drift_vector, box_to_draw.centerPoint())

            if drift_vector_median is None:
                continue

            #draw difference to drift_vector_median (shows how drift detected by this FeatureMatcher differs from median drift)
            draw_starting_point_up = box_to_draw.centerPoint().translateBy(Vector(-50, -50))
            drift_contribution_of_this_feature_matcher = drift_vector.minus(drift_vector_median)
            img.drawDriftVectorOnImage(drift_contribution_of_this_feature_matcher, draw_starting_point_up)

            # draw difference to drift_vector_median but exaggerate the x dimension 10-fold and y dimention 2 fold.
            draw_starting_point_down = box_to_draw.centerPoint().translateBy(Vector(50, 50))
            without_drift_elongated = Point(drift_contribution_of_this_feature_matcher.x*10, drift_contribution_of_this_feature_matcher.y*10)
            img.drawDriftVectorOnImage(without_drift_elongated, draw_starting_point_down)

        self.__ui_window.showWindowAndWait(img.asNumpyArray())

    def __createFeatureMatchers(self, is_high_resolution: bool):

        # __FRAME_HEIGHT_LOW_RES = 1080
        # __FRAME_WIDTH_LOW_RES = 1920

        # _FRAME_HEIGHT_HIGH_RES = 2048  # diff from low res is 968
        # __FRAME_WIDTH_HIGH_RES = 3072 # diff from low res is 1152

        if is_high_resolution:
            hi_res_hight_diff = 968
            hi_res_width_diff = 1152
        else:
            hi_res_hight_diff = 0
            hi_res_width_diff = 0

        self._fm = dict()
        # Boxes on the left side
        self._fm[0] = FeatureMatcher(Box(Point(200, 100), Point(200 + 600, 100 + 400)))  # left top
        self._fm[1] = FeatureMatcher(Box(Point(300, 400 + hi_res_hight_diff / 2), Point(300 + 200,
                                                                                          400 + hi_res_hight_diff / 2 + 350)))  # left middle, taller one
        self._fm[2] = FeatureMatcher(Box(Point(200, 650 + hi_res_hight_diff / 2), Point(200 + 300,
                                                                                          650 + hi_res_hight_diff / 2 + 200)))  # left middle, wider one

        # Boxes in the middle
        self._fm[3] = FeatureMatcher(Box(Point(700 + hi_res_width_diff / 2, 600 + hi_res_hight_diff / 2),
                      Point(700 + hi_res_width_diff / 2 + 400, 600 + hi_res_hight_diff / 2 + 200)))  # center over red dots

        self._fm[4] = FeatureMatcher(Box(Point(800 + hi_res_width_diff / 2, 100), Point(800 + hi_res_width_diff / 2 + 300, 100 + 200)))  # middle top
        self._fm[5] = FeatureMatcher(Box(Point(800 + hi_res_width_diff, 300 + hi_res_hight_diff),
                        Point(800 + hi_res_width_diff + 300,  300 + hi_res_hight_diff + 100)))  # between center box and "right middle" box

        # boxes on the right side
        self._fm[6] = FeatureMatcher(Box(Point(1250 + hi_res_width_diff, 650 + hi_res_hight_diff / 2),
                                           Point(1250 + hi_res_width_diff + 300,
                                                 650 + hi_res_hight_diff / 2 + 200))) # right middle
        self._fm[7] = FeatureMatcher(Box(Point(1250 + hi_res_width_diff, 125),
                                           Point(1250 + hi_res_width_diff + 200, 125 + 400)))  # right top, taller
        self._fm[8] = FeatureMatcher(Box(Point(1200 + hi_res_width_diff, 300),
                                           Point(1200 + hi_res_width_diff + 500, 300 + 300)))  # right top, wider

    def getMedianDriftDistance(self, drifts):
        if len(drifts) <= 0:
            return None

        driftPixels = list()
        for drift in drifts:
            driftPixels.append(drift.length())
        return numpy.median(driftPixels)

    def getMedianDriftAngle(self, drifts):
        if len(drifts) <= 0:
            return None

        driftAngles = list()
        for drift in drifts:
            driftAngles.append(drift.angle())
        return numpy.median(driftAngles)

    def _isNegative(self, number):
        if number < 0:
            return True
        else:
            return False

    def __bothHaveSameSign(self, number1, number2):
        if number1 == 0 and number2 == 0:
            return True

        if number1 == 0 or number2 == 0:
            # zero is neither negative nor positive. So if one number is zero, then the two numbers have SAME sign
            return False

        if self._isNegative(number1) and self._isNegative(number2):
            return True
        if not self._isNegative(number1) and not self._isNegative(number2):
            return True
        else:
            return False

    def replaceOutlier(self, prev_prev, prev, this, next, next_next):

        diff1 = prev - prev_prev
        diff2 = this - prev
        diff3 = next - this
        diff4 = next_next - next

        if abs(diff2) > 30 and abs(diff3) > 30:
            # this is outlier
            return prev + int(next - prev) / 2

        return this

    def __getMedianDriftVector(self, drifts: List) ->Vector:
        return self._getMedianDriftVector_toMove(drifts)

    def reset_all_fm(self):
        for fm_id, fm in self._fm.items():
            fm.reset_to_starting_box()

    def detectVelocity(self, frame: Frame) -> List:
        drifts = list()
        for fm_id, fm in self._fm.items():
            fm.detectSeeFloorSection(frame.getImgObj())
            if not fm.drift_is_valid():
                continue

            section = fm.seefloor_section()
            if not section.detection_was_successful():
                continue

            drift = section.get_detected_drift()
            drifts.append(drift)

        self._timer.lap("in detectVelocity() sequential end")
        return drifts

    def infoAboutDrift(self, frame_id: int, drifts: List):
        driftVector = self.__getMedianDriftVector(drifts)
        driftDistance = self.getMedianDriftDistance(drifts)
        driftAngle = self.getMedianDriftAngle(drifts)
        driftsCount = len(drifts)
        driftsStr = Vector.vectorArrayAsString(drifts)
        driftsWithoutOutliers = list() #self.excludeOutliers(self._drifts)
        driftsNoOutliersStr = Vector.vectorArrayAsString(driftsWithoutOutliers)

        driftsRow = []
        if driftsStr:
            driftsRow.append(frame_id)
            driftsRow.append(driftVector.x)
            driftsRow.append(driftVector.y)
            driftsRow.append(driftDistance)
            driftsRow.append(driftAngle)
            driftsRow.append(len(driftsWithoutOutliers))
            driftsRow.append(driftsCount)
            driftsRow.append(driftsStr)
            driftsRow.append(driftsNoOutliersStr)
            driftsRow.append("DETECTED_DRIFTS")
            for idx in range(0, 9):
                section = self._fm[idx].seefloor_section()
                box = section.box_around_feature()
                driftsRow.append(box.topLeft.x)
                driftsRow.append(box.topLeft.y)
                driftsRow.append(box.bottomRight.x)
                driftsRow.append(box.bottomRight.y)
                # if section.detection_was_successfull():
                if self._fm[idx].drift_is_valid():
                    drift = section.get_detected_drift()
                    driftsRow.append("DETECTED")
                    driftsRow.append(drift.x)
                    driftsRow.append(drift.y)
                else:
                    driftsRow.append("FAILED")
                    driftsRow.append(0)
                    driftsRow.append(0)

        return driftsRow

    def emptyRow(self, frame_id: int, drifts: List):
        row = []
        row.append(frame_id)
        row.append(-888)
        row.append(-999)
        row.append(-777)
        row.append(-45)
        row.append(0)
        row.append(len(drifts))
        row.append("")
        row.append(Vector.vectorArrayAsString(drifts))
        row.append("EMPTY_DRIFTS")
        return row

    @staticmethod
    def infoHeaders():
        row = []
        row.append("frameNumber")
        row.append("driftX")
        row.append("driftY")
        row.append("driftDistance")
        row.append("driftAngle")
        row.append("driftsCountNoOutliers")
        row.append("driftsCount")
        row.append("drifts")
        row.append("driftsNoOutliers")
        row.append("outlier")

        row.append("fm_0_top_x")
        row.append("fm_0_top_y")
        row.append("fm_0_bottom_x")
        row.append("fm_0_bottom_y")
        row.append("fm_0_result")
        row.append("fm_0_drift_x")
        row.append("fm_0_drift_y")

        row.append("fm_1_top_x")
        row.append("fm_1_top_y")
        row.append("fm_1_bottom_x")
        row.append("fm_1_bottom_y")
        row.append("fm_1_result")
        row.append("fm_1_drift_x")
        row.append("fm_1_drift_y")

        row.append("fm_2_top_x")
        row.append("fm_2_top_y")
        row.append("fm_2_bottom_x")
        row.append("fm_2_bottom_y")
        row.append("fm_2_result")
        row.append("fm_2_drift_x")
        row.append("fm_2_drift_y")

        row.append("fm_3_top_x")
        row.append("fm_3_top_y")
        row.append("fm_3_bottom_x")
        row.append("fm_3_bottom_y")
        row.append("fm_3_result")
        row.append("fm_3_drift_x")
        row.append("fm_3_drift_y")

        row.append("fm_4_top_x")
        row.append("fm_4_top_y")
        row.append("fm_4_bottom_x")
        row.append("fm_4_bottom_y")
        row.append("fm_4_result")
        row.append("fm_4_drift_x")
        row.append("fm_4_drift_y")

        row.append("fm_5_top_x")
        row.append("fm_5_top_y")
        row.append("fm_5_bottom_x")
        row.append("fm_5_bottom_y")
        row.append("fm_5_result")
        row.append("fm_5_drift_x")
        row.append("fm_5_drift_y")

        row.append("fm_6_top_x")
        row.append("fm_6_top_y")
        row.append("fm_6_bottom_x")
        row.append("fm_6_bottom_y")
        row.append("fm_6_result")
        row.append("fm_6_drift_x")
        row.append("fm_6_drift_y")

        row.append("fm_7_top_x")
        row.append("fm_7_top_y")
        row.append("fm_7_bottom_x")
        row.append("fm_7_bottom_y")
        row.append("fm_7_result")
        row.append("fm_7_drift_x")
        row.append("fm_7_drift_y")

        row.append("fm_8_top_x")
        row.append("fm_8_top_y")
        row.append("fm_8_bottom_x")
        row.append("fm_8_bottom_y")
        row.append("fm_8_result")
        row.append("fm_8_drift_x")
        row.append("fm_8_drift_y")

        return row

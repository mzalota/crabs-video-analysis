import math
import traceback

import numpy

from lib.drifts.FeatureMatcher import FeatureMatcher
from lib.common import Box, Point, Vector
from lib.Frame import Frame
from lib.ImageWindow import ImageWindow
from lib.infra.MyTimer import MyTimer
from lib.VideoStream import VideoStreamException


class VelocityDetector():
    def __init__(self, is_debug = False):
        # type: () -> VelocityDetector
        self._prevFrame = None
        self._timer = MyTimer("VelocityDetector")
        self.__is_debug = is_debug

    def runLoop(self, frameID, stepSize, logger, videoStream):
        self.__createFeatureMatchers(Frame.is_high_resolution(videoStream.frame_height()))

        if self.__is_debug:
            self.__ui_window = ImageWindow("mainWindow", Point(700, 200))

        success = True
        while success:
            try:
                frame = Frame(frameID, videoStream)
                self.detectVelocity(frame)
            except VideoStreamException as error:
                if frameID > 1000:
                    print ("no more frames to read from video ")
                    print(repr(error))
                    # traceback.print_exc()
                    break
                else:
                    print("cannot read frame " + str(frameID) + ", skipping to next")
                    frameID += stepSize
                    continue

            except Exception as error:
                print('Caught this error: ' + repr(error))
                traceback.print_exc()
                break
            except AssertionError as assertion:
                print('Caught this assertion: ' + repr(assertion))
                traceback.print_exc()
                break

            driftVector = self.__getMedianDriftVector()
            if driftVector is None:
                driftsRow = self.emptyRow(frameID)
            else:
                driftsRow = self.infoAboutDrift(frameID)

            print(driftsRow)
            logger.writeToFile(driftsRow)

            if self.__is_debug:
                self.__show_ui_window(self._fm.values(), frame, driftVector)

            frameID += stepSize

            if frameID > 99100:
                break

        if self.__is_debug:
            self.__ui_window.closeWindow()

    def __show_ui_window(self, feature_matchers, frame, driftVector):
        img = frame.getImgObj()
        for feature_matcher in feature_matchers:
            if feature_matcher.detectionWasReset():
                color = (0, 255, 255) # draw box in yellow color when it is reset
            else:
                color = (0, 255, 0)
                drift_vector = feature_matcher.seefloor_section().getDrift()
                draw_starting_point = feature_matcher.seefloor_section().getLocation()
                img.drawDriftVectorOnImage(drift_vector, draw_starting_point)

                if driftVector is not None:
                    vector_shift_up = Vector(0, -50)
                    # vector_shift_up = Vector(0, 0)
                    draw_starting_point2 = draw_starting_point.translateBy(vector_shift_up)
                    without_drift = drift_vector.asPoint().translateBy(Vector(-driftVector.x, -driftVector.y))
                    img.drawDriftVectorOnImage(without_drift, draw_starting_point2)

                    without_drift_elongated = Point(without_drift.x*20, without_drift.y)
                    draw_starting_point3 = draw_starting_point2.translateBy(Vector(-without_drift_elongated.x, -without_drift_elongated.y))
                    img.drawDriftVectorOnImage(without_drift_elongated, draw_starting_point3)


            img.drawBoxOnImage(feature_matcher.seefloor_section().box_around_feature(), color=color, thickness=4)

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

    def getMedianDriftDistance(self):
        if len(self._drifts) <= 0:
            return None

        driftPixels = list()
        for drift in self._drifts:
            driftPixels.append(drift.length())
        return numpy.median(driftPixels)

    def getMedianDriftAngle(self):
        if len(self._drifts) <= 0:
            return None

        driftAngles = list()
        for drift in self._drifts:
            driftAngles.append(drift.angle())
        return numpy.median(driftAngles)

    def __isAbsoluteValueMoreThanTwiceBig(self, thisValue, medianValue):
        if math.fabs(thisValue) > math.fabs(medianValue) * 2:
            return True
        else:
            return False

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

    def __getMedianDriftVector(self):
        # type: () -> Vector
        withoutOutliers = self.excludeOutliers(self._drifts)
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

    def detectVelocity(self, frame: Frame):
        self._timer.lap("in detectVelocity() sequential start")
        self._drifts = list()
        for fm_id, fm in self._fm.items():
            # TODO: If the next line is moved one down we get exception for video files that don't have first frame
            #imgObj = frame.getImgObj()
            fm.detectSeeFloorSection(frame)
            section = fm.seefloor_section()
            #section.drawFeatureOnFrame(imgObj)
            if fm.detectionWasReset():
                continue

            drift = section.getDrift()
            if not drift:
                continue

            self._drifts.append(drift)

        self._prevFrame = frame
        self._timer.lap("in detectVelocity() sequential end")

    def getDriftsAsString(self):
        return Vector.vectorArrayAsString(self._drifts)

    def getDriftsCount(self):
        return len(self._drifts)

    def infoAboutDrift(self, frame_id):
        driftVector = self.__getMedianDriftVector()
        driftDistance = self.getMedianDriftDistance()
        driftAngle = self.getMedianDriftAngle()
        driftsCount = self.getDriftsCount()
        driftsStr = self.getDriftsAsString()
        driftsWithoutOutliers = self.excludeOutliers(self._drifts)
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
                drift = section.getDrift()
                driftsRow.append(box.topLeft.x)
                driftsRow.append(box.topLeft.y)
                driftsRow.append(box.bottomRight.x)
                driftsRow.append(box.bottomRight.y)
                # driftsRow.append(box.centerPoint().x)
                # driftsRow.append(box.centerPoint().y)
                if section.drift_was_detected():
                    driftsRow.append("DETECTED")
                    driftsRow.append(drift.x)
                    driftsRow.append(drift.y)
                else:
                    driftsRow.append("FAILED")
                    driftsRow.append(0)
                    driftsRow.append(0)

        return driftsRow

    def emptyRow(self, frame_id):
        row = []
        row.append(frame_id)
        row.append(-888)
        row.append(-999)
        row.append(-777)
        row.append(-45)
        row.append(0)
        row.append(self.getDriftsCount())
        row.append("")
        row.append(self.getDriftsAsString())
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

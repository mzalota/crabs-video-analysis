import math
import traceback

import numpy

from lib.FeatureMatcher import FeatureMatcher
from Image import Image
from common import Box, Point, Vector
from lib.Frame import Frame
from lib.ImageWindow import ImageWindow
from lib.MyTimer import MyTimer
from lib.VideoStream import VideoStreamException, VideoStream


class VelocityDetector():
    def __init__(self):
        # type: () -> VelocityDetector
        self._prevFrame = None
        self._timer = MyTimer("VelocityDetector")
        self.__ui_window = ImageWindow("mainWindow", Point(700, 200))
        # self.__createFeatureMatchers()

    def runLoop(self, frameID, stepSize, logger, videoStream):
        self.__createFeatureMatchers(videoStream)

        success = True
        while success:
            try:
                frame = Frame(frameID, videoStream)
                self.detectVelocity(frame)
            except VideoStreamException as error:
                if frameID > 300:
                    print ("no more frames to read from video ")
                    print(repr(error))
                    # traceback.print_exc()
                    break
                else:
                    print "cannot read frame " + str(frameID) + ", skipping to next"
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

            driftVector = self.getMedianDriftVector()
            if driftVector is None:
                driftsRow = self.emptyRow(frameID)
            else:
                driftsRow = self.infoAboutDrift(frameID)

            print driftsRow
            logger.writeToFile(driftsRow)

            self.__show_ui_window(driftVector, self._fm, frame)

            frameID += stepSize

            if frameID > 99100:
                break

        self.__ui_window.closeWindow()

    def __show_ui_window(self, driftVector, feature_matchers, frame):
        img = frame.getImgObj()
        # img.drawDriftVectorOnImage(driftVector)
        for feature_matcher in feature_matchers:
            if feature_matcher.detectionWasReset():
                color = (0, 255, 255) # draw box in yellow color when it is reset
            else:
                color = (0, 255, 0)
            img.drawBoxOnImage(feature_matcher.seefloor_section().box_around_feature(), color=color, thickness=4)

        self.__ui_window.showWindowAndWait(img.asNumpyArray())

    def __createFeatureMatchers(self, videoStream):
        self._fm = list()

        # __FRAME_HEIGHT_LOW_RES = 1080
        # __FRAME_WIDTH_LOW_RES = 1920

        # _FRAME_HEIGHT_HIGH_RES = 2048  # diff from low res is 968
        # __FRAME_WIDTH_HIGH_RES = 3072 # diff from low res is 1152

        # TODO: Reuse Frame.is_high_resolution() function instead of reimplementing comparison here
        if videoStream.frame_height() >= Frame._FRAME_HEIGHT_HIGH_RES:
            hi_res_hight_diff = 968
            hi_res_width_diff = 1152
        else:
            hi_res_hight_diff = 0
            hi_res_width_diff = 0

        # Boxes on the left side
        self._fm.append(FeatureMatcher(Box(Point(200, 50), Point(200 + 600, 50 + 400))))  # left top
        self._fm.append(FeatureMatcher(Box(Point(300, 400 + hi_res_hight_diff / 2), Point(300 + 200,
                                                                                          400 + hi_res_hight_diff / 2 + 350))))  # left middle, taller one
        self._fm.append(FeatureMatcher(Box(Point(200, 650 + hi_res_hight_diff / 2), Point(200 + 300,
                                                                                          650 + hi_res_hight_diff / 2 + 200))))  # left middle, wider one

        # Boxes in the middle
        self._fm.append(FeatureMatcher(Box(Point(700 + hi_res_width_diff / 2, 600 + hi_res_hight_diff / 2),
                                           Point(700 + hi_res_width_diff / 2 + 400,
                                                 600 + hi_res_hight_diff / 2 + 300))))  # center over red dots
        self._fm.append(FeatureMatcher(Box(Point(800 + hi_res_width_diff / 2, 50),
                                           Point(800 + hi_res_width_diff / 2 + 300, 50 + 200))))  # middle top
        self._fm.append(FeatureMatcher(Box(Point(800 + hi_res_width_diff, 300 + hi_res_hight_diff),
                                           Point(800 + hi_res_width_diff + 300,
                                                 300 + hi_res_hight_diff + 200))))  # between center box and "right middle" box

        # boxes on the right side
        self._fm.append(FeatureMatcher(Box(Point(1250 + hi_res_width_diff, 650 + hi_res_hight_diff / 2),
                                           Point(1250 + hi_res_width_diff + 300,
                                                 650 + hi_res_hight_diff / 2 + 200))))  # right middle
        self._fm.append(FeatureMatcher(Box(Point(1250 + hi_res_width_diff, 125),
                                           Point(1250 + hi_res_width_diff + 200, 125 + 400))))  # right top, taller
        self._fm.append(FeatureMatcher(Box(Point(1200 + hi_res_width_diff, 300),
                                           Point(1200 + hi_res_width_diff + 500, 300 + 300))))  # right top, wider

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
            if drift.isZeroVector():
                continue

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

    def getMedianDriftVector(self):

        withoutOutliers = self.excludeOutliers(self._drifts)
        if not withoutOutliers:
            return None

        if len(withoutOutliers) <= 0:
            return None

        driftX = list()
        driftY = list()

        for drift in withoutOutliers:
            if not drift.isZeroVector():
                driftX.append(drift.x)
                driftY.append(drift.y)

        medianXDrift = numpy.median(driftX)
        medianYDrift = numpy.median(driftY)
        return Vector(medianXDrift, medianYDrift)

    def detectVelocity(self, frame):
        self._timer.lap("in detectVelocity() sequential start")
        self._drifts = list()
        for fm in self._fm:
            # TODO: If the next line is moved one down we get exception for video files that don't have first frame
            imgObj = frame.getImgObj()
            section = fm.detectSeeFloorSection(frame)
            section.drawFeatureOnFrame(imgObj)
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
        driftVector = self.getMedianDriftVector()
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
        return row

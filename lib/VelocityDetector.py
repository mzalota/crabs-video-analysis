import math
import traceback

import numpy

from lib.FeatureMatcher import FeatureMatcher
from Image import Image
from common import Box, Point, Vector
from lib.Frame import Frame
from lib.MyTimer import MyTimer
from lib.VideoStream import VideoStreamException, VideoStream


class VelocityDetector():
    def __init__(self, folderStruct):
        # type: (FolderStructure) -> VelocityDetector
        self._prevFrame = None
        self._timer = MyTimer("VelocityDetector")
        self.__createFeatureMatchers()
        self.__videoStream = VideoStream(folderStruct.getVideoFilepath())

    def runLoop(self, frameID, stepSize, logger):
        success = True
        while success:

            #windowName = 'Detected_' + str(frameID)

            try:
                frame = Frame(frameID, self.__videoStream)
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

            # findBrightestSpot()

            driftVector = self.getMedianDriftVector()
            if driftVector is None:
                driftsRow = self.emptyRow()
                driftsRow.insert(0, frameID)
            else:
                driftLength = driftVector.length()
                driftsRow = self.infoAboutDrift()
                driftsRow.insert(0, frameID)

            print driftsRow
            logger.writeToFile(driftsRow)

            img = frame.getImgObj()
            img.drawDriftVectorOnImage(driftVector)

            # imageWin.showWindowAndWait(img.asNumpyArray(), 1000)
            # imageWin.showWindowAndWaitForClick(img.asNumpyArray())

            frameID += stepSize

            if frameID > 99100:
                break


    def __createFeatureMatchers(self):
        self._fm = list()
        self._fm.append(FeatureMatcher(Box(Point(1250, 650), Point(1250 + 300, 650 + 200)))) # middle right
        self._fm.append(FeatureMatcher(Box(Point(700, 600), Point(700 + 400, 600 + 300))))  # center
        self._fm.append(FeatureMatcher(Box(Point(1250, 125), Point(1450 + 200, 125 + 400)))) #top right
        self._fm.append(FeatureMatcher(Box(Point(1200, 300), Point(1200 + 500, 300 + 300)))) #top right
        self._fm.append(FeatureMatcher(Box(Point(200, 50), Point(200 + 600, 50 + 400))))
        self._fm.append(FeatureMatcher(Box(Point(800, 50), Point(800 + 300, 50 + 200))))
        self._fm.append(FeatureMatcher(Box(Point(300, 400), Point(300 + 250, 400 + 350)))) # middle left
        self._fm.append(FeatureMatcher(Box(Point(800, 300), Point(800 + 300, 300 + 200))))
        self._fm.append(FeatureMatcher(Box(Point(200, 650), Point(200 + 300, 650 + 200))))

    def getMedianDriftDistance(self):
        if len(self._drifts)<=0:
            return None

        driftPixels = list()
        for drift in self._drifts:
            driftPixels.append(drift.length())
        return numpy.median(driftPixels)

    def getMedianDriftAngle(self):
        if len(self._drifts)<=0:
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
            #zero is neither negative nor positive. So if one number is zero, then the two numbers have SAME sign
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
            #this is outlier
            return prev + int(next-prev)/2

        return this


    def excludeOutliers(self, driftsOld):
        if len(driftsOld)<=0:
            return None

        medianLength = Vector.medianLengthOfVectorArray(driftsOld)

        driftsNew = list()
        for drift in driftsOld:
            if  drift.isZeroVector():
                continue

            if drift.y >150:
                #the ship is not going to move that fast
                continue

            if drift.y < -30:
                #the ship is not going to move backward faster that -30...
                continue

            #print "medianLength "+str(medianLength)+ " drift.length() "+str(drift.length())+ " div two "+ str(medianLength / 2)
            if (self.__isAbsoluteValueMoreThanTwiceBig(drift.length(),medianLength)):
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
            section = fm.detectSeeFloorSections(frame)
            section.drawFeatureOnFrame(imgObj)
            if fm.detectionWasReset():
                continue

            drift = section.getDrift()
            if not drift:
                continue

            self._drifts.append(drift)

            # section.showSubImage()

        self._prevFrame = frame
        self._timer.lap("in detectVelocity() sequential end")

    def getDriftsAsString(self):
        return Vector.vectorArrayAsString(self._drifts)

    def getDriftsCount(self):
        return len(self._drifts)

    def infoAboutDrift(self):
        driftVector = self.getMedianDriftVector()
        driftDistance = self.getMedianDriftDistance()
        driftAngle = self.getMedianDriftAngle()
        driftsCount = self.getDriftsCount()
        driftsStr = self.getDriftsAsString()
        driftsWithoutOutliers = self.excludeOutliers(self._drifts)
        driftsNoOutliersStr = Vector.vectorArrayAsString(driftsWithoutOutliers)

        driftsRow = []
        if driftsStr:
            driftsRow.append(driftVector.x)
            driftsRow.append(driftVector.y)
            driftsRow.append(driftDistance)
            driftsRow.append(driftAngle)
            driftsRow.append(len(driftsWithoutOutliers))
            driftsRow.append(driftsCount)
            driftsRow.append(driftsStr)
            driftsRow.append(driftsNoOutliersStr)

        return driftsRow

    def emptyRow(self):
        row = []
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

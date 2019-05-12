import math

import numpy

from FeatureMatcher import FeatureMatcher
from Image import Image
from common import Box, Point, Vector


class VelocityDetector():
    def __init__(self):
        self.__prevFrame = None
        self.__fm = list()

        self.__fm.append(FeatureMatcher(Box(Point(1250,75), Point(1250 + 100, 75 + 200))))
        self.__fm.append(FeatureMatcher(Box(Point(1250, 75), Point(1350 + 100, 75 + 100))))
        self.__fm.append(FeatureMatcher(Box(Point(1250, 75), Point(1450 + 200, 75 + 100))))
        self.__fm.append(FeatureMatcher(Box(Point(1300, 100), Point(1300 + 500, 100 + 300))))
        self.__fm.append(FeatureMatcher(Box(Point(200, 50), Point(200 + 600, 50 + 400))))
        self.__fm.append(FeatureMatcher(Box(Point(800, 50), Point(800 + 300, 50 + 200))))

        self.__fm.append(FeatureMatcher(Box(Point(200, 450), Point(200 + 200, 450 + 200))))
        self.__fm.append(FeatureMatcher(Box(Point(800, 300), Point(800 + 300, 300 + 200))))

    def getMedianDriftDistance(self):
        if len(self.__drifts)<=0:
            return None

        driftPixels = list()
        for drift in self.__drifts:
            driftPixels.append(drift.length())
        return numpy.median(driftPixels)

    def getMedianDriftAngle(self):
        if len(self.__drifts)<=0:
            return None

        driftAngles = list()
        for drift in self.__drifts:
            driftAngles.append(drift.angle())
        return numpy.median(driftAngles)

    def __isAbsoluteValueMoreThanTwiceBig(self, thisValue, medianValue):
        if math.fabs(thisValue) > math.fabs(medianValue) * 2:
        #if thisValue > medianValue * 2:
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

            #print "medianLength "+str(medianLength)+ " drift.length() "+str(drift.length())+ " div two "+ str(medianLength / 2)
            if (self.__isAbsoluteValueMoreThanTwiceBig(drift.length(),medianLength)):
                continue

            driftsNew.append(drift)

        return driftsNew


    def getMedianDriftVector(self):

        withoutOutliers = self.excludeOutliers(self.__drifts)
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

    def detectVelocity(self,frame,image):
        self.__drifts = list()
        for fm in self.__fm:
            section = fm.detectSeeFloorSections(frame)
            img = Image(image)
            section.drawFeatureOnFrame(img)
            if fm.detectionWasReset():
                continue

            #if self.__prevFrame is None:
            #    continue

            drift = section.getDrift()
            if not drift:
                continue

            self.__drifts.append(drift)

            #section.showSubImage()

        self.__prevFrame = frame



        #sec1 = self.__fm[0].detectSeeFloorSections(frame)
        #sec2 = self.__fm[1].detectSeeFloorSections(frame)
        #sec3 = self.__fm[2].detectSeeFloorSections(frame)
        #sec4 = self.__fm[3].detectSeeFloorSections(frame)
        # imageWinNoBoxes.showWindow(withRedDots)
        # fm.showSubImage()
        # fm2.showSubImage()
        # fm3.showSubImage()
        # fm4.showSubImage()
        # sec1.showSubImage()
        # sec2.showSubImage()
        # sec3.showSubImage()
        # sec4.showSubImage()
        #sec1.drawFeatureOnFrame(withRedDots)
        #sec2.drawFeatureOnFrame(withRedDots)
        #sec3.drawFeatureOnFrame(withRedDots)
        #sec4.drawFeatureOnFrame(withRedDots)

        # fm.drawBoxOnImage(withRedDots)
        # fm2.drawBoxOnImage(withRedDots)
        # fm3.drawBoxOnImage(withRedDots)
        # fm4.drawBoxOnImage(withRedDots)

        #for fm in self.__fm:
        #    print fm.infoAboutFeature()

    def getDriftsAsString(self):
        return Vector.vectorArrayAsString(self.__drifts)
        #if len(self.__drifts) <= 0:
        #    return ""
        #concatStr = [str(x) for x in self.__drifts]
        #return concatStr

    def getDriftsCount(self):
        return len(self.__drifts)

    def infoAboutDrift(self):
        driftVector = self.getMedianDriftVector()
        driftDistance = self.getMedianDriftDistance()
        driftAngle = self.getMedianDriftAngle()
        driftsCount = self.getDriftsCount()
        driftsStr = self.getDriftsAsString()
        driftsNoOutliersStr = Vector.vectorArrayAsString(self.excludeOutliers(self.__drifts))

        driftsRow = []
        if driftsStr:
            driftsRow.append(driftVector.x)
            driftsRow.append(driftVector.y)
            driftsRow.append(driftDistance)
            driftsRow.append(driftAngle)
            driftsRow.append(driftsCount)
            driftsRow.append(driftsStr)
            driftsRow.append(driftsNoOutliersStr)

        return driftsRow

    @staticmethod
    def infoHeaders():
        row = []
        row.append("driftX")
        row.append("driftY")
        row.append("driftDistance")
        row.append("driftAngle")
        row.append("driftsCount")
        row.append("drifts")
        row.append("driftsNoOutliers")
        return row

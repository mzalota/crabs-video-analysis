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

    def getMedianDriftVector(self):
        if len(self.__drifts)<=0:
            return None

        driftX = list()
        driftY = list()
        for drift in self.__drifts:
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
            if not fm.detectionWasReset() and self.__prevFrame is not None:
                drift = section.getDrift()
                self.__drifts.append(drift)
            #section.showSubImage()

        self.__prevFrame = frame

        if len(self.__drifts)>0:
            print [str(x) for x in self.__drifts]

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







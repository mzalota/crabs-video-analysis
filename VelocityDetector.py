import numpy

from FeatureMatcher import FeatureMatcher
from common import Box, Point


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

    def detectVelocity(self,frame,image):
        drifts = list()
        for fm in self.__fm:
            section = fm.detectSeeFloorSections(frame)
            section.drawFeatureOnFrame(image)
            if not fm.detectionWasReset() and self.__prevFrame is not None:
                drift = section.getDrift()
                drifts.append(drift)
            #section.showSubImage()

        if len(drifts)>0:
            print drifts
            #print "median value is"
            print numpy.median(drifts)

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





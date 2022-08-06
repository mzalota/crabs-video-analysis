import math

import numpy
from pebble import concurrent

from lib.FeatureMatcher import FeatureMatcher
from Image import Image
from common import Box, Point, Vector
from lib.MyTimer import MyTimer
from lib.VelocityDetector import VelocityDetector


class VelocityDetectorMultiThreaded(VelocityDetector):


    def detectVelocity(self,frame):
        #timerOuter = MyTimer("detectVelocity Outer")
        self._timer.lap("in detectVelocity() multithreaded start")
        # TODO: If the next line is moved one down we get exception for video files that don't have first frame
        imgObj = frame.getImgObj()
        self._drifts = list()
        futures = list()
        for fm in self._fm:
            #timerInner = MyTimer("timerInner")
            future = self.parallelize(fm, frame)
            futures.append(future)
            #timerInner.lap("futures.append")

        for future in futures:
            #timerInner = MyTimer("futures")
            section = future.result()
            #timerInner.lap("join")
            section.drawFeatureOnFrame(imgObj)
            if fm.detectionWasReset():
                continue

            drift = section.getDrift()
            if not drift:
                continue

            self._drifts.append(drift)

            #section.showSubImage()

        self._timer.lap("in detectVelocity() multithreaded end")
        self._prevFrame = frame

    @concurrent.thread
    def parallelize(self, fm, frame):
        #https://pythonhosted.org/Pebble/#concurrent-decorators
        section = fm.detectSeeFloorSection(frame)
        return section

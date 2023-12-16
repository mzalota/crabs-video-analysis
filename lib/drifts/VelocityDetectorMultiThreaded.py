from pebble import concurrent

from lib.drifts.FeatureMatcher import FeatureMatcher
from lib.drifts.VelocityDetector import VelocityDetector


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
            fm = future.result()
            if not fm.drift_is_valid():
                continue

            section = fm.seefloor_section()
            if not section.detection_was_successfull():
                continue

            drift = section.get_detected_drift()
            self._drifts.append(drift)

        self._timer.lap("in detectVelocity() multithreaded end")
        self._prevFrame = frame

    # https://pythonhosted.org/Pebble/#concurrent-decorators
    @concurrent.thread
    def parallelize(self, fm: FeatureMatcher, frame: Frame) -> SeeFloorSection:
        fm.detectSeeFloorSection(frame)
        return fm

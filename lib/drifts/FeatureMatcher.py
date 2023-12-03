from lib.Frame import Frame
from lib.drifts.SeeFloorSection import SeeFloorSection
from lib.imageProcessing.Analyzer import Analyzer
from lib.imageProcessing.Camera import Camera
from lib.model.Box import Box
from lib.model.Point import Point


class FeatureMatcher:
    def __init__(self, startingBox):
        self.__startingBox = startingBox
        self.__resetReason = ""
        self.__resetToStartingBox = False
        self.__correlation = 0
        self.__seeFloorSection = None

    def seefloor_section(self):
        return self.__seeFloorSection

    def detectionWasReset(self):
        return self.__resetToStartingBox

    def detectSeeFloorSection(self, frame: Frame) -> bool:
        if self.__seeFloorSection is None:
            self.__resetReason = "NotInitialized"
            self.__resetToStartingBox = False
            self.__seeFloorSection = SeeFloorSection(frame, self.__startingBox)
            return False

        successfull_detection = self.__detectSeeFloorSection(frame, self.__seeFloorSection)
        if not successfull_detection:
            self.__resetToStartingBox = False
            self.__seeFloorSection = SeeFloorSection(frame, self.__startingBox)
            return False

        if self.__is_feature_too_close_to_edge(self.__seeFloorSection.box_around_feature()):
            self.__resetReason = "TooCloseToEdge"
            self.__resetToStartingBox = False
            self.__seeFloorSection = SeeFloorSection(frame, self.__startingBox)

        return True


    def __detectSeeFloorSection(self, frame: Frame, section: SeeFloorSection) -> bool:
        newTopLeftOfFeature = section.findLocationInFrame(frame)

        if newTopLeftOfFeature is None:
            print("WARN: newTopLeftOfFeature is None. NotDetected_1")
            self.__resetReason = "NotDetected_1"
            return False

        section_drift = section.get_detected_drift()
        if section_drift is None:
            print("WARN: section_drift is None. NotDetected_2")
            self.__resetReason = "NotDetected_2"
            return False

        if section_drift.x != 0 or section_drift.y != 0:
            #drift was detected.
            return True

        return False


        # image = section.getImage()
        # i = Analyzer(image)
        # haze_ratio = i.getHazeRatio()
        # focus_ratio = i.getFocusRatio()
        #
        # if haze_ratio < 50 and focus_ratio > 200:
        #     print("This Subimage is very hazy and unfocused. Don't use this drift reading")
        #     self.__resetReason = "TooHazy"
        #     return False
        #
        # number_of_detections = section.number_of_detections()
        # if number_of_detections == 2:
        #     print("This Subimage is StuckOnStart. Don't use this drift reading")
        #     self.__resetReason = "StuckOnStart"
        #     return False
        #
        # return True


    def __is_feature_too_close_to_edge(self, top_left_of_feature: Box) -> bool:
        camera = Camera.create()

        too_close_to_image_top_edge = 100
        too_close_to_image_bottom_edge = camera.frame_height() - 150
        too_close_to_image_left_edge = 80
        too_close_to_image_right_edge = camera.frame_width() - 80

        if top_left_of_feature.topLeft.y < too_close_to_image_top_edge:
            return True #"TopEdge"
        if top_left_of_feature.bottomRight.y > too_close_to_image_bottom_edge:
            return True #"BottomEdge"
        if top_left_of_feature.topLeft.x < too_close_to_image_left_edge:
            return True #"LeftEdge"
        if top_left_of_feature.bottomRight.x > too_close_to_image_right_edge:
            return True #"RightEdge"

        return False

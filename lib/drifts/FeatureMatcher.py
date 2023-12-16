from lib.Frame import Frame
from lib.drifts.SeeFloorSection import SeeFloorSection
from lib.imageProcessing.Analyzer import Analyzer
from lib.imageProcessing.Camera import Camera
from lib.model.Box import Box
from lib.model.Point import Point


class FeatureMatcher:
    def __init__(self, startingBox):
        self.__startingBox = startingBox
        self.__resetReason = "JustCreated"
        self.__resetToStartingBox = True
        self.__driftIsValid = False
        self.__seeFloorSection = None

    def seefloor_section(self) -> SeeFloorSection:
        return self.__seeFloorSection

    def detectionWasReset(self) -> bool:
        return self.__resetToStartingBox

    def drift_is_valid(self) -> bool:
        return self.__driftIsValid

    def reset_to_starting_box(self):
        self.__resetReason = "ManualReset"
        self.__resetToStartingBox = True
        self.__driftIsValid = False

    def detectSeeFloorSection(self, frame: Frame) -> bool:
        if self.__resetToStartingBox:
            self.__seeFloorSection = SeeFloorSection(frame, self.__startingBox)
            self.__resetReason = "JustReset"
            self.__resetToStartingBox = False
            self.__driftIsValid = False
            return False

        self.__seeFloorSection.findLocationInFrame(frame)
        if not self.__seeFloorSection.detection_was_successfull():
            print("WARN: section_drift is None. NotDetected")
            self.__resetReason = "NotDetected_2"
            self.__resetToStartingBox = True
            self.__driftIsValid = False
            return False

        section_drift = self.__seeFloorSection.get_detected_drift()

        if section_drift.x == 0 and section_drift.y == 0:
            self.__resetReason = "NotMoved"
            self.__resetToStartingBox = True
            self.__driftIsValid = False
            return False

        if self.__is_feature_too_close_to_edge(self.__seeFloorSection.box_around_feature()):
            self.__resetReason = "TooCloseToEdge"
            self.__resetToStartingBox = True
            self.__driftIsValid = True
            return False

        self.__resetReason = ""
        self.__resetToStartingBox = False
        self.__driftIsValid = True
        return True


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

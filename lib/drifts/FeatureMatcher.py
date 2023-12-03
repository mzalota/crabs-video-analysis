from lib.Frame import Frame
from lib.drifts.SeeFloorSection import SeeFloorSection
from lib.imageProcessing.Analyzer import Analyzer
from lib.imageProcessing.Camera import Camera
from lib.model.Point import Point


class FeatureMatcher:
    def __init__(self, startingBox):
        self.__startingBox = startingBox
        self.__resetReason = ""
        self.__correlation = 0
        self.__seeFloorSection = None

    def starting_box(self):
        # type: () -> Box
        return self.__startingBox

    def seefloor_section(self):
        return self.__seeFloorSection

    def detectionWasReset(self):
        if self.__resetReason == "":
            return False
        else:
            return True

    def detectSeeFloorSection(self, frame):
        # type: (Frame) -> None
        self.__seeFloorSection = self.__detectSeeFloorSection(frame, self.__seeFloorSection)

    def __detectSeeFloorSection(self, frame: Frame, section: SeeFloorSection) -> SeeFloorSection:
        if section is None:
            return SeeFloorSection(frame, self.__startingBox)

        newTopLeftOfFeature = section.findLocationInFrame(frame)

        if newTopLeftOfFeature is None:
            self.__resetReason = "NotDetected"
            return SeeFloorSection(frame, self.__startingBox)

        section_drift = section.getDrift()
        if (section_drift is not None and section_drift.x == 0 and section_drift.y == 0):
            i = Analyzer(section.getImage())
            haze_ratio = i.getHazeRatio()
            focus_ratio = i.getFocusRatio()
            brightness_ratio = i.getBrightnessRatio()
            msg =  "detected zero drift. " + str(newTopLeftOfFeature.x) + "x" + str(newTopLeftOfFeature.y)
            msg += ": haze_ratio=" + str(haze_ratio)
            msg += ", focus_ratio=" + str(focus_ratio)
            msg += ", brightness_ratio=" + str(brightness_ratio)
            print(msg)

        self.__resetReason = self.__is_feature_too_close_to_edge(newTopLeftOfFeature, Frame.is_high_resolution(frame.frame_height()))


        return section

    def __is_feature_too_close_to_edge(self, top_left_of_feature: Point, is_high_resolution: bool) -> str:

        camera = Camera.create()

        too_close_to_image_top_edge = 100 #20
        too_close_to_image_bottom_edge = camera.frame_height() - 150 # 980+hi_res_height_diff
        too_close_to_image_left_edge = 80 #20
        too_close_to_image_right_edge = camera.frame_width() - 80 # 1900+hi_res_width_diff

        if top_left_of_feature.y <= too_close_to_image_top_edge:
            return "TopEdge"
        elif (top_left_of_feature.y + self.__startingBox.hight()) > too_close_to_image_bottom_edge:
            return "BottomEdge"
        elif top_left_of_feature.x <= too_close_to_image_left_edge:
            return "LeftEdge"
        elif (top_left_of_feature.x + self.__startingBox.width()) > too_close_to_image_right_edge:
            return "RightEdge"
        else:
            return ""


    @staticmethod
    def infoHeaders():
        row = list()
        row.append("featureId")
        row.append("boxSize")
        row.append("correlation")
        row.append("Reset")
        row.append("featureX")
        row.append("featureY")
        row.append("resetReason")
        return row

    def infoAboutFeature(self):
        row = list()
        row.append(self.__seeFloorSection.getID())
        row.append(self.__startingBox.width())
        row.append(self.__correlation)
        if self.detectionWasReset():
            row.append("Yes")
        else:
            row.append("No")
        row.append(self.__seeFloorSection.getLocation().x)
        row.append(self.__seeFloorSection.getLocation().y)

        row.append(self.__resetReason)
        return row

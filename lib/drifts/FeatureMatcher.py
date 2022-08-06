from lib.Frame import Frame
from lib.drifts.SeeFloorSection import SeeFloorSection


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
        #@rtype: SeeFloorSection
        return self.__seeFloorSection

    def detectionWasReset(self):
        if self.__resetReason == "":
            return False
        else:
            return True

    def detectSeeFloorSection(self, frame):
        # type: (Frame) -> None
        self.__seeFloorSection = self.__detectSeeFloorSection(frame, self.__seeFloorSection)

    def __detectSeeFloorSection(self, frame, section):
        # type: (Frame, SeeFloorSection) -> SeeFloorSection
        if section is None:
            return SeeFloorSection(frame, self.__startingBox)

        newTopLeftOfFeature = section.findLocationInFrame(frame)
        if newTopLeftOfFeature is None:
            self.__resetReason = "NotDetected"
        else:
            self.__resetReason = self.__is_feature_too_close_to_edge(newTopLeftOfFeature, frame.is_high_resolution())

        if self.detectionWasReset():
            #create bew SeeFloorSection
            return SeeFloorSection(frame, self.__startingBox)
        else:
            return section

    def __is_feature_too_close_to_edge(self, top_left_of_feature, is_high_resolution):
        # type: (Point, bool) -> str

        if is_high_resolution:
            hi_res_height_diff = 968
            hi_res_width_diff = 1152
        else:
            hi_res_height_diff = 0
            hi_res_width_diff = 0

        too_close_to_image_top_edge = 20
        too_close_to_image_bottom_edge = 980+hi_res_height_diff
        too_close_to_image_left_edge = 20
        too_close_to_image_right_edge = 1900+hi_res_width_diff

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

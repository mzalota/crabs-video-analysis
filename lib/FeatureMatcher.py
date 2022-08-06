from Frame import Frame
from SeeFloorSection import SeeFloorSection


class FeatureMatcher:
    def __init__(self, startingBox):
        self.__startingBox = startingBox
        self.__resetReason = ""
        self.__correlation = 0
        self.__seeFloorSection = None

    def startingBox(self):
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
        # type: (Frame) -> SeeFloorSection
        self.__seeFloorSection = self.__detectSeeFloorSection(frame, self.__seeFloorSection)
        return self.__seeFloorSection

    def __detectSeeFloorSection(self, frame, section):
        # type: (Frame, SeeFloorSection) -> SeeFloorSection
        if section is None:
            return SeeFloorSection(frame, self.__startingBox)

        newTopLeftOfFeature = section.findLocationInFrame(frame)

        self.__resetFeatureIfNecessary(newTopLeftOfFeature, frame.is_high_resolution())
        if self.detectionWasReset():
            #create bew SeeFloorSection
            return SeeFloorSection(frame, self.__startingBox)
        else:
            return section

    def __resetFeatureIfNecessary(self, newTopLeftOfFeature, is_high_resolution):
        # type: (Point) -> bool

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

        if newTopLeftOfFeature is None:
            #print "Did not detect feature: resetting Location to Default: "
            self.__resetReason = "NotDetected"
        elif newTopLeftOfFeature.y <= too_close_to_image_top_edge:
            #print "Got to the bottom of the screen: resetting location to default: "
            self.__resetReason = "TopEdge"
        elif (newTopLeftOfFeature.y + self.__startingBox.hight()) > too_close_to_image_bottom_edge:
            #print "Got to the bottom of the screen: resetting location to default: "
            self.__resetReason = "BottomEdge"
        elif newTopLeftOfFeature.x <= too_close_to_image_left_edge:
            #print "Got too close to the left edge: resetting location to default: "
            self.__resetReason = "LeftEdge"
        elif (newTopLeftOfFeature.x + self.__startingBox.width()) > too_close_to_image_right_edge:
            #print "Got too close to the right edge: resetting location to default: "
            self.__resetReason = "RightEdge"
        else:
            self.__resetReason = ""


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

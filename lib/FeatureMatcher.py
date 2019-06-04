from Frame import Frame
from SeeFloorSection import SeeFloorSection


class FeatureMatcher:
    def __init__(self, startingBox):
        self.__startingBox = startingBox
        self.__detectionWasReset = False
        self.__resetReason = ""
        self.__correlation = 0
        self.__seeFloorSection = None

    def detectionWasReset(self):
        return self.__detectionWasReset

    def detectSeeFloorSections(self, frame):
        # type: (Frame) -> SeeFloorSection
        self.__seeFloorSection = self.detectSeeFloorSection(frame, self.__seeFloorSection)
        return self.__seeFloorSection

    def detectSeeFloorSection(self, frame, section):
        # type: (Frame, SeeFloorSection) -> SeeFloorSection
        if section is None:
            return SeeFloorSection(frame, self.__startingBox)

        newTopLeftOfFeature = section.findFeature(frame)
        wasReset = self.__resetFeatureIfNecessary(newTopLeftOfFeature)
        self.__detectionWasReset = wasReset
        if wasReset:
            #section.closeWindow()
            return SeeFloorSection(frame, self.__startingBox)
        else:
            return section

    def __resetFeatureIfNecessary(self, newTopLeftOfFeature):
        if newTopLeftOfFeature is None:
            #print "Did not detect feature: resetting Location to Default: "+self.__seeFloorSection.getID()
            self.__resetReason = "NotDetected"
            wasReset = True
        elif ((newTopLeftOfFeature.y + self.__startingBox.hight()) > 980):
            #print "Got to the bottom of the screen: resetting location to default: "+self.__seeFloorSection.getID()
            #print newTopLeftOfFeature
            self.__resetReason = "Bottom"
            wasReset = True
        elif newTopLeftOfFeature.x <= 20:
            #print "Got too close to the left edge: resetting location to default: "+self.__seeFloorSection.getID()
            #print newTopLeftOfFeature
            self.__resetReason = "LeftEdge"
            wasReset = True
        else:
            self.__resetReason = ""
            wasReset = False
        return wasReset

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

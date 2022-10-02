import cv2

from lib.Frame import Frame
from lib.infra.Configurations import Configurations
from lib.reddots.RedDot import RedDot
from lib.common import Point, Box


class RedDotsDetector:
    # __initialDistanceForRedBoxSearchArea = 200

    def __init__(self, frame, configs):
        # type: (Frame, Configurations) -> RedDotsDetector
        self.__initial_x_coord_midpoint = configs.get_red_dots_x_mid_point()
        self.__initialDistanceForRedBoxSearchArea = configs.get_distance_between_red_dots()
        self.__frame = frame
        self.__redDot1 = None
        self.__redDot2 = None

    def getRedDot1(self):
        # type: () -> RedDot
        return self.__redDot1

    def getRedDot2(self):
        # type: () -> RedDot
        return self.__redDot2

    def show_on_UI(self, frame_id):

        drew1 = self.__redDot1.draw_on_UI("reddot_1_frame", frame_id)
        drew2 = self.__redDot2.draw_on_UI("reddot_2_frame", frame_id)
        print("trying to show UI drew1 "+ str(drew1) + ", drew2 " + str(drew2))
        if drew1 or drew2:
            cv2.waitKey(0)
        # cv2.destroyAllWindows()

    def isolateRedDots(self):
        imageObj = self.__frame.getImgObj()
        self.__redDot1 = RedDot(imageObj, self.__redDotsSearchArea1())
        self.__redDot2 = RedDot(imageObj, self.__redDotsSearchArea2())

    def __getImage(self):
        return self.__frame.getImgObj()

    def __distanceBetweenRedPoints(self):
        if self.__redDot1.dotWasDetected() and self.__redDot2.dotWasDetected():
            result = int(self.__redDot1.boxAroundDot.distanceTo(self.__redDot2.boxAroundDot))
        else:
            result = int(self.__initialDistanceForRedBoxSearchArea)

        print ("__distanceBetweenRedPoints is "+str(result))
        return result

    def __redDotsSearchArea1(self):
        #TODO: The self.__redDot1 is ALWAYS NULL... We need to somehow get redDot1 from previous frame...
        if self.__redDot1 is None:
            return self.__initial_search_area1()

        print ("__redDotsSearchArea1 detected "+str(self.__redDot1.dotWasDetected()))
        if not self.__redDot1.dotWasDetected():
            return self.__initial_search_area1()

        return self.__updateRedDotsSearchArea(self.__redDot1.boxAroundDot)


    def __redDotsSearchArea2(self):
        # TODO: The self.__redDot2 is ALWAYS NULL... We need to somehow get redDot2 from previous frame...
        if self.__redDot2 is None:
            return self.__initial_search_area2()

        print ("__redDotsSearchArea2 detected " + str(self.__redDot2.dotWasDetected()))
        if not self.__redDot2.dotWasDetected():
            return self.__initial_search_area2()

        return self.__updateRedDotsSearchArea(self.__redDot2.boxAroundDot)

    def __initial_search_area1(self):
        # type: () -> Box
        if (self.__frame.is_high_resolution() ):
            box = Box(Point(self.__initial_x_coord_midpoint - 400, 1000), Point(self.__initial_x_coord_midpoint, 1400))
        else:
            box = Box(Point(600, 300), Point(900, 600))
        return box

    def __initial_search_area2(self):
        # type: () -> Box
        if (self.__frame.is_high_resolution()):
            box = Box(Point(self.__initial_x_coord_midpoint, 1000), Point(self.__initial_x_coord_midpoint + 400, 1400))
        else:
            box = Box(Point(900, 300), Point(1400, 800))
        return box

    def __updateRedDotsSearchArea(self, boxAroundRedDots):
        dotsShift = int(self.__distanceBetweenRedPoints() / 2)

        bottomRightLimit_x = self.__getImage().width() - 200
        bottomRightLimit_y = self.__getImage().height() - 200

        topLeftX = min(max(boxAroundRedDots.topLeft.x - dotsShift, 1), bottomRightLimit_x-100)
        topLeftY = min(max(boxAroundRedDots.topLeft.y - dotsShift, 1), bottomRightLimit_y-100)
        bottomRightX = min(boxAroundRedDots.bottomRight.x + dotsShift, bottomRightLimit_x)
        bottomRightY = min(boxAroundRedDots.bottomRight.y + dotsShift, bottomRightLimit_y)

        redDotsSearchArea = Box(Point(topLeftX, topLeftY), Point(bottomRightX, bottomRightY))
        print("in __updateRedDotsSearchArea: "+ str(redDotsSearchArea) + " bottomRightLimit_x: "+str(bottomRightLimit_x))
        return redDotsSearchArea

    def dotsWasDetected(self):
        if not self.__redDot1.dotWasDetected():
            return False

        if not self.__redDot2.dotWasDetected():
            return False

        return True

    def infoAboutFrame(self):
        row = []

        row.append(self.__distanceBetweenRedPoints())
        row.append(self.__redDot1.dotWasDetected())
        row.append(self.__redDot2.dotWasDetected())
        if self.__redDot1.dotWasDetected():
            row.append(self.__redDot1.boxAroundDot.topLeft.x)
            row.append(self.__redDot1.boxAroundDot.topLeft.y)
            row.append(self.__redDot1.boxAroundDot.bottomRight.x)
            row.append(self.__redDot1.boxAroundDot.bottomRight.y)
            row.append(self.__redDot1.boxAroundDot.diagonal())
        else:
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
        if self.__redDot2.dotWasDetected():
            row.append(self.__redDot2.boxAroundDot.topLeft.x)
            row.append(self.__redDot2.boxAroundDot.topLeft.y)
            row.append(self.__redDot2.boxAroundDot.bottomRight.x)
            row.append(self.__redDot2.boxAroundDot.bottomRight.y)
            row.append(self.__redDot2.boxAroundDot.diagonal())
        else:
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
            row.append(-1)
        row.append(self.__getSearchAreaAsString())

        return row


    def __getSearchAreaAsString(self):
        redBox1 = self.__redDotsSearchArea1()
        redBox2 = self.__redDotsSearchArea2()
        return str(redBox1)+"_"+str(redBox2)

    @staticmethod
    def infoHeaders():
        row = []
        row.append("distance")
        row.append("redDot1Detected")
        row.append("redDot2Detected")
        row.append("redDot1_topLeft_x")
        row.append("redDot1_topLeft_y")
        row.append("redDot1_bootomRight_x")
        row.append("redDot1_bootomRight_y")
        row.append("redDot1_box_diagonal")
        row.append("redDot2_topLeft_x")
        row.append("redDot2_topLeft_y")
        row.append("redDot2_bootomRight_x")
        row.append("redDot2_bootomRight_y")
        row.append("redDot2_box_diagonal")
        row.append("searchArea")
        return row

from lib.reddots_interpolate.RedDotsData import RedDotsData
from lib.ui.RedDotsUI import RedDotsUI


class FillRedDotsGapsController:
    def __init__(self, redDotsData, redDotsUI):
        # type: (RedDotsData, RedDotsUI) -> RedDotsUI
        self.__redDotsData = redDotsData
        self.__redDotsUI = redDotsUI

    def showUI(self):
        while True:
            frameID, gapSize = self.__redDotsData.getMiddleFrameIDOfBiggestGap()
            print ("next Frame to process", frameID)

            frameID = self.__redDotsUI.showUI(frameID, gapSize)
            if frameID is None:
                # print "Pressed Q button" quit
                break

            # user clicked with a mouse, presumably
            redDots = self.__redDotsUI.selectedRedDots()
            self.__redDotsData.addManualDots(frameID, redDots)

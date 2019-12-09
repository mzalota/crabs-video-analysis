from lib.data.RedDotsManualData import RedDotsManualData
from lib.ui.RedDotsUI import RedDotsUI


class FillRedDotsGapsUI:
    def __init__(self, redDotsManualData, redDotsUI):
        # type: (RedDotsManualData, RedDotsUI) -> RedDotsUI
        self.__redDotsManualData = redDotsManualData
        self.__redDotsUI = redDotsUI

    def showUI(self):
        while True:
            frameID = self.__redDotsManualData.getMiddleOfBiggestGap()
            print ("next Frame to process", frameID)

            frameID = self.__redDotsUI.showUI(frameID)
            if frameID is None:
                # print "Pressed Q button" quit
                break

            # user clicked with a mouse, presumably
            redDots = self.__redDotsUI.selectedRedDots()
            self.__redDotsManualData.addManualDots(frameID, redDots)

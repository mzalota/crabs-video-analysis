import cv2

from lib.Frame import Frame
from lib.Image import Image
from lib.infra.Configurations import Configurations
from lib.reddots.RedDot import RedDot
from lib.common import Point, Box


class RedDotsDetector:
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
        images_reddot_1 = self.__redDot1.debugging_images()
        self.__show_UI_windows(images_reddot_1, "Reddot_1", frame_id)

        images_reddot_2 = self.__redDot2.debugging_images()
        self.__show_UI_windows(images_reddot_2, "Reddot_2", frame_id)

        #wait for 1 second so that the UI refreshes
        cv2.waitKey(1)

    def __show_UI_windows(self, images_dict, window_name_prefix, frame_id):
        for name, image_np in images_dict.items():
            orig_img = Image(image_np)
            orig_img.drawFrameID(frame_id)
            cv2.imshow(window_name_prefix + "_" + name, orig_img.asNumpyArray())

    def isolateRedDots(self):
        imageObj = self.__frame.getImgObj()
        self.__redDot1 = RedDot(imageObj, self.__initial_search_area1())
        self.__redDot2 = RedDot(imageObj, self.__initial_search_area2())

    def __getImage(self):
        return self.__frame.getImgObj()

    def __distanceBetweenRedPoints(self):
        if self.__redDot1.dotWasDetected() and self.__redDot2.dotWasDetected():
            result = int(self.__redDot1.boxAroundDot.distanceTo(self.__redDot2.boxAroundDot))
        else:
            result = int(self.__initialDistanceForRedBoxSearchArea)

        print ("__distanceBetweenRedPoints is "+str(result))
        return result

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

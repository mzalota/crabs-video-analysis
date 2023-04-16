from __future__ import annotations

import cv2

from lib.Frame import Frame
from lib.Image import Image
from lib.reddots.RedDot import RedDot
from lib.common import Point, Box


class RedDotsDetector:
    def __init__(self, frame: Frame) -> RedDotsDetector:
        self.__frame = frame
        self.__initial_x_coord_midpoint = frame.frame_width()/2
        self.__initial_y_coord_midpoint = frame.frame_height()/2
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

    def __getImage(self) -> Image:
        return self.__frame.getImgObj()

    def __initial_search_area1(self) -> Box:
        x = self.__initial_x_coord_midpoint
        y = self.__initial_y_coord_midpoint
        return Box(Point(x - 400, y), Point(x, y + 400))

    def __initial_search_area2(self) -> Box:
        x = self.__initial_x_coord_midpoint
        y = self.__initial_y_coord_midpoint
        return Box(Point(x, y), Point(x + 400, y + 400))

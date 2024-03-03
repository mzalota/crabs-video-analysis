import cv2

from lib.model.Box import Box
from lib.model.Image import Image
from lib.model.Point import Point
from lib.model.Vector import Vector


class SeeFloorSection:
    CORRELATION_THRESHOLD_FOR_MATCHING = 0.6

    def __init__(self, full_frame_image: Image, starting_box_location: Box):
        self.__box_width = starting_box_location.width()
        self.__box_height = starting_box_location.height()

        self._detection_was_successful = False
        self.__drift_vector = None

        self.__reset_vars(full_frame_image, starting_box_location.topLeft)

    def __reset_vars(self, image_full_frame: Image, top_left):
        self._box_top_left_point = top_left #change this variable first, so that box_around_feature() function returns correct location.
        self._sub_image_to_find = image_full_frame.subImage(self.box_around_feature())

    def try_detecting(self, image_to_search: Image) -> bool:
        new_location = self.__find_location_of_sub_image(image_to_search, self._sub_image_to_find)
        if not new_location:
            self._detection_was_successful = False
            self.__drift_vector = None
            return False

        self._detection_was_successful = True
        self.__drift_vector = Vector.create_from(new_location).minus(self._box_top_left_point)
        self.__reset_vars(image_to_search, new_location)
        return True

    def box_around_feature(self) -> Box:
        top_left = self._box_top_left_point
        bottom_right = Point(top_left.x + self.__box_width, top_left.y + self.__box_height)
        return Box(top_left, bottom_right)

    def detection_was_successful(self) -> bool:
        return self._detection_was_successful

    def get_detected_drift(self) -> Vector:
        return self.__drift_vector

    def __find_location_of_sub_image(self, whereToSearch: Image, whatToFind: Image) -> Point:
        image = whereToSearch.asNumpyArray()
        subImage = whatToFind.asNumpyArray()

        # Algorithm is described here: https: // www.geeksforgeeks.org / template - matching - using - opencv - in -python /

        # Convert image and subImage to grayscale
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        subImage_gray = cv2.cvtColor(subImage, cv2.COLOR_BGR2GRAY)

        # Perform match operations.
        res = cv2.matchTemplate(img_gray, subImage_gray, cv2.TM_CCOEFF_NORMED)

        #determine which rechtangle on the image is the best fit for subImage (has the highest correlation)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val < self.CORRELATION_THRESHOLD_FOR_MATCHING:
            # If the best matching box still has correlation below the "threshold" then declare defeat -> we could not find a match for subImage on this image
            return None

        # get w and h, so that we can reconstruct the box
        d, w, h = subImage.shape[::-1]
        topLeft = Point(max_loc[0], max_loc[1])
        Point(topLeft.x + w, topLeft.y + h)

        return topLeft

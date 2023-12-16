import cv2

from lib.Frame import Frame
from lib.model.Image import Image
from lib.model.Box import Box
from lib.model.Vector import Vector
from lib.model.Point import Point



class SeeFloorSection:
    CORRELATION_THRESHOLD_FOR_MATCHING = 0.6

    def __init__(self, frame: Frame, starting_box_location: Box):
        self.__startingBox = starting_box_location

        self._detection_was_successfull = False
        self._prev_frame_obj = None
        self._this_frame_obj = frame
        self._prev_top_left_point = None
        self._this_top_left_point = starting_box_location.topLeft

    def box_around_feature(self) -> Box:
        topLeftPoint = self._this_top_left_point
        bottomRightPoint = Point(topLeftPoint.x + self.__startingBox.width(), topLeftPoint.y + self.__startingBox.hight())
        return Box(topLeftPoint, bottomRightPoint)

    def get_center_point(self) -> Point:
        box = self.box_around_feature()
        return box.centerPoint()

    def detection_was_successfull(self) -> bool:
        return self._detection_was_successfull

    def get_detected_drift(self) -> Vector:
        # if self._prev_frame_obj is None:
        #     return None

        lastPoint = self._this_top_left_point
        beforeLastPoint = self._prev_top_left_point
        driftVector = Vector(lastPoint.x-beforeLastPoint.x, lastPoint.y-beforeLastPoint.y)

        return driftVector

    def findLocationInFrame(self, frame: Frame) -> bool:
        newLocation = self.__find_location_of_sub_image(frame.getImgObj(), self.__get_prev_subimage())
        if not newLocation:
            self._detection_was_successfull = False
            self._prev_frame_obj = None
            self._this_frame_obj = frame
            self._prev_top_left_point = None
            # self._this_top_left_point = newLocation
            return False
        else:
            self._detection_was_successfull = True
            self._prev_frame_obj = self._this_frame_obj
            self._this_frame_obj = frame
            self._prev_top_left_point = self._this_top_left_point
            self._this_top_left_point = newLocation
            return True

    def __get_prev_subimage(self) -> Image:
        # img_obj = self._prev_frame_obj.getImgObj()
        img_obj = self._this_frame_obj.getImgObj()
        img = img_obj.subImage(self.box_around_feature())
        return img

    def __find_location_of_sub_image(self, whereToSearch: Image, whatToFind: Image) -> Point:
        image = whereToSearch.asNumpyArray()
        subImage = whatToFind.asNumpyArray()

        if subImage is None:
            return None

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

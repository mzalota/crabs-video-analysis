from lib.Camera import Camera
from lib.model.Box import Box
from lib.model.Point import Point


class Crab:
    def __init__(self, frame_id: int, side1: Point, side2: Point):
        self.__frame_id = frame_id
        self.__side1 = side1
        self.__side2 = side2

    def getBox(self) -> Box:
        return Box(self.__side1, self.__side2)

    def frame_id(self) -> int:
        return self.__frame_id

    def center(self) -> Point:
        return self.getBox().centerPoint()

    def width_px(self) -> float:
        return self.getBox().diagonal()

    def width_px_undistorted(self) -> float:
        camera = Camera.create()
        point_undistorted_1 = camera.undistort_point(self.__side1)
        point_undistorted_2 = camera.undistort_point(self.__side2)

        return Box(point_undistorted_1, point_undistorted_2).diagonal()

    def width_mm_undistorted(self) -> float:
        pass

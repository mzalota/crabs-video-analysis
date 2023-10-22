from lib.imageProcessing.Camera import Camera
from lib.reddots.RedDot import RedDot


class RedDots:
    def __init__ (self, frame_id: int, red_dot1: RedDot, red_dot2: RedDot):
        self.__frame_id = frame_id
        self.__red_dot1 = red_dot1
        self.__red_dot2 = red_dot2

    def mm_per_pixel_undistorted(self) -> int:
        camera = Camera.create()
        redDot1 = camera.undistort_point(self.__red_dot1)
        redDot2 = camera.undistort_point(self.__red_dot2)
        return redDot1.distanceTo(redDot2)

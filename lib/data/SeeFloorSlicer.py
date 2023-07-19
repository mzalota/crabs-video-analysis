from lib.Camera import Camera
from lib.common import Point
from lib.data.PandasWrapper import PandasWrapper
from lib.infra.MyTimer import MyTimer


class SeeFloorSlicer(PandasWrapper):
    def getPrevFrame(self, frame_id):
        # type: (int) -> int
        return self.jumpToSeefloorSlice(frame_id, -1)

    def getNextFrame(self, frame_id):
        # type: (int) -> int
        return self.jumpToSeefloorSlice(frame_id, 1)

    def jumpToSeefloorSlice(self, frame_id, frames_to_jump):
        # type: (int, float) -> int
        if frame_id < self._min_frame_id():
            return int(self._min_frame_id())

        if frame_id > self._max_frame_id():
            return int(self._max_frame_id())

        new_frame_id = frame_id
        while frames_to_jump != 0:
            if frames_to_jump > 0:

                if frames_to_jump>0 and frames_to_jump<1:
                    #its a fractional jump
                    new_frame_id = int(self._jump_to_next_seefloor_slice(new_frame_id, frames_to_jump))
                    frames_to_jump = 0
                else:
                    new_frame_id = int(self._jump_to_next_seefloor_slice(new_frame_id))
                    frames_to_jump = frames_to_jump-1
            if frames_to_jump < 0:
                new_frame_id = int(self._jump_to_previous_seefloor_slice(new_frame_id))
                frames_to_jump = frames_to_jump+1

        return new_frame_id

    def _jump_to_previous_seefloor_slice(self, frame_id):
        # type: (int) -> int
        if frame_id < self._min_frame_id():
            return self._min_frame_id()

        if frame_id > self._max_frame_id():
            return self._max_frame_id()

        # we are in a good segment and not in its first frame.
        pixels_to_jump = Camera.create().frame_height() * (-1)
        new_frame_id = int(self._getNextFrame(pixels_to_jump, frame_id))
        return new_frame_id

    def _jump_to_next_seefloor_slice(self, frame_id, fraction=1):
        # type: (int) -> int
        if frame_id < self._min_frame_id():
            return self._min_frame_id()

        if frame_id > self._max_frame_id():
            return self._max_frame_id()

        # we are in a good segment and not in its last frame.
        pixels_to_jump = Camera.create().frame_height() * fraction
        new_frame_id = int(self._getNextFrame(pixels_to_jump, frame_id))

        timer = MyTimer("SeeFloorSlicer._get_next_frame_id()")
        next_frame_id_new = self._get_next_frame_id(frame_id)
        timer.lap()
        print("new_frame_id: " + str(new_frame_id) + ", next_frame_id_new: " + str(next_frame_id_new) + " orig_frameId: " + str(frame_id) + ", fraction: " + str(fraction) + ", pixels_to_jump:" + str(pixels_to_jump))
        return new_frame_id

    def _get_next_frame_id(self, start_frame_id: int):
        #examine next frames, until none of the corner pixels visible.
        frame_width = Camera.create().frame_width()
        frame_height = Camera.create().frame_height()
        top_left = Point(1,1)
        top_right = Point(frame_width-1, 1)
        bottom_left = Point(1, frame_height-1)
        bottom_right = Point(frame_width-1, frame_height-1)
        center = Point(int(frame_width/2), int(frame_height/2))

        candidate_frame_id = start_frame_id
        while(True):
            candidate_frame_id += 1

            if candidate_frame_id >= self._max_frame_id():
                break

            if candidate_frame_id <= self._min_frame_id():
                break

            new_top_left = self.translatePointCoordinate(top_left, start_frame_id, candidate_frame_id)
            new_top_right = self.translatePointCoordinate(top_right, start_frame_id, candidate_frame_id)
            new_bottom_left = self.translatePointCoordinate(bottom_left, start_frame_id, candidate_frame_id)
            new_bottom_right = self.translatePointCoordinate(bottom_right, start_frame_id, candidate_frame_id)
            new_center = self.translatePointCoordinate(center, start_frame_id, candidate_frame_id)

            if (self.__point_is_visible(new_top_left)):
                continue
            if self.__point_is_visible(new_top_right):
                continue
            if self.__point_is_visible(new_bottom_left):
                continue
            if self.__point_is_visible(new_bottom_right):
                continue
            if self.__point_is_visible(new_center):
                continue

            #All 4 corner points have disappeared from the screen on frame "candidate_frame_id".
            #we found our next frame!
            break

        return candidate_frame_id

    def __point_is_visible(self, point):
        frame_width = Camera.create().frame_width()
        frame_height = Camera.create().frame_height()
        if point.y < 0:
            return False
        if point.x < 0:
            return False
        if point.y > frame_height:
            return False
        if point.x > frame_width:
            return False
        return True

from lib.Camera import Camera
from lib.common import Point
from lib.data.SeeFloorFast import SeeFloorFast
from lib.infra.MyTimer import MyTimer


# class SeeFloorSlicer(PandasWrapper):
class SeeFloorSlicer:
    def __init__(self, seeFloorFast: SeeFloorFast, minFrameID: int, maxFrameID: int):
        self.__fastObj = seeFloorFast
        self.__minFrameID = minFrameID
        self.__maxFrameID = maxFrameID

    def translatePointCoordinate(self, pointLocation: Point, origFrameID: int, targetFrameID: int) -> Point:
        return self.__fastObj.translatePointCoordinate(pointLocation, origFrameID, targetFrameID)

    def _min_frame_id(self):
        return self.__minFrameID
        # return self.__seeFloor.minFrameID()

    def _max_frame_id(self):
        return self.__maxFrameID
        # return self.__seeFloor.maxFrameID()

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

        print("!!!!!!!!!! in _jump_to_previous_seefloor_slice. frame_id:", frame_id)
        new_frame_id = self._get_prev_frame_id(frame_id)

        return new_frame_id

    def _jump_to_next_seefloor_slice(self, frame_id, fraction=1):
        # type: (int) -> int
        if frame_id < self._min_frame_id():
            return self._min_frame_id()

        if frame_id > self._max_frame_id():
            return self._max_frame_id()

        new_frame_id = self._get_next_frame_id(frame_id)

        return new_frame_id

    def _get_prev_frame_id(self, start_frame_id: int):
        return self._jump_one_frame_id(start_frame_id, -1)

    def _get_next_frame_id(self, start_frame_id: int):
        return self._jump_one_frame_id(start_frame_id, 1)

    def _jump_one_frame_id(self, start_frame_id: int, direction = 1):
        # #examine next frames, until none of the corner pixels visible.
        step_size = 256

        if start_frame_id >= self._max_frame_id() and direction == 1:
            return self._max_frame_id()
        if start_frame_id <= self._min_frame_id() and direction == -1:
            return self._min_frame_id()

        timer = MyTimer("SeeFloorSlicer._get_next_frame_id()")

        candidate_frame_id = start_frame_id + direction
        too_far_frame_id = start_frame_id + (step_size * direction)
        not_far_enough_frame_id = start_frame_id

        if too_far_frame_id > self._max_frame_id():
            too_far_frame_id = self._max_frame_id()
        if too_far_frame_id < self._min_frame_id():
            too_far_frame_id = self._min_frame_id()

        while self._frames_overlap(start_frame_id, too_far_frame_id):
            too_far_frame_id = too_far_frame_id + (step_size * direction)
            if too_far_frame_id > self._max_frame_id():
                too_far_frame_id = self._max_frame_id()
                break
            if too_far_frame_id < self._min_frame_id():
                too_far_frame_id = self._min_frame_id()
                break

        num_of_loops = 0
        while(True):
            num_of_loops += 1
            # print(candidate_frame_id, not_far_enough_frame_id, too_far_frame_id)

            if not_far_enough_frame_id + direction == too_far_frame_id:
                #not_far_enough_frame_id has overlap and too_far_frame_id does not have overlap. So our answer is too_far_frame_id
                candidate_frame_id = too_far_frame_id
                break

            if self._frames_overlap(start_frame_id, candidate_frame_id):
                not_far_enough_frame_id = candidate_frame_id
            else:
                too_far_frame_id = candidate_frame_id

            candidate_frame_id = not_far_enough_frame_id + int((too_far_frame_id - not_far_enough_frame_id)/2)

        timer.lap("finished calculating too_far_frame_id. next_frame_id_new: " + str(candidate_frame_id) + " orig_frameId: " + str(start_frame_id) +", num_of_loops: "+str(num_of_loops))
        return candidate_frame_id

    def _frames_overlap(self, start_frame_id, candidate_frame_id):
        # examine next frames, until none of the corner pixels visible.
        frame_width = Camera.create().frame_width()
        frame_height = Camera.create().frame_height()

        # top_left = Point(1, 1)
        # top_right = Point(frame_width - 1, 1)
        # bottom_left = Point(1, frame_height - 1)
        # bottom_right = Point(frame_width - 1, frame_height - 1)
        # center = Point(int(frame_width / 2), int(frame_height / 2))

        top_left = Point(int(frame_width / 2), 1)  # top_center
        top_right = Point(frame_width - 1, int(frame_height / 2))  # right_center
        bottom_left = Point(int(frame_width / 2), frame_height - 1)  # bottom center
        bottom_right = Point(1, int(frame_height / 2))  # left_center
        center = Point(int(frame_width / 2), int(frame_height / 2))

        isContinue = True
        firstLoop = True
        while (firstLoop):
            firstLoop = False
            new_top_left = self.translatePointCoordinate(top_left, start_frame_id, candidate_frame_id)
            # print("new_top_left")
            new_top_right = self.translatePointCoordinate(top_right, start_frame_id, candidate_frame_id)
            # print("new_top_right")
            new_bottom_left = self.translatePointCoordinate(bottom_left, start_frame_id, candidate_frame_id)
            # print("new_bottom_left")
            new_bottom_right = self.translatePointCoordinate(bottom_right, start_frame_id, candidate_frame_id)
            # print("new_bottom_right")
            new_center = self.translatePointCoordinate(center, start_frame_id, candidate_frame_id)
            # print("new_center")

            if (self.__point_is_visible(new_top_left)):
                # print("new_top_left is still visible")
                continue
            if self.__point_is_visible(new_top_right):
                # print("new_top_right is still visible")
                continue
            if self.__point_is_visible(new_bottom_left):
                # print("new_bottom_left is still visible")
                continue
            if self.__point_is_visible(new_bottom_right):
                # print("new_bottom_right is still visible")
                continue
            if self.__point_is_visible(new_center):
                # print("new_center is still visible")
                continue

            # now check the 4 corners of destination frame
            new_top_left = self.translatePointCoordinate(top_left, candidate_frame_id, start_frame_id)
            # print("new_top_left reverse")
            new_top_right = self.translatePointCoordinate(top_right, candidate_frame_id, start_frame_id)
            # print("new_top_right reverse")
            new_bottom_left = self.translatePointCoordinate(bottom_left, candidate_frame_id, start_frame_id)
            # print("new_bottom_left reverse")
            new_bottom_right = self.translatePointCoordinate(bottom_right, candidate_frame_id, start_frame_id)
            # print("new_bottom_right reverse")
            new_center = self.translatePointCoordinate(center, candidate_frame_id, start_frame_id)
            # print("new_center reverse")

            if (self.__point_is_visible(new_top_left)):
                # print("new_top_left reverse is still visible")
                continue
            if self.__point_is_visible(new_top_right):
                # print("new_top_right reverse is still visible")
                continue
            if self.__point_is_visible(new_bottom_left):
                # print("new_bottom_left reverse is still visible")
                continue
            if self.__point_is_visible(new_bottom_right):
                # print("new_bottom_right reverse is still visible")
                continue
            if self.__point_is_visible(new_center):
                # print("new_center reverse is still visible")
                continue

            # All 4 corner points have disappeared from the screen on frame "candidate_frame_id".
            # we found our next frame!
            isContinue = False
        return isContinue

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

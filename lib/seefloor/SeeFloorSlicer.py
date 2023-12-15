from lib.imageProcessing.Camera import Camera
from lib.model.Point import Point
from lib.seefloor.PointTranslator import PointTranslator
from lib.seefloor.SeeFloorFast import SeeFloorFast
from lib.infra.MyTimer import MyTimer

class SeeFloorSlicer:
    def __init__(self, point_translator: PointTranslator, fastObj: SeeFloorFast):
        self._point_translator = point_translator
        self.__fastObj = fastObj
        self.__cache_next_frames = dict()
        self.__cache_prev_frames = dict()

    def _min_frame_id(self):
        return self.__fastObj.min_frame_id()

    def _max_frame_id(self):
        return self.__fastObj.max_frame_id()

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

    def _jump_to_previous_seefloor_slice(self, frame_id: int) -> int:
        if frame_id <= self._min_frame_id():
            return self._min_frame_id()

        if frame_id > self._max_frame_id():
            return self._max_frame_id()

        if (frame_id in self.__cache_prev_frames):
            prev_frames_id = self.__cache_prev_frames.get(frame_id)
            return prev_frames_id

        prev_frame_id = self._get_prev_frame_id(frame_id)

        self.__cache_prev_frames[frame_id] = prev_frame_id
        self.__cache_next_frames[prev_frame_id] = frame_id
        return prev_frame_id

    def _jump_to_next_seefloor_slice(self, frame_id: int) -> int:
        if frame_id < self._min_frame_id():
            return self._min_frame_id()

        if frame_id >= self._max_frame_id():
            return self._max_frame_id()

        if (frame_id in self.__cache_next_frames):
            next_frame_id = self.__cache_next_frames.get(frame_id)
            return next_frame_id

        next_frame_id = self._get_next_frame_id(frame_id)

        self.__cache_next_frames[frame_id] = next_frame_id
        self.__cache_prev_frames[next_frame_id] = frame_id
        return next_frame_id

    def _get_prev_frame_id(self, start_frame_id: int):
        return self._jump_one_frame_id(start_frame_id, -1)

    def _get_next_frame_id(self, start_frame_id: int):
        return self._jump_one_frame_id(start_frame_id, 1)

    def _jump_one_frame_id(self, start_frame_id: int, direction = 1):

        if start_frame_id >= self._max_frame_id() and direction == 1:
            return self._max_frame_id()
        if start_frame_id <= self._min_frame_id() and direction == -1:
            return self._min_frame_id()

        timer = MyTimer("SeeFloorSlicer._jump_one_frame_id()")

        # #examine next frames, until none of the corner pixels visible.
        step_size = 256

        candidate_frame_id = start_frame_id + direction
        too_far_frame_id = start_frame_id + (step_size * direction)
        not_far_enough_frame_id = start_frame_id

        if too_far_frame_id > self._max_frame_id():
            too_far_frame_id = self._max_frame_id()
        if too_far_frame_id < self._min_frame_id():
            too_far_frame_id = self._min_frame_id()

        while self._do_frames_overlap(start_frame_id, too_far_frame_id):
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

            if self._do_frames_overlap(start_frame_id, candidate_frame_id):
                not_far_enough_frame_id = candidate_frame_id
            else:
                too_far_frame_id = candidate_frame_id

            candidate_frame_id = not_far_enough_frame_id + int((too_far_frame_id - not_far_enough_frame_id)/2)

        timer.lap("finished calculating too_far_frame_id. next_frame_id_new: " + str(candidate_frame_id) + " orig_frameId: " + str(start_frame_id) +", num_of_loops: "+str(num_of_loops))
        return candidate_frame_id

    def _do_frames_overlap(self, start_frame_id, candidate_frame_id):
        #check if any of the points on the center of each start_frame_id's side are visible on candidate_frame_id
        is_there_overlap = self.__is_start_frame_visible_on_candidate_frame(start_frame_id, candidate_frame_id)
        if is_there_overlap:
            return True

        # now check the reverse
        # check if any of the points on the center of each candidate_frame_id's side are visible on start_frame_id
        is_there_overlap = self.__is_start_frame_visible_on_candidate_frame(candidate_frame_id, start_frame_id)
        if is_there_overlap:
            return True

        return False

    def __is_start_frame_visible_on_candidate_frame(self, start_frame_id, candidate_frame_id):
        # examine next frames, until none of the corner pixels visible.
        camera = Camera.create()
        frame_width = camera.frame_width()
        frame_height = camera.frame_height()

        frame_center  = camera.center_point()
        top_center    = Point(frame_center.x, 1)
        bottom_center = Point(frame_center.x, frame_height - 1)

        left_center   = Point(1,               frame_center.y)
        right_center  = Point(frame_width - 1, frame_center.y)

        point_translator = self._point_translator
        new_top_center = point_translator.translatePointCoordinate(top_center, start_frame_id, candidate_frame_id)
        if (self.__point_is_visible(new_top_center)):
            # print("new_top_center is still visible")
            return True

        new_bottom_center = point_translator.translatePointCoordinate(bottom_center, start_frame_id, candidate_frame_id)
        if self.__point_is_visible(new_bottom_center):
            # print("new_bottom_center is still visible")
            return True

        new_right_center = point_translator.translatePointCoordinate(right_center, start_frame_id, candidate_frame_id)
        if self.__point_is_visible(new_right_center):
            # print("new_right_center is still visible")
            return True

        new_left_center = point_translator.translatePointCoordinate(left_center, start_frame_id, candidate_frame_id)
        if self.__point_is_visible(new_left_center):
            # print("new_left_center is still visible")
            return True

        new_center = point_translator.translatePointCoordinate(frame_center, start_frame_id, candidate_frame_id)
        if self.__point_is_visible(new_center):
            # print("new_center is still visible")
            return True

        return False

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

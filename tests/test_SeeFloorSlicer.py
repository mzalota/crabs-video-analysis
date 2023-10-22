from unittest import TestCase
from unittest.mock import MagicMock

from lib.seefloor.SeeFloorSlicer import SeeFloorSlicer





class TestSeeFloorSlicer(TestCase):

    def frames_overlap_160(*args, **kwargs):
        start_frame_id = args[1]
        candidate_frame_id = args[2]
        # print("start_frame_id", start_frame_id)
        # print("candidate_frame_id", candidate_frame_id)

        if candidate_frame_id > 890:
            raise Exception

        if candidate_frame_id < 5:
            raise Exception

        if candidate_frame_id >= 660:
            return False

        if candidate_frame_id <= 220:
            return False

        return True

    def test__get_prev_frame_id_result_is_first(self):
        slicer = SeeFloorSlicer(None, None)

        slicer._frames_overlap = MagicMock(side_effect=self.frames_overlap_160)
        slicer._max_frame_id = MagicMock(return_value=890)
        slicer._min_frame_id = MagicMock(return_value=5)

        #exercise
        result_frame_id = slicer._get_prev_frame_id(5)

        #assert
        self.assertEqual(5, result_frame_id)


    def test__get_next_frame_id_next_frame_is_last(self):
        slicer = SeeFloorSlicer(None, None)

        slicer._frames_overlap = MagicMock(side_effect=self.frames_overlap_160)
        slicer._max_frame_id = MagicMock(return_value=890)
        slicer._min_frame_id = MagicMock(return_value=5)

        #exercise
        result_frame_id = slicer._get_next_frame_id(890)

        #assert
        self.assertEqual(890, result_frame_id)

    def test__get_next_frame_id_next_frame_is_further_than_256(self):
        slicer = SeeFloorSlicer(None, None)

        slicer._frames_overlap = MagicMock(side_effect=self.frames_overlap_160)
        slicer._max_frame_id = MagicMock(return_value=890)
        slicer._min_frame_id = MagicMock(return_value=5)

        #exercise
        result_frame_id = slicer._get_next_frame_id(350)

        #assert
        self.assertEqual(660, result_frame_id)


    def test__get_prev_frame_id_result_is_close_to_start(self):
        slicer = SeeFloorSlicer(None, None)

        slicer._frames_overlap = MagicMock(side_effect=self.frames_overlap_160)
        slicer._max_frame_id = MagicMock(return_value=890)
        slicer._min_frame_id = MagicMock(return_value=5)

        #exercise
        result_frame_id = slicer._get_prev_frame_id(240)

        #assert
        self.assertEqual(220, result_frame_id)

    def test__get_prev_frame_id_result_is_further_than_256(self):
        slicer = SeeFloorSlicer(None, None)

        slicer._frames_overlap = MagicMock(side_effect=self.frames_overlap_160)
        slicer._max_frame_id = MagicMock(return_value=890)
        slicer._min_frame_id = MagicMock(return_value=5)

        #exercise
        result_frame_id = slicer._get_prev_frame_id(550)

        #assert
        self.assertEqual(220, result_frame_id)
from unittest import TestCase
from unittest.mock import MagicMock

from lib.data.SeeFloorSlicer import SeeFloorSlicer





class TestSeeFloorSlicer(TestCase):

    def frames_overlap_160(*args, **kwargs):
        start_frame_id = args[1]
        candidate_frame_id = args[2]
        # print("start_frame_id", start_frame_id)
        # print("candidate_frame_id", candidate_frame_id)

        if candidate_frame_id > 240:
            raise Exception

        if candidate_frame_id >= 160:
            return False


        return True
    def test__get_next_frame_id_aa(self):
        slicer = SeeFloorSlicer()

        slicer.frames_overlap = MagicMock(side_effect=self.frames_overlap_160)
        # slicer.frames_overlap = MagicMock(return_value=False)
        slicer._max_frame_id = MagicMock(return_value=1000)
        slicer._min_frame_id = MagicMock(return_value=5)

        #exercise
        result_frame_id = slicer._get_next_frame_id(100)

        #assert
        self.assertEqual(result_frame_id, 160)


    def test__get_next_frame_id_bb(self):
        slicer = SeeFloorSlicer()

        slicer.frames_overlap = MagicMock(side_effect=self.frames_overlap_160)
        # slicer.frames_overlap = MagicMock(return_value=False)
        slicer._max_frame_id = MagicMock(return_value=240)
        slicer._min_frame_id = MagicMock(return_value=5)

        #exercise
        result_frame_id = slicer._get_next_frame_id(50)

        #assert
        self.assertEqual(result_frame_id, 160)

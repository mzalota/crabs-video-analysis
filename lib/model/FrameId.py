from typing import List


class FrameId:

    @staticmethod
    def sequence_of_frames(origFrameID: int, targetFrameID: int)-> List[int]:
        if origFrameID > targetFrameID:
            increment = -1
        else:
            increment = 1
        individual_frames = list(range(origFrameID, targetFrameID, increment))
        return individual_frames
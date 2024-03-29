from __future__ import annotations

from operator import itemgetter
from typing import Dict

import numpy as np

from lib.model.FrameId import FrameId
from lib.model.Point import Point
from lib.seefloor.SeefloorFrame import SeefloorFrame


class SeeFloorTract:
    def __init__(self, dict_of_seefloor_frames: Dict[SeefloorFrame], forward: bool = True) -> SeeFloorTract:
        self.__seefloor_frames = dict_of_seefloor_frames
        self.__forward = forward

    def __min_frame_id(self):
        return min(list(self.__seefloor_frames.keys()))

    def __max_frame_id(self):
        return max(list(self.__seefloor_frames.keys()))

    def translatePointCoordinate(self, pointLocation):
        if len(self.__seefloor_frames) <=0 :
            # Tract is just the same frame. Sot it's the same point.
            return pointLocation

        point_location_new = pointLocation
        # timer = MyTimer("translatePointCoordinate")
        individual_frames = FrameId.sequence_of_frames(self.__min_frame_id(), self.__max_frame_id())
        for idx in range(1, len(individual_frames)):
            to_frame_id = individual_frames[idx]
            if self.__forward:
                seefloorFrame = self.__seefloor_frames[to_frame_id]
                result = seefloorFrame.translate_forward(point_location_new)
            else:
                frame_id = to_frame_id - 1
                seefloorFrame = self.__seefloor_frames[frame_id]
                result = seefloorFrame.translate_backward(point_location_new)
            point_location_new = result
        # timer.lap("end "+str(pointLocation)+" loops:"+ str(len(individual_frames))+ ", orig frameId: "+str(origFrameID)+ ", target frameId: "+str(targetFrameID) + " new loc:"+str(point_location_new) )
        return Point(int(round(point_location_new.x, 0)), int(round(point_location_new.y, 0)))

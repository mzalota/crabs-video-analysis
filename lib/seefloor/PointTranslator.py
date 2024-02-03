from lib.model.FrameId import FrameId
from lib.seefloor.FramePhysics import FramePhysics
from lib.model.Vector import Vector
from lib.model.Point import Point
from lib.seefloor.SeeFloorFast import SeeFloorFast


class PointTranslator:

    def __init__(self, fastObj: SeeFloorFast):
        self.__fastObj = fastObj

    def __get_frame_physics(self, to_frame_id: int) -> FramePhysics:
        drift = self.__fastObj.get_drift(to_frame_id)
        zoom = self.__fastObj.zoom_factor(to_frame_id)
        return FramePhysics(drift, zoom)

    def translatePointCoordinate(self, pointLocation: Point, origFrameID: int, targetFrameID: int) -> Point:
        point_location_new = pointLocation
        # timer = MyTimer("translatePointCoordinate")
        individual_frames = FrameId.sequence_of_frames(origFrameID, targetFrameID)
        for idx in range(1, len(individual_frames)):
            to_frame_id = individual_frames[idx]
            if targetFrameID < origFrameID:
                frame_physics = self.__get_frame_physics(to_frame_id-1)
                result = frame_physics.translate_backward(point_location_new)
            else:
                frame_physics = self.__get_frame_physics(to_frame_id)
                result = frame_physics.translate_forward(point_location_new)
            point_location_new = result
        # timer.lap("end "+str(pointLocation)+" loops:"+ str(len(individual_frames))+ ", orig frameId: "+str(origFrameID)+ ", target frameId: "+str(targetFrameID) + " new loc:"+str(point_location_new) )

        return Point(int(round(point_location_new.x, 0)), int(round(point_location_new.y, 0)))

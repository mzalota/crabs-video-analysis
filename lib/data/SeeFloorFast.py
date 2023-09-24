from lib.FrameId import FrameId
from lib.FramePhysics import FramePhysics
from lib.common import Vector, Point
from lib.infra.MyTimer import MyTimer


class SeeFloorFast:

    def __init__(self, seefloorDF):
        df_indexed = seefloorDF.set_index('frameNumber')

        self.__mm_per_pixel_dict = df_indexed["mm_per_pixel"].to_dict()
        self.__drift_y_dict = df_indexed ['driftY'].to_dict()
        self.__drift_x_dict = df_indexed['driftX'].to_dict()

    def min_frame_id(self) -> int:
        return min(self.__drift_y_dict.keys())

    def max_frame_id(self) -> int:
        return max(self.__drift_y_dict.keys())


    def _mm_per_pixel(self, frame_id):
        return self.__mm_per_pixel_dict[frame_id]

    def __drift_x(self, frame_id: int) -> float:
        return self.__drift_x_dict[frame_id]

    def __drift_y(self, frame_id: int) -> float:
        return self.__drift_y_dict[frame_id]

    def __get_drift_instantaneous(self, frame_id):
        # type: (int) -> Vector
        drift_x = self.__drift_x(frame_id)
        drift_y = self.__drift_y(frame_id)
        return Vector(drift_x, drift_y)

    def __zoom_instantaneous(self, frame_id):
        # type: (int) -> float
        if frame_id <= self.min_frame_id():
            return 1

        scale_this = self._mm_per_pixel(frame_id)
        scale_prev = self._mm_per_pixel(frame_id - 1) #self.__mm_per_pixel_dict[frame_id-1]

        change = scale_this / scale_prev
        return change

    def __get_frame_physics(self, to_frame_id: int) -> FramePhysics:
        # scale = self.getRedDotsData().getMMPerPixel(to_frame_id)
        scale = self._mm_per_pixel(to_frame_id)
        drift = self.__get_drift_instantaneous(to_frame_id)
        zoom = self.__zoom_instantaneous(to_frame_id)
        #print("In __get_frame_physics: scale", scale, "drift", drift, "zoom", zoom)
        return FramePhysics(to_frame_id, scale, drift, zoom)

    def translatePointCoordinate(self, pointLocation: Point, origFrameID: int, targetFrameID: int) -> Point:
        point_location_new = pointLocation
        timer = MyTimer("translatePointCoordinate")
        individual_frames = FrameId.sequence_of_frames(origFrameID, targetFrameID)
        for idx in range(1, len(individual_frames)):
            to_frame_id = individual_frames[idx]
            # frame_physics = self.__get_frame_physics(to_frame_id)
            if targetFrameID < origFrameID:
                frame_physics = self.__get_frame_physics(to_frame_id-1)
                result = frame_physics.translate_backward(point_location_new)
            else:
                frame_physics = self.__get_frame_physics(to_frame_id)
                result = frame_physics.translate_forward(point_location_new)
            point_location_new = result
        # timer.lap("end "+str(pointLocation)+" loops:"+ str(len(individual_frames))+ ", orig frameId: "+str(origFrameID)+ ", target frameId: "+str(targetFrameID) + " new loc:"+str(point_location_new) )

        return Point(int(round(point_location_new.x, 0)), int(round(point_location_new.y, 0)))

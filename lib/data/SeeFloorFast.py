from lib.FrameId import FrameId
from lib.FramePhysics import FramePhysics
from lib.common import Vector, Point
from lib.infra.MyTimer import MyTimer


class SeeFloorFast:
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'
    _COLNAME_frameNumber = 'frameNumber'
    def __init__(self, seefloorDF):
        self.__df = seefloorDF
        self.__drift_y_dict = None
        self.__drift_x_dict = None
        self.__mm_per_pixel_dict = None

    def __drift_x_fast(self, frame_id: int) -> float:
        if self.__drift_x_dict is None:
            # Lazy loading of cache
            # key is frame_id, value is drift_x_
            self.__drift_x_dict = self.__df.set_index(self._COLNAME_frameNumber)[self.__COLNAME_driftX].to_dict()

        return self.__drift_x_dict[frame_id]

    def __get_drift_instantaneous(self, frame_id):
        # type: (int) -> Vector
        # drift_x = self.__getValueFromDF(self.__COLNAME_driftX, frame_id)
        drift_x = self.__drift_x_fast(frame_id)
        # drift_y = self.__getValueFromDF(self.__COLNAME_driftY, frame_id)
        drift_y = self.__drift_y_fast(frame_id)
        return Vector(drift_x, drift_y)

    def __drift_y_fast(self, frame_id: int) -> float:
        if self.__drift_y_dict is None:
            # Lazy loading of cache
            # key is frame_id, value is drift_y
            self.__drift_y_dict = self.__df.set_index(self._COLNAME_frameNumber)[self.__COLNAME_driftY].to_dict()

        return self.__drift_y_dict[frame_id]

    def minFrameID(self):
        # type: () -> int
        return self.__df[self._COLNAME_frameNumber].min()
    def __zoom_instantaneous(self, frame_id):
        # type: (int) -> float
        if frame_id <= self.minFrameID():
            return 1

        scale_this = self._mm_per_pixel(frame_id)
        scale_prev = self._mm_per_pixel(frame_id - 1) #self.__mm_per_pixel_dict[frame_id-1]

        change = scale_this / scale_prev
        return change

    def __mm_per_pixel_fast(self, frame_id: int) -> float:
        # if !hasattr(self, '__mm_per_pixel_dict'):
        if self.__mm_per_pixel_dict is None:
            # Lazy loading of cache
            # key is frame_id, value is mm_per_pixel
            self.__mm_per_pixel_dict = self.__df.set_index(self._COLNAME_frameNumber)["mm_per_pixel"].to_dict()
        return self.__mm_per_pixel_dict[frame_id]

    def _mm_per_pixel(self, frame_id):
        # return self.__getValueFromDF("mm_per_pixel", frame_id)
        return self.__mm_per_pixel_fast(frame_id)

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

    def __get_frame_physics(self, to_frame_id: int) -> FramePhysics:
        # scale = self.getRedDotsData().getMMPerPixel(to_frame_id)
        scale = self._mm_per_pixel(to_frame_id)
        drift = self.__get_drift_instantaneous(to_frame_id)
        zoom = self.__zoom_instantaneous(to_frame_id)
        #print("In __get_frame_physics: scale", scale, "drift", drift, "zoom", zoom)
        return FramePhysics(to_frame_id, scale, drift, zoom)

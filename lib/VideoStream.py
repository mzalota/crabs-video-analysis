import psutil
import cv2
import pylru
import os
import numpy as np

# import Image
from lib.imageProcessing.Camera import Camera
from lib.model.Image import Image


class VideoStreamException(Exception):
    pass

#List of all properties available for video stream
#https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#gaeb8dd9c89c10a5c63c139bf7c4f5704d


class VideoStream():
    FRAMES_PER_SECOND = 25

    def __init__(self, videoFilepath):
        self._vidcap = cv2.VideoCapture(videoFilepath)
        self.__imagesCache = pylru.lrucache(4) #set the size of cache to be 10 images large

        print("cv2 version", cv2.__version__)
        print ("num_of_frames", self.num_of_frames())
        print ("frame_height", self.frame_height())
        print ("frame_width", self.frame_width())
        print ("frames_per_second", self.frames_per_second())
        print ("codec_code", self.codec_code())

    def num_of_frames(self):
        # type: () -> int
        return int(self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    def frame_width(self):
        # type: () -> int
        return int(self._vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))

    def frame_height(self):
        # type: () -> int
        return int(self._vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def frames_per_second(self):
        # type: () -> int
        return int(self._vidcap.get(cv2.CAP_PROP_FPS))

    def codec_code(self):
        # type: () -> int
        return int(self._vidcap.get(cv2.CAP_PROP_FOURCC))

    def rectification(self):
        # type: () -> int
        return int(self._vidcap.get(cv2.CAP_PROP_RECTIFICATION))


    def read_image(self, frameID):
        # type: (int) -> np
        if  frameID not in self.__imagesCache:
            # image is not in the cache. Read it from VideoCapture and save into cache
            # image = self.read_image_undistorted(frameID).asNumpyArray()
            image = self._read_image_raw(frameID)
            self.__imagesCache[frameID] = image

        return self.__imagesCache[frameID].copy()

    def read_image_obj(self, frameID):
        # type: () -> Image
        return Image(self.read_image(frameID))


    def _read_image_raw(self, frameID: int) -> np:
        self._vidcap.set(cv2.CAP_PROP_POS_FRAMES, float(frameID))
        success, image = self._vidcap.read()
        if not success:
            errorMessage = "Could not read frame " + str(frameID) + " from videofile"
            raise VideoStreamException(errorMessage)
        return image

    def printMemoryUsage(self):
        process = psutil.Process(os.getpid())
        print("memoryUsed: "+self.__toMegaBytes(process.memory_info().rss))

    def __toMegaBytes(self, memoryInBytes):
        memoryInMegabytes = int(memoryInBytes) / (1024 * 1024)
        return str(memoryInMegabytes) + "MB"

    def get_id_of_first_frame(self, step_size):
        # type: (int) -> int
        frame_id = step_size
        while True:
            if frame_id > self.num_of_frames():
                raise Exception("Cannot find a valid frame in stream. Max valid frame is: "+self.num_of_frames())

            try:
                print ("get_id_of_first_frame", frame_id)
                self._read_image_raw(frame_id)
                return frame_id
            except VideoStreamException as error:
                print("Cannot read frame " + str(frame_id) + ", skipping to next")

            frame_id += step_size


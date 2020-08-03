import psutil
from cv2 import cv2
import pylru
import os

from Image import Image

class VideoStreamException(Exception):
    pass

class VideoStream:

    def __init__(self, videoFilepath):
        self._vidcap = cv2.VideoCapture(videoFilepath)
        self.__imagesCache = pylru.lrucache(4) #set the size of cache to be 10 images large

    def readImage(self, frameID):
        # type: (int) -> np
        if  frameID not in self.__imagesCache:
            # image is not in the cache. Read it from VideoCapture and save into cache
            image = self.readFromVideoCapture(frameID)
            self.__imagesCache[frameID] = image

        return self.__imagesCache[frameID].copy()

    def readImageObj(self, frameID):
        # type: () -> Image
        return Image(self.readImage(frameID))

    def readFromVideoCapture(self, frameID):
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

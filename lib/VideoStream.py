import psutil
from cv2 import cv2
import pylru
import os

from Image import Image

class VideoStreamException(Exception):
    pass

class VideoStream:

    def __init__(self, videoFilepath):
        self.__vidcap = cv2.VideoCapture(videoFilepath)
        self.__imagesCache = pylru.lrucache(4) #set the size of cache to be 10 images large

    def readImage(self, frameID):
        if  frameID not in self.__imagesCache:
            # image is not in the cache. Read it from VideoCapture and save into cache
            image = self.__readFromVideoCapture(frameID)
            self.__imagesCache[frameID] = image

        return self.__imagesCache[frameID]

    def readImageObj(self, frameID):
        # type: () -> Image
        return Image(self.readImage(frameID))

    def __readFromVideoCapture(self, frameID):
        self.__vidcap.set(cv2.CAP_PROP_POS_FRAMES, float(frameID))
        success, image = self.__vidcap.read()
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

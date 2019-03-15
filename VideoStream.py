from cv2 import cv2
import pylru

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

    def __readFromVideoCapture(self, frameID):
        self.__vidcap.set(cv2.CAP_PROP_POS_FRAMES, frameID)
        success, image = self.__vidcap.read()
        if not success:
            raise Exception("Could not read Videofile any more")
        return image

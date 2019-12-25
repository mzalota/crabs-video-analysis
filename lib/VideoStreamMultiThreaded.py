from cv2 import cv2

from pebble import synchronized

from lib.Image import Image
from lib.VideoStream import VideoStream, VideoStreamException


class VideoStreamMultiThreaded(VideoStream):

    @synchronized
    def _readFromVideoCapture(self, frameID):
        self._vidcap.set(cv2.CAP_PROP_POS_FRAMES, float(frameID))
        success, image = self._vidcap.read()
        if not success:
            errorMessage = "Could not read frame " + str(frameID) + " from videofile"
            raise VideoStreamException(errorMessage)
        return image

    @synchronized
    def readImageObj(self, frameID):
        # type: () -> Image
        return Image(self.readImage(frameID))
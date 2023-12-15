from cv2 import cv2

from pebble import synchronized

from lib.model.Image import Image
from lib.VideoStream import VideoStream, VideoStreamException


class VideoStreamMultiThreaded(VideoStream):

    @synchronized
    def _read_image_raw(self, frameID):
        self._vidcap.set(cv2.CAP_PROP_POS_FRAMES, float(frameID))
        success, image = self._vidcap.read()
        if not success:
            errorMessage = "Could not read frame " + str(frameID) + " from videofile"
            raise VideoStreamException(errorMessage)
        return image

    @synchronized
    def read_image_obj(self, frameID):
        # type: () -> Image
        return Image(self.read_image(frameID))
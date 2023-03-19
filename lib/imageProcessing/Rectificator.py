import cv2
import numpy as np

from lib.Image import Image
from lib.VideoStream import VideoStream
from lib.imageProcessing.EuclidianPlane import EuclidianPlane
from lib.imageProcessing.PointDetector import PointDetector


class Rectificator():

    def __init__(self, video_stream: VideoStream, frameID, debug_mode=False):
        self.__vs = video_stream
        self.__frameID = frameID
        self.__show_debug = debug_mode

        # By default scale 4K video dowm 4 times
        self.__abs_motion_threshold = 50.0
        self.__init_frame_step = 10
        self.__frame_step_size = 2
        self.__scale_factor = 0.25


    def __estimate_rectify_step_direction(self, frame_step):
        # By default step is positive, but if the video is close to end, make it negative instead
        if self.__frameID + frame_step > self.__vs.num_of_frames():
            return -frame_step
        return frame_step
        

    def generate_rectified_image(self) -> Image:
        print('Attempt to rectify current frame')
        image_to_rectify = self.__vs.read_image_obj(self.__frameID)

        motion = 0.0
        step = self.__init_frame_step

        image1 = image_to_rectify.scale_by_factor(self.__scale_factor)
        image1 = image1.equalize()

        iteration = 0
        while motion < self.__abs_motion_threshold and iteration < 20:
            step = self.__estimate_rectify_step_direction(step)
            frame2_ID = self.__frameID + step

            image2 = self.__vs.read_image_obj(frame2_ID)
            image2 = image2.scale_by_factor(self.__scale_factor)
            image2 = image2.equalize()

            pd = PointDetector(self.__show_debug)
            ret = pd.calculate_keypoints(image1, image2)
            if not ret:
                print('None returned from matcher')
                step += self.__frame_step_size
                iteration += 1
                continue

            ptsA = pd.points_A()
            ptsB = pd.points_B()

            motion = pd.absolute_motion()
            print(f'Motion between frame {self.__frameID} and {frame2_ID} is {motion}')
            step += self.__frame_step_size

        if motion == 0.0:
            print('Unable to rectify current frame: no motion detected')
            return None

        # Calculate translation vector
        try:
            plane = EuclidianPlane(ptsA, ptsB, self.__scale_factor)
            res_img = plane.rectify_image(image_to_rectify)
            res_img = res_img.scale_by_factor(self.__scale_factor)
        except(TypeError, np.linalg.LinAlgError):
            print('Unable to rectify current frame: can not estimate translation vector')
            return None

        if self.__show_debug:
            cv2.imshow('Rectified', res_img.asNumpyArray())
            cv2.waitKey(2000)
            cv2.destroyWindow('Rectified')

        return res_img

        
            

import cv2
import numpy as np

from lib.Image import Image
from lib.Camera import Camera
from lib.common import Point
from lib.VideoStream import VideoStream
from lib.imageProcessing.EuclidianPlane import EuclidianPlane
from lib.imageProcessing.PointDetector import PointDetector


class Rectificator():

    def __init__(self, video_stream: VideoStream, frameID: int, debug_mode=False):
        self.__vs = video_stream
        self.__frame_height = self.__vs.frame_height()
        self.__frame_width = self.__vs.frame_width()
        self.__frameID = frameID
        self.__show_debug = debug_mode

        # By default scale 4K video dowm 4 times
        self.__abs_motion_threshold = 50.0
        self.__init_frame_step = 10
        self.__frame_step_size = 2
        self.__scale_factor = 0.25

        camera = Camera()
        self.__mtx = camera.getCalibrationMatrix()
        self.__dst = camera.getDistortionCoefficients()

        # self.__image_to_rectify = self.__vs.read_image_obj(self.__frameID)
        self.__plane_normal = None


    def generate_rectified_image(self, image_to_rectify: Image) -> Image:
        if self.__plane_normal is None:
            self.__generate_normal(image_to_rectify)
        plane_normal = self.__plane_normal

        if plane_normal is None:
            return None

        rot_mtx = self.__rotate_matrix_from_normal(*plane_normal)
        res_img = self.__rotate_image_plane(image_to_rectify, rot_mtx)
        res_img = Image(res_img)
        # res_img = res_img.scale_by_factor(self.__scale_factor)
        return res_img


    def rectify_point(self, image_to_rectify: Image, point_to_rectify: Point) -> Point:
        if self.__plane_normal is None:
            self.__generate_normal(image_to_rectify)

        return self.__rectifyPoint(point_to_rectify)

    def __generate_normal(self, image_to_rectify: Image) -> None:
        print('Attempt to rectify current frame')
        # image_to_rectify = self.__image_to_rectify

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
            seafloor_plane = EuclidianPlane(ptsA, ptsB, self.__scale_factor, self.__mtx)
            self.__plane_normal = seafloor_plane.compute_normal()

        except(TypeError, np.linalg.LinAlgError):
            print('Unable to rectify current frame: can not estimate translation vector')
            return None


    def get_plane_normal(self):
        return self.__plane_normal


    def load_plane_normal(self, plane_normal: np.ndarray):
        # Use this to provide previously calculated normal
        if plane_normal.shape[0] != 3:
            raise TypeError('Normal must contain 3 values')
        self.__plane_normal = plane_normal


    ##### IMAGE RECTIFICATOR FUNCS ######
    def __estimate_rectify_step_direction(self, frame_step):
        # By default step is positive, but if the video is close to end, make it negative instead
        if self.__frameID + frame_step > self.__vs.num_of_frames():
            return -frame_step
        return frame_step


    def __rotate_matrix_from_normal(self, a, b, c):
        # a,b,c - coordinates of Z component of rotation
        # Get Z component of rotation
        len_Z = np.sqrt(a*a + b*b + c*c)
        a = a / len_Z
        b = b / len_Z
        c = c / len_Z

        Z = (a, b, c) if c > 0 else (-a, -b, -c)

        # Get Y component of rotation from assumption
        # that Y perpendicular to Z and x component of Y is zero
        yy = np.sqrt(1 / (1 + b*b / (c*c)))
        xy = 0.0
        zy = -b * yy / c
        Y = (xy, yy, zy)

        # Get X component of rotation
        X = np.cross(Y, Z)

        ret = np.vstack((X,Y,Z)).transpose()

        return ret

    def __rotate_image_plane(self, image: Image, R):
        """
        Rotation of image plane based on formula
        X' = RX - RD + D
        where X = K_inv*(u,v,1)
        (u', v', 1) = KX'
        """
        img = image.asNumpyArray()

        K = self.__mtx

        # Load intrinsic and invert it
        K_inv = np.linalg.inv(K)

        # Augmented inverse for further mtx multiplication
        K_inv1 = np.vstack((K_inv, np.array([0,0,1])))

        # Z distance constant, 1
        d = np.array([0,0,1]).transpose()

        # Calculate translation vector
        t = (d - R.dot(d)).reshape((3,1))
        R1 = np.hstack((R, t))

        # Calc result homography
        matrix = K @ R1 @ K_inv1

        # to try to avoid cropping read https://stackoverflow.com/questions/13063201/how-to-show-the-whole-image-when-using-opencv-warpperspective

        # Rotate image
        tf_img = cv2.warpPerspective(img, np.linalg.inv(matrix), (img.shape[1], img.shape[0]))

        # return transformed image
        normalized = cv2.normalize(tf_img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        return normalized


    ##### POINT RECTIFICATOR FUNCS ######
    def __rectifyPoint(self, point: Point) -> Point:
        mtx = self.__mtx
        normal = self.__plane_normal
        R = self.__rotate_matrix_from_normal(*normal)
        K = mtx.copy()
        K_inv = np.vstack((np.linalg.inv(K), np.array([0,0,1])))
        d = np.array([0,0,1]).transpose()
        t = (d - R.dot(d)).reshape((3,1))
        R1 = np.hstack((R, t))
        matrix = K @ R1 @ K_inv
        matrix = np.linalg.inv(matrix)
        ptN = np.append(point.x, 1.0)
        ptNN = matrix @ ptN
        recPt = (ptNN[0] / ptNN[-1], ptNN[1] / ptNN[-1])

        return Point(recPt[0], recPt[1])


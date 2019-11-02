# crabs-video-analysis

#command to install opencv library so that "import cv2" command does not fail
#python -m pip install opencv-python
#python -m pip install numpy

#python -m pip install --upgrade imutils
#python -m pip install scikit-image
#python -m pip install scipy
#python -m pip install matplotlib
#python -m pip install pyautogui ##ERROR#Command "python setup.py egg_info" failed with error code 1 in c:\users\user\appdata\local\temp\pip-install-fiv6z_\pygetwindow\
#pip install pyautogui==0.9.35

#python -m pip install psutil
#python -m pip install pylru

#https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

#from skimage.measure import structural_similarity as ssim

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4

ffmpeg -i "D:\Video_Biology\Kara\2018\AMK72\2018_09_15_St_5993\V4__R_20180915_210447.avi" -strict -2 output.mp4
#https://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html#gsc.tab=0

#https://www.geeksforgeeks.org/template-matching-using-opencv-in-python/


#https://stackoverflow.com/questions/13564851/how-to-generate-keyboard-events-in-python


# https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames

# ffmpeg -i "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi" -strict -2 ../output_st_v3.mp4
# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 -vcodec copy -bsf h264_mp4toannexb "%d.h264"
# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 "output/%d.h264"
# ffmpeg -i i"C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4

Command to copy directories from S3 to Maxim's laptop.
aws --no-verify-ssl s3 cp s3://crab-videos/2019-Kara/St6267_19/ . --recursive

Glossary:

Frame - a single image from video stream. A typical 4,5 minutes video file is encoded consists of about 14000 frames (50 frames-per-second). 
SeeFloorSection - a rectangular subimage in a frame
Feature - an object on the see floor that appears in multiple frames. Feature could just be a part of see floor without any distinct object, just a distinct combination of holes and kills.
 
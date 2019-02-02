#command to install opencv library so that "import cv2" command does not fail
#python -m pip install opencv-python
#python -m pip install numpy

#from skimage.measure import structural_similarity as ssim
#import matplotlib.pyplot as plt


# Python program to illustrate
# template matching
import cv2

from RedDot import highlightMatchedFeature

# Read the main image
imagePath = 'C:/workspaces/AnjutkaVideo/frames/frame7.jpg'
feature_image = 'C:/workspaces/AnjutkaVideo/crab_from_frame_1.png'

img_rgb = cv2.imread(imagePath)
template = cv2.imread(feature_image, 0)

highlightMatchedFeature(img_rgb, template)
cv2.imshow('Detected',img_rgb) 

cv2.waitKey(0)
cv2.destroyAllWindows()
#command to install opencv library so that "import cv2" command does not fail
#python -m pip install opencv-python
#python -m pip install numpy

#from skimage.measure import structural_similarity as ssim
#import matplotlib.pyplot as plt


# Python program to illustrate  
# template matching 
import cv2 
import numpy as np 
  
# Read the main image 
img_rgb = cv2.imread('C:/workspaces/AnjutkaVideo/frames/frame7.jpg')
  
# Convert it to grayscale 
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
  
# Read the template 
template = cv2.imread('C:/workspaces/AnjutkaVideo/crab_from_frame_1.png',0) 
  
# Store width and heigth of template in w and h 
w, h = template.shape[::-1] 
  
# Perform match operations. 
res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
  
# Specify a threshold (it was 0.8)
threshold = 0.6
  
# Store the coordinates of matched area in a numpy array 
loc = np.where( res >= threshold)  
  
# Draw a rectangle around the matched region. 
for pt in zip(*loc[::-1]): 
    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2) 
  
# Show the final image with the matched area. 
cv2.imshow('Detected',img_rgb) 

cv2.waitKey(0)
cv2.destroyAllWindows()
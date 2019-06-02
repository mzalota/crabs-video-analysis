import cv2

from FramesStitcher import FramesStitcher
from ImageWindow import ImageWindow
from VideoStream import VideoStream
from common import Point, Box

print(cv2.__version__)
cv2.startWindowThread()

#imageWin = ImageWindow("mainWithRedDots", Point(700, 200))
imageWin2 = ImageWindow.createWindow("topSubimage",Box(Point(0,0),Point(960,740)))


#videoFileName="V5__R_20180915_211343"
#videoFileName="V6__R_20180915_212238"
filename = "V6__R_20180915_212238"
rootDirectory = "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V6__R_20180915_212238"


videoFileName = filename

#videoStream = VideoStream("C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"+videoFileName+".avi")
videoStream = VideoStream(rootDirectory+"/"+videoFileName+".avi")

framesStitcher = FramesStitcher(videoStream, rootDirectory, videoFileName)
#framesToSaveToFile = framesStitcher.determineFrames()
#print("Dataframe Contains:", framesToSaveToFile)

framesStitcher.saveFramesToFile()


#exit()


# Open File where Frame Info will be written using Semicolumn as a delimiter. Write the Header row into the file
#csvFilePath = 'C:/workspaces/AnjutkaVideo/redDots_log08.csv'


# src3 = cv2.imread("C:/Users/zal0001m/Documents/Private/AnjutkaVideo/IMG_20180814_181351.jpg")
# cv2.imshow("hi",src3)

# https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames

# vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi')
# vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/output_v1.mp4')
# vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V2_R_20180911_165730.avi' )

#vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi')


# vidcap = cv2.VideoCapture("D:/Video_Biology/Kara/2018/AMK72/2018_09_15_St_5993/V4__R_20180915_210447.avi")
# ffmpeg -i "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi" -strict -2 ../output_st_v3.mp4

#imageWinNoBoxes = ImageWindow("withoutFeatureBoxes", Point(700, 20))




cv2.destroyAllWindows()

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


cv2.destroyAllWindows()

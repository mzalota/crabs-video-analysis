import traceback

import cv2




from Frame import Frame
from FramesStitcher import FramesStitcher
from Image import Image
from ImageWindow import ImageWindow
from VelocityDetector import VelocityDetector
from VideoStream import VideoStream
from common import Point, Box

filename = "V6__R_20180915_212238"
rootDirectory = "C:/workspaces/AnjutkaVideo/output/"

framesStitcher = FramesStitcher()
framesToSaveToFile = framesStitcher.determineFrames(rootDirectory, filename+"_toCut")

print("Dataframe Contains:", framesToSaveToFile)


exit()



# filenameFull = os.path.basename(filepath)
# filename = os.path.splitext(filenameFull)[0]


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


print(cv2.__version__)
cv2.startWindowThread()

velocityDetector = VelocityDetector()
vf = None
#imageWin = ImageWindow("mainWithRedDots", Point(700, 200))
imageWin2 = ImageWindow.createWindow("topSubimage",Box(Point(0,0),Point(960,740)))

#videoFileName="V5__R_20180915_211343"
#videoFileName="V6__R_20180915_212238"
videoFileName = filename

videoStream = VideoStream("C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"+videoFileName+".avi")


def processFrame(nextFrame, frame, prevFrame):
    print 'Read a new frame: ', nextFrameNumber
    try:

        #frame.saveImageToFile(rootDirectory+"/"+videoFileName+"/")
        #frame.saveCollageToFile(rootDirectory+"/"+videoFileName+"/")

        image = frame.attachNeighbourFrames(nextFrame, prevFrame, 800)
        imgObj = Image(image)
        imageFilePath = frame.constructFilePath(rootDirectory + "/" + videoFileName + "/")
        print "writing frame image to file: "+imageFilePath
        imgObj.writeToFile(imageFilePath )

        #imageWin2.showWindowAndWaitForClick(image)

    except Exception as error:
        print ("no more frames to read from video ")
        print('Caught this error: ' + repr(error))
        traceback.print_exc()

nextFrameNumber = 0
frameNumber = 0
prevFrameNumber= 0
line_count = 0

print(framesToSaveToFile.size)
print(framesToSaveToFile.count())

for index in range(len(framesToSaveToFile.index)-2):

    print(index)

    prevFrameNumber = framesToSaveToFile['frameNumber'][index]
    frameNumber = framesToSaveToFile['frameNumber'][index+1]
    nextFrameNumber = framesToSaveToFile['frameNumber'][index+2]

    if nextFrameNumber > 0 and frameNumber > 0:
        prevFrame = Frame(prevFrameNumber, videoStream)
        frame = Frame(frameNumber, videoStream)
        nextFrame = Frame(nextFrameNumber, videoStream)
        processFrame(nextFrame, frame, prevFrame)

    line_count += 1
print('Processed ' + str(line_count) + ' lines.')

cv2.destroyAllWindows()

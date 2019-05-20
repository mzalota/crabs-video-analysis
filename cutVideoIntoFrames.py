import cv2
#from pandas.compat.numpy import np

import math

import csv
import pandas as pd


from Frame import Frame
from Image import Image
from ImageWindow import ImageWindow
from VelocityDetector import VelocityDetector
from VideoStream import VideoStream
from common import Point, Box


def determineFrames():

    rootDirectory = "C:/workspaces/AnjutkaVideo/output/"

    framesFilePath = rootDirectory+"/V5__R_20180915_211343_toCut_2.csv"

    #cutFramesFilePath = rootDirectory+"/V5__R_20180915_211343_framesToCut_aaaa.csv"
    #cutFramesFile = open(cutFramesFilePath, 'wb')

    # Creating an empty Dataframe with column names only
    #dfObj = pd.DataFrame(columns=['FrameNumber', 'UserName', 'Action'])
    dfObj = pd.DataFrame(columns=['frameNumber', 'count'])
    #print("Dataframe Contens ", dfObj)

    yDrift = 0
    frameNumber = 0
    prevFrameNumber= 0
    cumulativeDrift = 0
    printedFrames = 1
    prevFrameToUse = 0
    with open(framesFilePath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print('Column names are: '+", ".join(row))
                line_count += 1
            else:
                prevFrameNumber = frameNumber
                prevYDrift = yDrift

                frameNumber = row[0]
                yDrift = float(row[1].replace(",","."))

                prevCumulativeDrift = cumulativeDrift
                cumulativeDrift += yDrift

                driftPerFrame = yDrift/(int(frameNumber)-int(prevFrameNumber))
                #print (frameNumber, yDrift, cumulativeDrift, prevFrameNumber, prevYDrift, prevCumulativeDrift, driftPerFrame)

                nextFrameBreak= 1080*printedFrames
                if cumulativeDrift > (nextFrameBreak):
                    pixelsToBacktrack = cumulativeDrift - nextFrameBreak
                    framesToBacktrack = pixelsToBacktrack/driftPerFrame
                    frameToUse = int(frameNumber)-math.floor(framesToBacktrack)
                    frameJump = frameToUse - prevFrameToUse
                    print (int(frameToUse), printedFrames, frameJump, cumulativeDrift, pixelsToBacktrack, framesToBacktrack, math.floor(framesToBacktrack))
                    printedFrames = printedFrames+1
                    prevFrameToUse = frameToUse

                    dfObj = dfObj.append({'frameNumber': int(frameToUse), 'count': line_count}, ignore_index=True)

                    #cutFramesFile.write(str(int(frameToUse)) + "\n")
                    #cutFramesFile.flush()

                line_count += 1
        print('Processed '+str(line_count)+' lines.')

    #print("Dataframe Contens ", dfObj)
    return dfObj
    #cutFramesFile.close()

framesToSaveToFile = determineFrames()
#print("Dataframe Contens ", framesToSaveToFile)




#exit()


rootDirectory = "C:/workspaces/AnjutkaVideo/output/"
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

videoFileName="V5__R_20180915_211343"

videoStream = VideoStream("C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"+videoFileName+".avi")


def processFrame(nextFrame, frame, prevFrame):
    print 'Read a new frame: ', nextFrameNumber
    return
    try:

        #frame.saveImageToFile(rootDirectory+"/"+videoFileName+"/")
        #frame.saveCollageToFile(rootDirectory+"/"+videoFileName+"/")

        image = frame.attachNeighbourFrames(nextFrame, prevFrame, 800)
        imgObj = Image(image)
        imageFilePath = frame.constructFilePath(rootDirectory + "/" + videoFileName + "/")
        imgObj.writeToFile(imageFilePath )

        #imageWin2.showWindowAndWaitForClick(image)


    except Exception as error:
        print ("no more frames to read from video ")
        print('Caught this error: ' + repr(error))

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
    #print (nextFrameNumber)
    #prevFrameNumber = frameNumber
    #frameNumber = nextFrameNumber
    #nextFrameNumber = row['frameNumber']


    if nextFrameNumber > 0 and frameNumber > 0:
        prevFrame = Frame(prevFrameNumber, videoStream)
        frame = Frame(frameNumber, videoStream)
        nextFrame = Frame(nextFrameNumber, videoStream)
        processFrame(nextFrame, frame, prevFrame)

    line_count += 1
print('Processed ' + str(line_count) + ' lines.')

exit()

import csv

framesFilePath = rootDirectory+"/V5__R_20180915_211343_framesToCut.csv"
nextFrameNumber = 0
frameNumber = 0
prevFrameNumber= 0
with open(framesFilePath) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print('Column names are: '+", ".join(row))
            line_count += 1
        else:
            prevFrameNumber = frameNumber
            frameNumber = nextFrameNumber
            nextFrameNumber = row[0]
            print (nextFrameNumber)

            if nextFrameNumber > 0 and frameNumber > 0:
                prevFrame = Frame(prevFrameNumber, videoStream)
                frame = Frame(frameNumber, videoStream)
                nextFrame = Frame(nextFrameNumber, videoStream)
                processFrame(nextFrame, frame, prevFrame)

            line_count += 1
    print('Processed '+str(line_count)+' lines.')


        # cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file

cv2.destroyAllWindows()

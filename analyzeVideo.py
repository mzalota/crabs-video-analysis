# command to install opencv library so that "import cv2" command does not fail
# python -m pip install opencv-python

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 -vcodec copy -bsf h264_mp4toannexb "%d.h264"
# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 "output/%d.h264"
# ffmpeg -i i"C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4

import cv2

from Frame import Frame
from Image import Image
from ImageWindow import ImageWindow
from VelocityDetector import VelocityDetector
from RedDotsDetector import RedDotsDetector
from VideoStream import VideoStream
from common import Point, Box
from logger import Logger


rootDirectory = "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"

#videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi'
#videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V2_R_20180911_165730.avi'
#videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V3_R_20180911_170159.avi'
#videoFilenameFull = '2018_09_16_St_5994/V3_R_20180916_012323.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/output_st_v4.mp4'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V4__R_20180915_210447.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V5__R_20180915_211343.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V6__R_20180915_212238.avi'

videoFilename = "V6__R_20180915_212238"

videoFilepath = rootDirectory+"V6__R_20180915_212238.avi"


#filenameFull = os.path.basename(videoFilenameFull)
#videoFilename = os.path.splitext(filenameFull)[0]

videoStream = VideoStream(videoFilepath)

print "videoFilename is "+videoFilename



# Open File where Frame Info will be written using Semicolumn as a delimiter. Write the Header row into the file


reddotsFilepath = rootDirectory + "/" + videoFilename + "/" + videoFilename + '_reddots.csv'
driftsFilepath = rootDirectory + "/" + videoFilename + "/"+videoFilename + '_drifts.csv'

logger = Logger(reddotsFilepath, driftsFilepath)

headerRow = RedDotsDetector.infoHeaders()
headerRow.insert(0, "frameNumber")
logger.writeToRedDotsFile(headerRow)

driftsFileHeaderRow = VelocityDetector.infoHeaders()
driftsFileHeaderRow.insert(0, "frameNumber")
#driftsFileHeaderRow.append("frameNumber")
logger.writeToDriftsFile(driftsFileHeaderRow)



# https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames

# ffmpeg -i "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi" -strict -2 ../output_st_v3.mp4



# print "image shape"
# print image.shape
# (1080L, 1920L, 3L)


print(cv2.__version__)
cv2.startWindowThread()

velocityDetector = VelocityDetector()
vf = None
imageWin = ImageWindow("mainWithRedDots", Point(700, 200))

stepSize = 5
startingFrameID = 5

success = True
while success:

    windowName = 'Detected_' + str(startingFrameID)

    try:
        image = videoStream.readImage(startingFrameID)
        frame = Frame(startingFrameID, videoStream)
    except Exception as error:
        print ("no more frames to read from video ")
        print('Caught this error: ' + repr(error))
        break

    '''
    vf_prev = vf
    vf = RedDotsDetector(frame, vf_prev)
    vf.isolateRedDots()
    withRedDotsObj = vf.drawBoxesAroundRedDots()
    withRedDots = frame.getImgObj().asNumpyArray()

    row = vf.infoAboutFrame()
    row.insert(0, count)
    logger.writeToRedDotsFile(row)
    print row
    '''

    # findBrightestSpot()

    velocityDetector.detectVelocity(frame, image)
    driftVector = velocityDetector.getMedianDriftVector()

    #print "prevDriftLength: "+ str(prevDriftLength)
    if driftVector is None:
        #insert wrong values
        driftsRow = list()
        driftsRow.append(startingFrameID)
        driftsRow.append(-888)
        driftsRow.append(-999)
        driftsRow.append(-777)
        driftsRow.append(-45)
        driftsRow.append(0)
        driftsRow.append(velocityDetector.getDriftsCount())
        driftsRow.append("")
        driftsRow.append(velocityDetector.getDriftsAsString())
        driftsRow.append("EMPTY_DRIFTS")

    else:
        driftLength = driftVector.length()
        driftsRow = velocityDetector.infoAboutDrift()
        driftsRow.insert(0, startingFrameID)

    print driftsRow
    logger.writeToDriftsFile(driftsRow)


    #img = Image(withRedDots)
    img = Image(image)
    img.drawDriftVectorOnImage(driftVector)

    #withRedDots = img.asNumpyArray()

    #imageWin.showWindowAndWait(img.asNumpyArray(), 1000)

    #imageWin.showWindowAndWaitForClick(img.asNumpyArray())

    # cv2.destroyAllWindows()


    startingFrameID += stepSize

    #gc.collect()
    #printMemoryUsage()

    if startingFrameID > 99100:
        break

logger.closeFiles()


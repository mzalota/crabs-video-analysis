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
print "videoFilepath is "+videoFilepath

videoStream = VideoStream(videoFilepath)


reddotsFilepath = rootDirectory + "/" + videoFilename + "/" + videoFilename + '_reddots.csv'

logger = Logger(reddotsFilepath)

headerRow = RedDotsDetector.infoHeaders()
headerRow.insert(0, "frameNumber")
logger.writeToFile(headerRow)


print(cv2.__version__)
cv2.startWindowThread()

velocityDetector = VelocityDetector()
vf = None
imageWin = ImageWindow("mainWithRedDots", Point(700, 200))

stepSize = 5
startingFrameID = 20000

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

    vf_prev = vf
    vf = RedDotsDetector(frame, vf_prev)
    vf.isolateRedDots()
    withRedDotsObj = vf.drawBoxesAroundRedDots()
    withRedDots = frame.getImgObj().asNumpyArray()

    row = vf.infoAboutFrame()
    row.insert(0, startingFrameID)
    logger.writeToFile(row)
    print row


    # findBrightestSpot()

    imageWin.showWindowAndWait(withRedDots, 1000)
    #imageWin.showWindowAndWaitForClick(withRedDots)

    startingFrameID += stepSize

    #gc.collect()
    #printMemoryUsage()

    if startingFrameID > 99100:
        break

logger.closeFile()
cv2.destroyAllWindows()


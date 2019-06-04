import cv2

from lib.Frame import Frame
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from lib.VelocityDetector import VelocityDetector
from lib.VideoStream import VideoStream
from lib.common import Point
from lib.Logger import Logger


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
videoStream = VideoStream(videoFilepath)
print "videoFilepath is "+videoFilepath

driftsFilepath = rootDirectory + "/" + videoFilename + "/"+videoFilename + '_drifts.csv'
logger = Logger(driftsFilepath)


driftsFileHeaderRow = VelocityDetector.infoHeaders()
driftsFileHeaderRow.insert(0, "frameNumber")

logger.writeToFile(driftsFileHeaderRow)

# print "image shape"
# print image.shape
# (1080L, 1920L, 3L)
#print(cv2.__version__)

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

    # findBrightestSpot()

    velocityDetector.detectVelocity(frame, image)
    driftVector = velocityDetector.getMedianDriftVector()

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
    #logger.writeToFile(driftsRow)

    img = Image(image)
    img.drawDriftVectorOnImage(driftVector)

    #imageWin.showWindowAndWait(img.asNumpyArray(), 1000)
    imageWin.showWindowAndWaitForClick(img.asNumpyArray())


    startingFrameID += stepSize

    if startingFrameID > 99100:
        break


logger.closeFile()
cv2.destroyAllWindows()

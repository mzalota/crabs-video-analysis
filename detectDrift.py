import traceback

import cv2

from lib.FolderStructure import FolderStructure
from lib.Frame import Frame
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from lib.VelocityDetector import VelocityDetector
from lib.VideoStream import VideoStream, VideoStreamException
from lib.common import Point
from lib.Logger import Logger


#rootDirectory = "C:/Users/User/Documents/data/Kara/Video/V_Analysis"
#rootDirectory = "C:/workspaces/AnjutkaVideo/seeps/c15"

#rootDirectory = "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
rootDirectory = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"

#videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi'
#videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V2_R_20180911_165730.avi'
#videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V3_R_20180911_170159.avi'
#videoFilenameFull = '2018_09_16_St_5994/V3_R_20180916_012323.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/output_st_v4.mp4'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V4__R_20180915_210447.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V5__R_20180915_211343.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V6__R_20180915_212238.avi'

#specify filename again
videoFilename = "V3_R_20180911_170159"
#videoFilename = "V3__R_20180915_205551"
#videoFilename = "V6__R_20180915_212238"
#videoFilename = "V3_R_20180911_170159"

#videoFilename = "V20180825_191129_001"

#videoFilepath = rootDirectory+"/"+videoFilename+".avi"
#videoStream = VideoStream(videoFilepath)
#print "videoFilepath is "+videoFilepath

#driftsFilepath = rootDirectory + "/" + videoFilename + "/"+videoFilename + '_drifts.csv'

folderStruct = FolderStructure(rootDirectory, videoFilename)
videoStream = VideoStream(folderStruct.getVideoFilepath())
logger = Logger.openInOverwriteMode(folderStruct.getRawDriftsFilepath())

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

stepSize = 2
frameID = 5

success = True
while success:

    windowName = 'Detected_' + str(frameID)

    try:
        frame = Frame(frameID, videoStream)
        velocityDetector.detectVelocity(frame)
    except VideoStreamException as error:
        if frameID >300:
            print ("no more frames to read from video ")
            print(repr(error))
            # traceback.print_exc()
            break
        else:
            print "cannot read frame " + str(frameID) + ", skipping to next"
            frameID += stepSize
            continue

    except Exception as error:
        print('Caught this error: ' + repr(error))
        traceback.print_exc()
        break

    # findBrightestSpot()

    driftVector = velocityDetector.getMedianDriftVector()
    if driftVector is None:
        driftsRow = velocityDetector.emptyRow()
        driftsRow.insert(0, frameID)
    else:
        driftLength = driftVector.length()
        driftsRow = velocityDetector.infoAboutDrift()
        driftsRow.insert(0, frameID)

    print driftsRow
    logger.writeToFile(driftsRow)

    img = frame.getImgObj()
    img.drawDriftVectorOnImage(driftVector)

    #imageWin.showWindowAndWait(img.asNumpyArray(), 1000)
    #imageWin.showWindowAndWaitForClick(img.asNumpyArray())

    frameID += stepSize

    if frameID > 99100:
        break


logger.closeFile()
cv2.destroyAllWindows()

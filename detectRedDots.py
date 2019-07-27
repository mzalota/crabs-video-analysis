import cv2

from lib.FolderStructure import FolderStructure
from lib.Frame import Frame
from lib.ImageWindow import ImageWindow
from lib.VelocityDetector import VelocityDetector
from lib.RedDotsDetector import RedDotsDetector
from lib.VideoStream import VideoStream
from lib.common import Point
from lib.Logger import Logger


#rootDirectory = "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"

#videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi'
#videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V2_R_20180911_165730.avi'
#videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V3_R_20180911_170159.avi'
#videoFilenameFull = '2018_09_16_St_5994/V3_R_20180916_012323.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/output_st_v4.mp4'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V4__R_20180915_210447.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V5__R_20180915_211343.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V6__R_20180915_212238.avi'

#videoFilename = "V6__R_20180915_212238"


# rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
rootDir = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"

# videoFileName = "V4__R_20180915_210447"
# videoFileName = "V6__R_20180915_212238"
#videoFileName = "V3_R_20180911_170159"
videoFileName = "V2_R_20180911_165730"
# videoFileName = "V2_R_20180911_165730"

folderStruct = FolderStructure(rootDir, videoFileName)

#StreamToLogger(folderStruct.getLogFilepath())

videoStream = VideoStream(folderStruct.getVideoFilepath())

reddotsFilepath = folderStruct.getRedDotsFilepath()
#reddotsFilepath = rootDirectory + "/" + videoFilename + "/" + videoFilename + '_reddots.csv'

logger = Logger(reddotsFilepath)

#headerRow = RedDotsDetector.infoHeaders()
headerRow =  []
headerRow.append("frameNumber")
headerRow.append("dotName")
headerRow.append("centerPoint_x")
headerRow.append("centerPoint_y")
headerRow.append("topLeft_x")
headerRow.append("topLeft_y")
headerRow.append("bottomRight_x")
headerRow.append("bottomRight_y")
headerRow.append("diagonal")

logger.writeToFile(headerRow)


print(cv2.__version__)
cv2.startWindowThread()

velocityDetector = VelocityDetector()
vf = None
imageWin = ImageWindow("mainWithRedDots", Point(700, 200))

stepSize = 5
startingFrameID = 150

success = True
while success:

    windowName = 'Detected_' + str(startingFrameID)

    try:
        image = videoStream.readImage(startingFrameID)
        frame = Frame(startingFrameID, videoStream)
    except Exception as error:
        if startingFrameID >300:
            print ("no more frames to read from video ")
            print(repr(error))
            # traceback.print_exc()
            break
        else:
            print "cannot read frame " + str(startingFrameID) + ", skipping to next"
            startingFrameID += stepSize
            continue

    vf_prev = vf
    vf = RedDotsDetector(frame, vf_prev)
    vf.isolateRedDots()
    withRedDotsObj = vf.drawBoxesAroundRedDots()
    withRedDots = frame.getImgObj().asNumpyArray()

    if vf.getRedDot1().dotWasDetected():
        row = vf.getRedDot1().infoAboutDot()
        row.insert(0, startingFrameID)
        row.insert(1, "redDot1")
        logger.writeToFile(row)
        print row

    if vf.getRedDot2().dotWasDetected():
        row = vf.getRedDot2().infoAboutDot()
        row.insert(0, startingFrameID)
        row.insert(1, "redDot2")
        logger.writeToFile(row)
        print row

    #if vf.dotsWasDetected():
    #    row = vf.infoAboutFrame()
    #    row.insert(0, startingFrameID)
    #    logger.writeToFile(row)
    #    print row


    # findBrightestSpot()

    #imageWin.showWindowAndWait(withRedDots, 1000)
    #imageWin.showWindowAndWaitForClick(withRedDots)

    startingFrameID += stepSize

    #gc.collect()
    #videoStream.printMemoryUsage()

    if startingFrameID > 99100:
        break

logger.closeFile()
cv2.destroyAllWindows()


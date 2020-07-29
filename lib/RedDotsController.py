
from lib.FolderStructure import FolderStructure
from lib.Frame import Frame
from lib.RedDotsDetector import RedDotsDetector
from lib.VideoStream import VideoStream
from lib.Logger import Logger

#https://www.pyimagesearch.com/2016/10/31/detecting-multiple-bright-spots-in-an-image-with-python-and-opencv/
from lib.data.RedDotsRawData import RedDotsRawData


class RedDotsController:

    def run(self, folderStruct):
        # type: (FolderStructure) -> void

        videoStream = VideoStream(folderStruct.getVideoFilepath())
        logger = Logger(folderStruct.getRedDotsRawFilepath())
        #headerRow = RedDotsDetector.infoHeaders()

        headerRow = RedDotsRawData.headerRow()
        logger.writeToFile(headerRow)

        vf = None
        stepSize = 5
        frame_id = 5
        success = True
        while success:
            print ("frame_id", frame_id)
            frame = Frame(frame_id, videoStream)

            vf_prev = vf
            vf = RedDotsDetector(frame, vf_prev)
            try:
                vf.isolateRedDots()
            except Exception as error:
                if frame_id > 300:
                    print ("no more frames to read from video ")
                    print(repr(error))
                    # traceback.print_exc()
                    break
                else:
                    print "cannot read frame " + str(frame_id) + ", skipping to next"
                    frame_id += stepSize
                    continue

            if vf.getRedDot1().dotWasDetected():
                row = vf.getRedDot1().infoAboutDot()
                row.insert(0, frame_id)
                row.insert(1, "redDot1")
                logger.writeToFile(row)
                print row

            if vf.getRedDot2().dotWasDetected():
                row = vf.getRedDot2().infoAboutDot()
                row.insert(0, frame_id)
                row.insert(1, "redDot2")
                logger.writeToFile(row)
                print row

            frame_id += stepSize

            # videoStream.printMemoryUsage()

            if frame_id > 99100:
                break

        logger.closeFile()


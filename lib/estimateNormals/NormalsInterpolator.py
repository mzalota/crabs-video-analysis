import traceback
from lib.infra.FolderStructure import FolderStructure
from lib.Frame import Frame
from lib.infra.Configurations import Configurations
from lib.imageProcessing.Rectificator import Rectificator
from lib.VideoStream import VideoStream, VideoStreamException
from lib.imageProcessing.Analyzer import Analyzer
from lib.estimateNormals.NormalsRawData import NormalsRawData
from lib.estimateNormals.NormalsInterpData import NormalsInterpData
import cv2

#https://www.pyimagesearch.com/2016/10/31/detecting-multiple-bright-spots-in-an-image-with-python-and-opencv/


class NormalsInterpolator:

    __loop_count = 0

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> None
        self.__configs = Configurations(folderStruct)
        self.__nrmRaw = NormalsRawData.createFromCSVFile(folderStruct)
        self.__nrmInterp = NormalsInterpData.createNewAndReplaceExistingCSVFile(folderStruct)

    def run(self):
        # type: () -> None
        self.__loop_thru_all_frames()
        self.__nrmRaw.closeOpenFiles()

    def __loop_thru_all_frames(self):
        stepSize = 5
        frame_id = self.__videoStream.get_id_of_first_frame(stepSize)

        while True:
            self.__loop_count += 1
            print("frame_id", frame_id)
            frame = Frame(frame_id, self.__videoStream)

            try:
                cur_img = frame.getImgObj()
                an = Analyzer(cur_img)
                if an.getOverexposedRatio() > 1.0:
                    print('Skipping overexposed image')
                    raise VideoStreamException
                self.__compute_current_frame_normal(frame, frame_id)
            except VideoStreamException as error:
                print("cannot read frame " + str(frame_id) + ", skipping to next")
                print(repr(error))
            except Exception as error:
                print('Caught this error: ' + repr(error))
                traceback.print_exc()
                break

            frame_id += stepSize
            if frame_id > self.__videoStream.num_of_frames():
                break
            # videoStream.printMemoryUsage()

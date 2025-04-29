import traceback
from lib.infra.FolderStructure import FolderStructure
from lib.Frame import Frame
from lib.infra.Configurations import Configurations
from lib.imageProcessing.Rectificator import Rectificator
from lib.VideoStream import VideoStream, VideoStreamException

#https://www.pyimagesearch.com/2016/10/31/detecting-multiple-bright-spots-in-an-image-with-python-and-opencv/
from lib.estimateNormals.NormalsRawData import NormalsRawData


class EstimateNormalsController:

    __loop_count = 0

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> None
        self.__configs = Configurations(folderStruct)
        self.__nrmRaw = NormalsRawData.createNewAndReplaceExistingCSVFile(folderStruct)
        self.__videoStream = VideoStream.instance(folderStruct.getVideoFilepath())
        self.__show_debug_UI = False


    def run(self):
        # type: () -> None
        self.__loop_thru_all_frames()
        self.__nrmRaw.closeOpenFiles()

    def run_with_debug_UI(self):
        self.__show_debug_UI = True
        self.run()

    def __loop_thru_all_frames(self):
        stepSize = 5
        frame_id = self.__videoStream.get_id_of_first_frame(stepSize)

        while True:
            self.__loop_count += 1
            print("frame_id", frame_id)
            frame = Frame(frame_id, self.__videoStream)

            try:
                frame.getImgObj()
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

    def __compute_current_frame_normal(self, frame, frame_id):
        # type: (Frame, int) -> None
        img = frame.getImgObj()
        vf = Rectificator(self.__videoStream, frame_id, self.__show_debug_UI)
        vf.generate_plane_normal(img)
        self.__add_normal_info_for_saving(frame_id, vf.get_plane_normal())


    def __add_normal_info_for_saving(self, frame_id, planeNormal):
        # type: (int, np.ndarray) -> object
        self.__nrmRaw.addNormal(frame_id, planeNormal)





from lib.FolderStructure import FolderStructure
from lib.Frame import Frame
from lib.infra.Configurations import Configurations
from lib.reddots.RedDotsDetector import RedDotsDetector
from lib.VideoStream import VideoStream

#https://www.pyimagesearch.com/2016/10/31/detecting-multiple-bright-spots-in-an-image-with-python-and-opencv/
from lib.data.RedDotsRawData import RedDotsRawData

class DetectRedDotsController:
    __loop_count = 0

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> None
        self.__configs = Configurations(folderStruct)
        self.__rdRaw = RedDotsRawData.createNewAndReplaceExistingCSVFile(folderStruct)
        self.__videoStream = VideoStream(folderStruct.getVideoFilepath())
        self.__show_debug_UI = False

    def run(self):
        # type: () -> None
        self.__loop_thru_all_frames()
        self.__rdRaw.closeOpenFiles()

    def run_with_debug_UI(self):
        self.__show_debug_UI = True
        self.run()

    def __loop_thru_all_frames(self):
        stepSize = 5
        frame_id = self.__videoStream.get_id_of_first_frame(stepSize)
        while True:
            self.__loop_count += 1
            print ("frame_id", frame_id)
            frame = Frame(frame_id, self.__videoStream)

            try:
                frame.getImgObj()
            except Exception as error:
                if frame_id > 300:
                    print ("no more frames to read from video ")
                    print(repr(error))
                    # traceback.print_exc()
                    break
                else:
                    print("cannot read frame " + str(frame_id) + ", skipping to next")
                    frame_id += stepSize
                    continue

            self.__detect_red_dots_on_frame(frame, frame_id)

            frame_id += stepSize
            if frame_id > self.__videoStream.num_of_frames():
                break
            # videoStream.printMemoryUsage()

        # cv2.destroyAllWindows()

    def __detect_red_dots_on_frame(self, frame, frame_id):
        vf = RedDotsDetector(frame, self.__configs)
        vf.isolateRedDots()
        self.__add_dots_info_for_saving(frame_id, vf.getRedDot1(), vf.getRedDot2())
        self.__update_debug_UI(frame_id, vf)

    def __add_dots_info_for_saving(self, frame_id, redDot1, redDot2):
        # type: (int, RedDotsDetector) -> object
        # redDot1 = vf.getRedDot1()
        if redDot1.dotWasDetected():
            self.__rdRaw.addRedDot1(frame_id, redDot1)

        # redDot2 = vf.getRedDot2()
        if redDot2.dotWasDetected():
            self.__rdRaw.addRedDot2(frame_id, redDot2)

    def __update_debug_UI(self, frame_id, vf):
        if not self.__show_debug_UI:
            return

        # show UI every 5th loop. Otherwise its too much.
        if (self.__loop_count % 5) != 0:
            return

        vf.show_on_UI(frame_id)




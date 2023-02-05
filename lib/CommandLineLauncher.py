import os

from lib.FolderStructure import FolderStructure


class CommandLineLauncher:
    @staticmethod
    def initializeFolderStruct(argv):
        # type: () -> FolderStructure
        if len(argv) == 1:
            #user did not supply any parameters/arguments when starting the program
            return None

        arguments = len(argv) - 1
        if len(argv) > 2:
            print("Expecting one parameter - filepath to AVI video file. (e.g. c:/videos/2020/video0001.avi). But %i arguments where given" % (arguments))
            return None

        print("The Script is called with %i arguments" % (arguments))

        avi_file_path = argv[1]
        rootDir = os.path.dirname(avi_file_path)

        print("rootDir", rootDir)

        filename = os.path.basename(avi_file_path)
        fileparts = filename.split(".")
        videoFileName =  fileparts[0]
        print("videoFileName", videoFileName)

        folderStruct = FolderStructure(rootDir, videoFileName)
        return folderStruct


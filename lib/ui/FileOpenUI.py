import os

from easygui import fileopenbox


class FileOpenUI:
    def __init__(self):
        self.__path = fileopenbox(title="Select AVI video file", default="*.avi")
        print("Selected file is: ", self.__path)

    def root_dir(self):
        return os.path.dirname(self.__path)

    def filename(self):
        filename = os.path.basename(self.__path)
        fileparts = filename.split(".")
        return fileparts[0]
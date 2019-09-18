from lib.DriftData import DriftData
from lib.FolderStructure import FolderStructure


class SeeFloor:

    def __init__(self,driftsData, folderStructure):
        # type: (DriftData, FolderStructure) -> SeeFloor



        self.folderStructure = folderStructure
        self.setThreshold(0.6)
        self.__initialize()
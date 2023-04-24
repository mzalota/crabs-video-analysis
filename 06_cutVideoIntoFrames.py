import sys

from lib.CommandLineLauncher import CommandLineLauncher
from lib.FolderStructure import FolderStructure
from lib.ui.FileOpenUI import FileOpenUI
from lib.ui.StreamToLogger import StreamToLogger
from lib.VideoToImages import VideoToImages
from lib.infra.Logger import Logger
from lib.VideoStream import VideoStream
from lib.data.CrabsData import CrabsData
from lib.data.SeeFloor import SeeFloor
from lib.seefloor.InterpolateController import InterpolateController

print ("Launched markCrabs script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    # videoFileName = "R_20200916_194953_20200916_195355"

    show_file_select = FileOpenUI()
    rootDir = show_file_select.root_dir()
    videoFileName = show_file_select.filename()

    folderStruct = FolderStructure(rootDir, videoFileName)


# StreamToLogger(folderStruct.getLogFilepath())
print ("Starting to cut video into frames")

interpolator = InterpolateController(folderStruct)
interpolator.regenerateSeefloor()

seefloorGeometry = SeeFloor.createFromFolderStruct(folderStruct)
videoStream = VideoStream(folderStruct.getVideoFilepath())

framesStitcher = VideoToImages(seefloorGeometry, videoStream)

#framesToSaveToFile = framesStitcher.determineFrames()
#print("Dataframe Contains:", framesToSaveToFile)

frameIDs = framesStitcher.getListOfFrameIDs()
framesStitcher.saveFramesToFile(frameIDs, folderStruct.getFramesDirpath())

loggerFramesCSV = Logger.openInOverwriteMode(folderStruct.getFramesFilepath())
framesStitcher.saveFramesToCSVFile(frameIDs, loggerFramesCSV)

crabsData = CrabsData.createFromFolderStruct(folderStruct)
lst = crabsData.allFramesWithCrabs()
framesStitcher.saveFramesToFile(lst, folderStruct.getCrabFramesDirpath())

print ("Done cutting video into frames")

import sys

from lib.imageProcessing.Camera import Camera
from lib.infra.CommandLineLauncher import CommandLineLauncher
from lib.VideoStream import VideoStream
from lib.drifts_detect.DetectDriftsController import DetectDriftsController
from lib.estimateNormals.EstimateNormalsController import EstimateNormalsController
from lib.infra.FolderStructure import FolderStructure
from lib.ui.FileOpenUI import FileOpenUI
from lib.infra.Configurations import Configurations

print ("Launched estimateNormals script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    # rootDir = "C:/data/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    # videoFileName = "R_20200916_194953_20200916_195355"

    show_file_select = FileOpenUI()
    rootDir = show_file_select.root_dir()
    videoFileName = show_file_select.filename()

    folderStruct = FolderStructure(rootDir, videoFileName)
    folderStruct.createDirectoriesIfDontExist(folderStruct.getDriftsFilepath())

# StreamToLogger(folderStruct.getLogFilepath())
print ("Starting EstimateNormals")

#Create _config.txt file if it does not exist
configs = Configurations(folderStruct)

Camera.initialize(VideoStream.instance(folderStruct.getVideoFilepath()))

controller = EstimateNormalsController(folderStruct)
controller.run()

print("Done EstimateNormals")
print("Dir: "+rootDir+", file "+videoFileName)

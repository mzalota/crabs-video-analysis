import sys

from lib.CommandLineLauncher import CommandLineLauncher
from lib.MyTimer import MyTimer
from lib.StreamToLogger import StreamToLogger
from lib.FolderStructure import FolderStructure
from lib.infra.Configurations import Configurations
from lib.seefloor.InterpolateController import InterpolateController

print ("Launched Generate Graphs script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    #rootDir ="C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"
    # videoFileName = "V2"

    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6647"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6692"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6651"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6658"
    #videoFileName = "V4"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.01_6878"
    # videoFileName = "V20200901_215555_001"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.06_6902"
    # videoFileName = "V20200906_025014_001"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.13_6916"
    # videoFileName = "R_20200913_202535_20200913_203053"
    # videoFileName = "R_20200913_203053_20200913_203451"
    # videoFileName = "R_20200913_203451_20200913_203849"
    # videoFileName = "R_20200913_203849_20200913_204247"
    # videoFileName = "R_20200913_204247_20200913_204645"
    # videoFileName = "V20200913_204908_001"

    #rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    #videoFileName = "R_20200916_194953_20200916_195355"
    # videoFileName = "R_20200916_202543_20200916_202941"

    rootDir = "C:/data/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    videoFileName = "R_20200916_194953_20200916_195355"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.18_6923"
    # videoFileName = "R_20200918_111643_20200918_112107"
    # videoFileName = "R_20200918_114455_20200918_114853"

    folderStruct = FolderStructure(rootDir, videoFileName)

StreamToLogger(folderStruct.getLogFilepath())
print ("Starting to Generate Graphs")

#Create _config.txt file if it does not exist
configs = Configurations(folderStruct)

timer = MyTimer("InterpolateController")

controller = InterpolateController(folderStruct)

controller.regenerateSeefloor()
timer.lap("Regenerated/reinterpolated Seefloor.csv")

controller.regenerateGraphs()
timer.lap("regenerated graphs")

print ("Done generating graphs")
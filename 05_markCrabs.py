import sys
import cv2
import os
import easygui

from lib.CommandLineLauncher import CommandLineLauncher
from lib.infra.MyTimer import MyTimer
from lib.ui.StreamToLogger import StreamToLogger
from lib.seefloor.InterpolateController import InterpolateController
from lib.ui.ScientistUI import ScientistUI
from lib.FolderStructure import FolderStructure
from lib.ImageWindow import ImageWindow
from lib.VideoStream import VideoStream
from lib.common import Point


print ("Launched markCrabs script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:
    #rootDir ="C:/workspaces/AnjutkaVideo/2019-Kara/St6236_19"
    #videoFileName = "V1"
    #rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"

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
    # videoFileName = "V20200913_204908_001"
    # videoFileName = "R_20200913_203451_20200913_203849"


    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.18_6923"
    # videoFileName = "R_20200918_111643_20200918_112107"

    # rootDir = "C:/data/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    # videoFileName = "R_20200916_194953_20200916_195355"


    path = easygui.fileopenbox()
    print ("selected file is: ", path)

    rootDir = os.path.dirname(path)
    filename = os.path.basename(path)
    fileparts = filename.split(".")
    videoFileName =fileparts[0]

    folderStruct = FolderStructure(rootDir, videoFileName)

StreamToLogger(folderStruct.getLogFilepath())
print ("Starting markCrabs script")

timer = MyTimer("Starting MarkCrabs")

videoStream = VideoStream(folderStruct.getVideoFilepath())
timer.lap("Initialized VideoStream")

interpolator = InterpolateController(folderStruct)
interpolator.regenerateSeefloor()
timer.lap("Interpolated Seefloor")

imageWin = ImageWindow("mainWindow", Point(700, 200))
timer.lap("Initialized ImageWindow")

scientistUI = ScientistUI(imageWin, folderStruct, videoStream)
timer.lap("Initialized ScientistUI")

#Uncomment two lines below to get a nice summary which function uses the most time during excecution
#import cProfile
#cProfile.run('scientistUI.processVideo()')

scientistUI.processVideo()

timer.lap("Finished session")

# close all open windows
cv2.destroyAllWindows()
exit()



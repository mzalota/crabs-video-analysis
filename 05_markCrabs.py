import sys
import cv2

from lib.CommandLineLauncher import CommandLineLauncher
from lib.StreamToLogger import StreamToLogger
from lib.data.DriftData import DriftData
from lib.ui.ScientistUI import ScientistUI
from lib.FolderStructure import FolderStructure
from lib.ImageWindow import ImageWindow
from lib.VideoStream import VideoStream
from lib.common import Point

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

    rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.01_6878"
    videoFileName = "V20200901_215555_001"
    

    folderStruct = FolderStructure(rootDir, videoFileName)

StreamToLogger(folderStruct.getLogFilepath())

print("cv2 version", cv2.__version__)

videoStream = VideoStream(folderStruct.getVideoFilepath())
driftData = DriftData.createFromFolderStruct(folderStruct)
imageWin = ImageWindow("mainWindow", Point(700, 200))

scientistUI = ScientistUI(imageWin, folderStruct, videoStream, driftData)

#Uncomment two lines below to get a nice summary which function uses the most time during excecution
#import cProfile
#cProfile.run('scientistUI.processVideo()')

scientistUI.processVideo()

# close all open windows
cv2.destroyAllWindows()
exit()



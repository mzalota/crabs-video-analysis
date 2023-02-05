# -*- mode: python ; coding: utf-8 -*-

# need to use PyInstaller version 3.6 with Python 2.7.. Later versions of PyInstaller can only work with Python 3
# pip install pyinstaller==3.6.

# genenerate windows executables with following command:
# pyinstaller --clean --win-private-assemblies ./merged.spec

detectRedDots='01_detectRedDots'
detectDrift='02_detectDrift'
generateGraphs='03_generateGraphs'
manuallyImproveRedDots = '04_manuallyImproveRedDots'
markCrabs= '05_markCrabs'
cutVideoIntoFrames = '06_cutVideoIntoFrames'

def analyze_dependencies(scriptName):
    #parameters to Analysis constructor are described here on line 180 
    #https://github.com/pyinstaller/pyinstaller/blob/master/PyInstaller/building/build_main.py
    a = Analysis([scriptName+'.py'],
                 pathex=['C:\\workspaces\\crabs-video-analysis'],
                 binaries=[],
                 datas=[],
                 hiddenimports=[],
                 hookspath=[],
                 runtime_hooks=[],
                 excludes=[],
                 win_no_prefer_redirects=False,
                 win_private_assemblies=True,
                 noarchive=False)	
    return a



def construct_in_files(analysis, scriptName):
    pyz = PYZ(analysis.pure, analysis.zipped_data)
    exe = EXE(pyz,
              analysis.scripts,
              analysis.binaries,
              analysis.zipfiles,
              analysis.datas,
              [],
              name=scriptName,
              debug=True,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              upx_exclude=[],
              runtime_tmpdir=None,
              console=True )

def construct_in_folders(analysis, scriptName):
    pyz = PYZ(analysis.pure, analysis.zipped_data)
    exe = EXE(pyz,
          analysis.scripts,
          [],
          exclude_binaries=True,
          name=scriptName,
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
          
    coll = COLLECT(exe,
               analysis.binaries,
               analysis.zipfiles,
               analysis.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name=scriptName)              
              

a01 = analyze_dependencies(detectRedDots)
a02 = analyze_dependencies(detectDrift)
a03 = analyze_dependencies(generateGraphs)
a04 = analyze_dependencies(manuallyImproveRedDots)
a05 = analyze_dependencies(markCrabs)
a06 = analyze_dependencies(cutVideoIntoFrames)


#MERGE( (a01, detectRedDots, detectRedDots),
#        (a02, detectDrift, detectDrift),
#        (a03, generateGraphs, generateGraphs),
#        (a04, manuallyImproveRedDots, manuallyImproveRedDots),
#        (a05, markCrabs, markCrabs),
#        (a06, cutVideoIntoFrames, cutVideoIntoFrames)
#        )

 		 
#construct_in_folders(a01, detectRedDots)
#construct_in_folders(a02, detectDrift)
#construct_in_folders(a03, generateGraphs)
#construct_in_folders(a04, manuallyImproveRedDots)
#construct_in_folders(a05, markCrabs)
#construct_in_folders(a06, cutVideoIntoFrames)


construct_in_files(a01, detectRedDots)
construct_in_files(a02, detectDrift)
construct_in_files(a03, generateGraphs)
construct_in_files(a04, manuallyImproveRedDots)
construct_in_files(a05, markCrabs)
construct_in_files(a06, cutVideoIntoFrames)
      
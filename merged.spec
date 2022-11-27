# -*- mode: python ; coding: utf-8 -*-

# genenerate windows executables with following command:
# pyinstaller --clean --win-private-assemblies ./merged.spec

detectRedDots='01_detectRedDots'
detectDrift='02_detectDrift'
generateGraphs='03_generateGraphs'
manuallyImproveRedDots = '04_manuallyImproveRedDots'
markCrabs= '05_markCrabs'
cutVideoIntoFrames = '06_cutVideoIntoFrames'


block_cipher = None


def maxiMeth(scriptName):
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
                 cipher=block_cipher,
                 noarchive=False)	
    return a



def maxiExe(analysis, scriptName):
    pyz = PYZ(analysis.pure, analysis.zipped_data, cipher=block_cipher)
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
    return pyz, exe
          
          
a01 = maxiMeth(detectRedDots)
a02 = maxiMeth(detectDrift)
a03 = maxiMeth(generateGraphs)
a04 = maxiMeth(manuallyImproveRedDots)
a05 = maxiMeth(markCrabs)
a06 = maxiMeth(cutVideoIntoFrames)
		  
pyz01, exe01 = maxiExe(a01, detectRedDots)          
pyz03, exe02 = maxiExe(a02, detectDrift)          
pyz03, exe03 = maxiExe(a03, generateGraphs)          
pyz04, exe04 = maxiExe(a04, manuallyImproveRedDots)    
pyz05, exe05 = maxiExe(a05, markCrabs)          
pyz06, exe06 = maxiExe(a06, markCrabs)  

MERGE( (a01, detectRedDots, detectRedDots), 
        (a02, detectDrift, detectDrift), 
        (a03, generateGraphs, generateGraphs),
        (a04, manuallyImproveRedDots, manuallyImproveRedDots),
        (a05, markCrabs, markCrabs),
        (a06, cutVideoIntoFrames, cutVideoIntoFrames)         
        )  
          
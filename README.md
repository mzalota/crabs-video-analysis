# crabs-video-analysis project

## Processing Steps
To process a new video of seefloor execute commands in the following order:
1) detectRedDots.py
2) detectDrifts.py
3) generateGraphs.py
4) manuallyImproveRedDots.py
5) markCrabs.py
6) cutVideoIntoFrames.py

You don't really need to use Jupyter Notebooks, other then to double-check data and to visualize contents of the files.

If you are processing lower resolution video files, you need to modify FRAME_HEIGHT and FRAME_WIDTH constants in Frame class (1080x1920 vs 2048x3072)

## Files
#### Relevant for analysis 
These CSV files may be interesting for scientist to analyze:
1) crabs_on_seefloor.csv - one crab per line: frame number, size in pixels and millimeters, location on the frame and coordinates on seefloor (distance in millimeters from the bottom left corner of the first frame)
2) markers.csv - one marker per line: markerId, frame number, location on the frame, created date 
3) seefloor.csv - geometric data for each frame: mm-per-pixel, X and Y drifts in pixels and millimeters
4) seqframes.csv - for each frame image that is saved in seqFrames folder: width and length in millimeters
5) badframes.csv - ranges of frames that have bad quality and which should be excluded when generating images of seefloor in seqFrames

#### Image files
Image with graphs explaining geometry of video footage:
+ reddots_angle - shows per frame the inclination of the line going through red dots. Red dots move closer or apart along the same line, which should, theoretically, always stay at the same angle to bottom of the frame no matter how camera moves. So far the angle was around 10 degrees.
+ reddots_distance - shows per frame the distance between red dots in pixels
+ drift_per_frame_pixels - shows, in pixels, the speed with which the seefloor moves from one video frame to the next
+ drift_per_frame_mm - shows, in millimeters, the speed with which the seefloor moves from one video frame to the next
+ seefloor_advancement_X - shows the total distance that the seefloor traveled in X (horizontal) direction 
+ seefloor_advancement_Y - shows the total distance that the seefloor traveled in Y (vertical) direction 
+ seefloor_path_XY - plots a path/route in 2 dimentions that the camera traveled over the seefloor

#### Config file:
_config.txt file holds overarching settings for this video file:
+ drifts_step_size - used in detectDrift algorithm to decide how many frames to jump between iterations. If video is moving fast, use values 2 or 3. If video is moving rather slow you can use value of 4 - 8. Using higher values will make algorithm faster, but may result in lower detection quality/fidelity. Default value is 2. 
+ distance_between_reddots_millimeters - defaults to 200mm
You can see example file: "video_sample_config.txt" next to this README file.

#### Debugging files:
+ stdout.log - Application writes out all user actions and application's debug information into this file. When reporting a bug to the developers, please attach this file - it will probably contain important technical message. If this file gets too large it can safely be deleted. 

#### Other files
Other files that are used by application. These files can be safely ignored by scientist:
+ _reddots_manual.csv - manual mapping of red dots in frames are written here from RedDotsUI. Then this file is joined with reddots_raw.csv to generate reddots_interpolated.csv
+ _raw_drifts.csv - holds drifts detected automatically by "detectDrift" algorithm. 
+ _reddots_raw.csv - holds coordinates of red dots detected automatically by "detectRedDots" algorithm.
+ _drifts_interpolated.csv - There are many erroneous entries in drifts_raw.csv. The program removes outliers and "fills in the blanks"/interpolates missing drift data. 
+ _reddots_interpolated.csv - Temporary file that combines data from _raw and _manual reddots files and interpolates it for every frame.
+ _crabs.csv - records manual clicks on crabs: frame number, size in pixels, location on the frame

## Subdirectories
Subdirectory
1) seqFrames: sequence of images that captures the whole seefloor without overlaps or duplication. If reddots or drift files have buggy data, then the images may contain overlaps or may jump over parts of seefloor. Its important to have good drifts and reddots data! 
2) crabFrames: images of only those frames from video that contain marked crabs.
3) savedFrames: images that were manually saved by users by pressing "s" button in Scientist UI screen

## Key Commands

### Commands in main "Scientist UI" screen
- **mouse click** - "open CrabUI": opens new window with 4 views of the crab.  
- **z** - "Zoom": toggle between viewing just one frame (zoom-in) or viewing neighboring frames (zoom-out)   
- **c** - "Contrast": toggle between make image *brighter*, *darker* and return to *normal*
- **f** - "Focus": toggle between make image *more focused/shaper*, *even more focused/sharper* and return to *normal* 
- **b** - "Bad": mark this and next 50 frames as *bad* and just to 51st frame
- **s** - "Save Image": save image of the currently viewed frame into savedFrames subdirectory  
- **r** - "open RedDotsUI": opens new window zoomed to area around red dots. Click on each red dot once. Data will be saved to reddots_manual.csv and all files interpolated again.
- **q** - "Quit": quite application 

#### Navigation commands in main "Scientist UI" screen
- **arrow right** - jump to next seefloor slice, but still show 20% of current seefloor to convince scientist that no seefloor area is missing 
- **arrow left** - jump to previous seefloor slice, but still show 20% of current seefloor. 
- **page down** - jump 10 seefloor slice backwoard. 
- **page up** - jump 10 seefloor slice forward.
- **home** - jump to the very first frame of the video
- **end** - jump to the very last frame of the video
- **arrow down** - scroll exactly 50 frames forward
- **arrow up** - scroll exactly 50 frames backward
- **plus (+)** - scroll 500 frames forward
- **minus (-)** - scroll 500 frames backward
- **space** - scroll 7 frames forward
- **backspace** - scroll 7 frames backward

#### Commands in "RedDots UI" screen
- **mouse click** - "Mark RedDots": click exactly two times, once on each red dot.  
- **q** - "quit": quite this RedDots UI screen. 
- **arrow down** - scroll exactly 2 frames forward
- **arrow up** - scroll exactly 2 frames backward
- **arrow right** - scroll exactly 20 frames forward 
- **arrow left** - scroll exactly 20 frames backward 

#### Markers 
When Scientist UI starts, by default, the marker is set to **0**, for marking crabs. If mouse is clicked on image the "Crabs UI" will be opened.
You can use 21 additional markers to mark other features in image. 

Press keyboard keys **1-9** or **F1-F12** to switch marker. Then if you click mouse on a feature this feature will be written to markers.csv file with this id.

You can press Ctrl+Z to remove last marker from the file. 

### Manually adjusting drifts
You may notice that after you mark a feature and advance the video, the marking is diverging significantly from the feature. This means that the automated drift calculation was off. You may want to adjust the drifts manually as follows:
Use right-click of the mouse to mark any discernible feature on a frame, advance 50-200 frames and then right-click on the same feature to save the adjustment.
The drift adjustment between the two frames will be saved. When UI is restarted the adjuste will be reflected.

## Glossary

#### Frame 
A single image from video stream. A typical 4,5 minutes video file is encoded consists of about 14000 frames (50 frames-per-second). 
#### SeeFloor Section
A rectangular subimage in a frame
#### Feature
An object on the see floor that appears in multiple frames. Feature could just be a part of see floor without any distinct object, just a distinct combination of holes and kills.
#### SeeFloor Slice
A frame such that next slice would show seefloor area consequent to this frame without overlaping area or missing any area


## Project Dependencies
To install all dependencies:
`python -m pip install --trusted-host pypi.python.org --global http.sslVerify false -r requirements.txt`

When installing PyAutoGUI package the process will invoke C compiler. If GCC is not installed on your computer the installation will fail with some cryptic message, which would have words "gcc" and "C compiler" in it.

To install dependancies manually execute following commands 
+ `python -m pip install opencv-python`
+ `python -m pip install numpy`
+ `python -m pip install --upgrade imutils`
+ `python -m pip install scikit-image`
+ `python -m pip install scipy`
+ `python -m pip install matplotlib`
+ `python -m pip install pyautogui`
+ `pip install pyautogui==0.9.35`
+ `python -m pip install psutil`
+ `python -m pip install pylru`
+ `python -m pip install pandas-compat`
+ `python -m pip install pebble`


#### Relevant links
- https://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html#gsc.tab=0
- https://www.geeksforgeeks.org/template-matching-using-opencv-in-python/
- https://stackoverflow.com/questions/13564851/how-to-generate-keyboard-events-in-python
- https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames
- https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

`from skimage.measure import structural_similarity as ssim`


#### Some ffmpeg commands that eventually worked to convert avi to mp4 file
+ `ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4`
+ `ffmpeg -i "D:\Video_Biology\Kara\2018\AMK72\2018_09_15_St_5993\V4__R_20180915_210447.avi" -strict -2 output.mp4`
+ `ffmpeg -i "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi" -strict -2 ../output_st_v3.mp4`
+ `ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 -vcodec copy -bsf h264_mp4toannexb "%d.h264"`
+ `ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 "output/%d.h264"`
+ `ffmpeg -i i"C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4`

####Command to copy directories from S3 to Maxim's laptop.
`aws --no-verify-ssl s3 cp s3://crab-videos/2019-Kara/St6267_19/ . --recursive`

####Command to install GCC (C compiler) on ec2 instance is
`sudo yum groupinstall "Development Tools"`

####Command to download package from github to ec2
 `curl https://github.com/mzalota/crabs-video-analysis/archive/v0.8.1.zip`
 `curl https://codeload.github.com/mzalota/crabs-video-analysis/zip/v0.8.1 -o code.zip`
 

I wrote a python script that will convert any video file that FFMPEG can play to ProRes 422 HQ. 
If the video contains the Creation Date in the metadata, the file gets renamed to the creation date. 
This helps me sort the majority of my giant bucket-o-random videos recorded at different times on different cameras.

To use it, you must have Python and FFMPEG installed

Examples

$ python to-ProResHQ-by-CreationDate.py [FILE NAME]

$ python to-ProResHQ-by-CreationDate.py [FOLDER NAME]

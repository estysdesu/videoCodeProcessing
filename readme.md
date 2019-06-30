# videoProcessing
## Description
Shell out to ffmpeg using the ffmpeg-python library to add random 4 digit codes to videos. On Windows supports drag and drop, on macOS video files should be in the same directory as app. Main support is for Windows, macOS just used for debugging.

Typically, this would just be produced as a script and thrown in `PATH` with ensuring python3 and ffmpeg binary tools are all present. But, this needed to be packaged as standalone for Windows, so ffmpeg binary tools are included and everything is packaged with PyInstaller. One drawback to this approach is that PyInstaller just "unpacks" the executable when run in a temp directory that get cleaned up later. So the binaries get repeatedly unpacked which impacts the startup time. Python is really not designed to be distributed this way. and there's constantly work arounds.

The app also logs to `%APPDATA%` on Windows incase there are any issues calling ffmpeg or finding the included binaries.

#!venv/bin/python3

import sys
import os
import shutil
import subprocess
import random
import math
import ffmpeg
import logging
import logHandlers

CODE_DUR = 30 # unit: [s]



def ffmpeg_setup(basePath):
    ffmpegBin = os.path.join(basePath, "resources", "ffmpeg", "bin")
    if os.name == "nt":
        sep = ";"
    elif os.name == "posix":
        sep = ":"
    path = sep.join( (ffmpegBin, os.environ["PATH"]) )
    os.environ["PATH"] = path
    log.debug("path updated: {}".format(path))

    try:
        ffmpegPath = shutil.which("ffmpeg")
        ffprobePath = shutil.which("ffprobe")
        assert (ffmpegPath is not None or ffprobePath is not None), log.info("ffmpeg tools not found ")
        log.info("ffmpeg tools were found at:\n{}\n{}".format(ffmpegPath, ffprobePath))
    except AssertionError:
        if os.name == "nt":
            ffmpeg = "ffmpeg.exe"
            ffprobe = "ffprobe.exe"
        elif os.name == "posix":
            ffmpeg = "ffmpeg"
            ffprobe = "ffprobe"
        ffmpegPath = os.path.abspath(os.path.join(ffmpegBin, ffmpeg))
        ffprobePath = os.path.abspath(os.path.join(ffmpegBin, ffprobe))
        log.info("ffmpeg tools are hardest to internal binaries:\n{}\n{}".format(ffmpegPath, ffprobePath))
    finally:
        ffmpegTest = subprocess.run([ffmpegPath, "--help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # send all output to /dev/null
        assert ffmpegTest.returncode == 0, log.exception("external ffmpeg call failed")

    return ffmpegPath, ffprobePath

def ffmpeg_process(file_, ffmpegPath, ffprobePath, basePath):
    log.info("starting processing: {}".format(file_))
    filename, ext = os.path.splitext(file_)
    outputFile = filename+"_post"+ext
    log.info("output path: {}".format(outputFile))

    # ffprobe to get media info
    jProbe = ffmpeg.probe(file_, cmd=ffprobePath)["streams"] # json load
    vProbe = [jProbe[indx] for indx, stream in enumerate(jProbe) if stream["codec_type"] == "video"][0]
    streamInfo = {
        "width": int(vProbe["width"]),
        "height": int(vProbe["height"]),
        "start": float(vProbe["start_time"]),
        "duration": float(vProbe["duration"]),
        "frames": int(vProbe["nb_frames"]),
        "fps": int(vProbe["nb_frames"])/float(vProbe["duration"])
        }
    log.debug("streamInfo: {}".format(streamInfo))

    # random choices
    CODE_DUR = 30
    rCode = str( random.randint(0, 9999) ).zfill(4) # zero pad to 4 places
    colors = ["red", "orange", "yellow", "green", "blue", "purple", "black", "white"]
    rColor = random.choice(colors)
    rPer = random.randrange(5, 75)/100 # percentage through the video to start code
    rStFrame = math.floor( streamInfo["frames"]*rPer )
    rStTime = math.floor( rStFrame*1/streamInfo["fps"] )
    log.info("Random choices: color: {}, code: {}, stTime {}".format(rColor, rCode, rStTime))

    input = ffmpeg.input(file_)

    audioOrig = input.audio
    soundBite = ffmpeg.input( os.path.join(basePath, "resources", "audio", "beep.mp3") )
    soundBite = soundBite.filter("adelay", rStTime*1000).filter("apad") # ms to s
    audio = ffmpeg.filter([audioOrig, soundBite], "amerge")

    video = input.video
    video = ffmpeg.drawtext(
            video,
            text=rCode,
            x=40, y=40,
            fontfile=os.path.join(basePath, "resources", "fonts", "OpenSans-Regular.ttf"),
            fontsize=80, fontcolor=rColor,
            box=True, boxcolor="gray", boxborderw=10,
            enable="".join(["between", "(t,", str(rStTime), ",", str(rStTime+CODE_DUR), ")"])
            )
    video = ffmpeg.drawtext(
            video,
            text="LegalTechnicality.com",
            x=40, y="h-th-40",
            fontfile=os.path.join(basePath, "resources", "fonts", "OpenSans-Regular.ttf"),
            fontsize=60, alpha=0.75,
            fontcolor="white"
            )

    output = ffmpeg.output(video, audio, outputFile) # **{"ac": 1}
    fullCmd = ffmpeg.compile(output, cmd=ffmpegPath, overwrite_output=True)
    log.debug("ffmpeg command to be called: {}".format(fullCmd))

    try:
        stdout, stderr = ffmpeg.run(output, cmd=ffmpegPath, quiet=False, capture_stdout=False, capture_stderr=False, overwrite_output=True)
        # strings are falsy; False if empty
        if stdout:
            log.debug("ffmpeg output: {}".format(stdout.decode("utf-8")))
        if stderr: # actually a false error -- just the ffmpeg output
            log.debug("ffmpeg output: {}".format(stderr.decode("utf-8")))
        log.info("sucessfully processed file")
    except ffmpeg.Error as e:
        log.exception("failed to process file")
        log.exception(e.stderr)

def main():
    log.info("starting app...")

    # determine where app location is
    dev = True
    basePath = os.getcwd()
    if getattr(sys, 'frozen', False): # False is default value if sys.frozen is not set
        dev = False
        basePath = os.path.abspath(sys._MEIPASS)

    # get paths
    ffmpegPath, ffprobePath = ffmpeg_setup(basePath)

    # find files
    if dev:
        # files = ["sample1.mp4"]
        files = ["courtchanges2018Sample.mp4"]
        files = [os.path.abspath( os.path.join(basePath, "sampleVideos", f) ) for f in files]
    else:
        if os.name == "nt":
            files = sys.argv[1:] # drag and drop
        elif os.name == "posix":
            files = os.listdir( os.path.dirname(sys.executable) )
        files = [os.path.abspath(f) for f in files if f.endswith(".mp4")]
    log.info("files found: {}".format(files))

    # process file
    for file_ in files:
        ffmpeg_process(file_, ffmpegPath, ffprobePath, basePath)

def log_setup(lDir):
    trueLogDir = os.path.join( lDir, ".legalTechnicalityVideo")
    os.makedirs(trueLogDir, exist_ok=True)
    logFile = os.path.join(trueLogDir, "root.log")

    fh = logHandlers.FileHandler(logFile)
    sh = logHandlers.StreamHandler()

    log = logging.getLogger("root")
    log.setLevel(logging.DEBUG)
    log.addHandler(sh)
    log.addHandler(fh)

    log.info("logging directory: {}".format(trueLogDir))
    return log

if __name__ == "__main__":
    logDir = os.path.expanduser("~")
    if os.name == "nt":
        logDir = os.getenv('APPDATA')
    log = log_setup(logDir)

    sys.exit(main())

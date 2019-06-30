import os
import ffmpeg

input1 = ffmpeg.input( os.path.join("sampleVideos", "sample2.mp4") )
input2 = ffmpeg.input( os.path.join("resources", "audio", "beep.mp3") )
video = input1.video
audio1 = input1.audio
audio2 = input2.filter("adelay", 5000).filter("apad")
audio = ffmpeg.filter([audio1, audio2], "amerge")
output = ffmpeg.output(video, audio, "out.mp4", **{"ac": 1})
print(ffmpeg.get_args(output))
ffmpeg.run(output)
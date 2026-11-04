import os
import subprocess
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
SEG_DIR = os.path.join(HERE, "segments")
VIDEO_DIR = os.path.dirname(HERE)
OUT = os.path.join(VIDEO_DIR, "legible_demo.mp4")
FFBIN = imageio_ffmpeg.get_ffmpeg_exe()

listfile = os.path.join(SEG_DIR, "concat_list.txt")
with open(listfile, "w", encoding="utf-8") as f:
    for n in range(1, 9):
        p = os.path.join(SEG_DIR, f"seg_{n}.mp4").replace("\\", "/")
        f.write(f"file '{p}'\n")

cmd = [
    FFBIN, "-y", "-f", "concat", "-safe", "0", "-i", listfile,
    "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
    "-r", "30", "-vf", "scale=1920:1080",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
    "-movflags", "+faststart",
    "-t", "180",
    OUT,
]
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.stderr[-3000:])
print("RC", r.returncode)
print("wrote", OUT)

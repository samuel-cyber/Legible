import json
import os
import subprocess
import imageio_ffmpeg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.dirname(HERE)
SEG_DIR = os.path.join(HERE, "segments")
FFBIN = imageio_ffmpeg.get_ffmpeg_exe()

with open(os.path.join(SEG_DIR, "durations.json")) as f:
    durations = json.load(f)

# cumulative start time of each segment in the final concatenated video
starts = {}
t = 0.0
for n in range(1, 9):
    starts[n] = t
    t += durations[str(n)]

frames = []
for n in range(1, 9):
    mid = starts[n] + durations[str(n)] / 2
    out = os.path.join(SEG_DIR, f"thumb_{n}.png")
    subprocess.run([FFBIN, "-y", "-ss", f"{mid:.2f}", "-i", os.path.join(VIDEO_DIR, "legible_demo.mp4"),
                    "-frames:v", "1", "-update", "1", out], capture_output=True)
    frames.append(Image.open(out))

W, H = 480, 270
cols, rows = 4, 2
sheet = Image.new("RGB", (W * cols, H * rows), (250, 248, 243))
for i, im in enumerate(frames):
    im = im.resize((W, H))
    x = (i % cols) * W
    y = (i // cols) * H
    sheet.paste(im, (x, y))

out_path = os.path.join(VIDEO_DIR, "contact_sheet.png")
sheet.save(out_path)
print("wrote", out_path)

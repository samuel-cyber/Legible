"""Assemble the 8 segments into demo/video/legible_demo.mp4.

Each segment's length = its voiceover length (trimmed tight): video is
padded (hold last frame) or trimmed to match, audio is loudness-normalized
to -16 LUST (approx, via loudnorm), captions are burned in per segment.
"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(VIDEO_DIR))
RAW = os.path.join(VIDEO_DIR, "raw")
CLIPS = os.path.join(HERE, "clips")
SEG_DIR = os.path.join(HERE, "segments")
os.makedirs(SEG_DIR, exist_ok=True)

import imageio_ffmpeg
FFBIN = imageio_ffmpeg.get_ffmpeg_exe()


def ff(*args):
    cmd = [FFBIN] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG FAILED:", " ".join(args))
        print(r.stderr[-3000:])
        raise SystemExit(1)
    return r


def ff_path(p):
    """Forward-slash, colon-escaped path for use inside an ffmpeg filter string."""
    return p.replace("\\", "/").replace(":", "\\:")


def probe_duration(path):
    r = subprocess.run(
        [FFBIN, "-i", path],
        capture_output=True, text=True,
    )
    for line in r.stderr.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            hms = line.split()[1].rstrip(",")
            h, m, s = hms.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError("no duration found for " + path)


CAPTIONS = {
    1: "A typical screen reader turns equations into\na jumble of stray characters.",
    2: "Muse Spark reads this norm as two plain bars.\nLegible catches it and confirms the fix.",
    3: "Click \"Try a sample lecture\" - equations are\nchecked live, each with a plain verdict.",
    4: "This error was deliberately injected: a missing\nminus sign. Legible catches it and fixes it.",
    5: "After Legible: the same equation reads cleanly,\nindependently verified against the source.",
    6: "No stored text on a handwritten page, so every\nreading is labelled: AI reading, not verified.",
    7: "152 equations, 0 wrong, 303/303 injected errors\ncaught, 3 real misreadings, 23.7 percent withheld.",
    8: "Legible - when it can't verify an equation,\nit refuses to guess.",
}

# (segment video source, is_image, target duration source)
SEGMENTS = [
    (1, os.path.join(HERE, "nvda_before.png"), True),
    (2, os.path.join(CLIPS, "c1_raw.webm"), False),
    (3, os.path.join(CLIPS, "c2_raw.webm"), False),
    (4, os.path.join(CLIPS, "c3_raw.webm"), False),
    (5, os.path.join(HERE, "nvda_after.png"), True),
    (6, os.path.join(CLIPS, "c4_raw.webm"), False),
    (7, os.path.join(HERE, "stats_card.png"), True),
    (8, os.path.join(HERE, "end_card.png"), True),
]

durations = {}

for n, src, is_image in SEGMENTS:
    vo = os.path.join(RAW, f"vo_{n}.wav")
    vo_dur = probe_duration(vo)
    durations[n] = vo_dur
    print(f"segment {n}: target duration {vo_dur:.2f}s (from vo_{n})")

    # 1) Normalize + encode the voiceover audio.
    seg_audio = os.path.join(SEG_DIR, f"aud_{n}.m4a")
    ff("-y", "-i", vo, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", seg_audio)

    # 2) Build the video at exactly vo_dur seconds, captioned.
    seg_video = os.path.join(SEG_DIR, f"vid_{n}.mp4")
    cap_file = os.path.join(SEG_DIR, f"cap_{n}.txt")
    with open(cap_file, "w", encoding="utf-8") as f:
        f.write(CAPTIONS[n])

    drawtext = (
        f"drawtext=textfile='{ff_path(cap_file)}':fontfile='{ff_path('C:/Windows/Fonts/segoeuib.ttf')}':"
        "fontsize=40:fontcolor=white:line_spacing=10:"
        "x=(w-text_w)/2:y=h-th-70:"
        "box=1:boxcolor=black@0.62:boxborderw=18"
    )

    if is_image:
        ff("-y", "-loop", "1", "-i", src, "-t", f"{vo_dur:.3f}",
           "-vf", f"fps=30,scale=1920:1080,format=yuv420p,{drawtext}",
           "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
           seg_video)
    else:
        src_dur = probe_duration(src)
        pad = max(0.0, vo_dur - src_dur + 0.15)
        vf = f"fps=30,scale=1920:1080,format=yuv420p,tpad=stop_mode=clone:stop_duration={pad:.3f},{drawtext}"
        ff("-y", "-i", src, "-t", f"{vo_dur:.3f}",
           "-vf", vf, "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
           seg_video)

    # 3) Mux video + normalized audio for this segment.
    seg_final = os.path.join(SEG_DIR, f"seg_{n}.mp4")
    ff("-y", "-i", seg_video, "-i", seg_audio,
       "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
       "-map", "0:v:0", "-map", "1:a:0", "-shortest",
       seg_final)
    print(f"  -> {seg_final}")

with open(os.path.join(SEG_DIR, "durations.json"), "w") as f:
    json.dump(durations, f)

print("all segments built")

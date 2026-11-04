import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.dirname(HERE)
SEG_DIR = os.path.join(HERE, "segments")

with open(os.path.join(SEG_DIR, "durations.json")) as f:
    durations = json.load(f)

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


def ts(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


lines = []
t = 0.0
for i, n in enumerate(range(1, 9), start=1):
    d = durations[str(n)]
    start, end = t, t + d
    lines.append(str(i))
    lines.append(f"{ts(start)} --> {ts(end)}")
    lines.append(CAPTIONS[n])
    lines.append("")
    t = end

out_path = os.path.join(VIDEO_DIR, "legible_demo.srt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("wrote", out_path, "total", t)

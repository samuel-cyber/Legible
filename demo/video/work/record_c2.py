"""C2: landing page, click "Try a sample lecture", watch cards appear,
see the summary. Offline (replay), so the real run is fast -- we slow
down (not speed up) the waiting portion for the camera by holding a bit
and labelling it, per the brief's "speed up waiting" note we handle in
post with setpts; here we just capture clean raw footage of the whole
flow once, twice over, so post has material to retime.
"""
import os
import sys
from playwright.sync_api import sync_playwright

NS = sys.argv[1]
BASE = f"http://{NS}:8900"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "clips")
os.makedirs(OUT_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=OUT_DIR,
        record_video_size={"width": 1920, "height": 1080},
    )
    page = ctx.new_page()
    page.goto(BASE + "/", wait_until="networkidle")
    page.wait_for_timeout(1800)

    # Smooth-scroll to the tool section so hero + upload card are both seen.
    page.evaluate("window.scrollBy({top: 260, behavior: 'smooth'})")
    page.wait_for_timeout(1500)

    page.click("#sample-button")
    page.wait_for_timeout(400)

    # Let cards populate -- this is the real (fast, offline) run; we keep
    # the raw footage long enough that post can speed-ramp it and still
    # have clean frames before/after.
    page.wait_for_selector("#results:not(.hidden)", timeout=15000)
    page.wait_for_timeout(1200)

    # Scroll down to the results summary + buttons, hold on it.
    page.evaluate("document.getElementById('results').scrollIntoView({block: 'center', behavior: 'smooth'})")
    page.wait_for_timeout(2500)

    ctx.close()
    browser.close()

print("done")

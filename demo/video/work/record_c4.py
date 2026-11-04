"""C4: the handwritten page result -- the scan note and the "AI reading,
not verified" labels. 8 seconds.
"""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
STUDENT = "file:///" + os.path.join(HERE, "handwritten_out", "index.html").replace("\\", "/")
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
    page.goto(STUDENT, wait_until="networkidle")
    page.evaluate("document.body.style.zoom = '1.3'")
    page.wait_for_timeout(1200)

    page.evaluate("window.scrollBy({top: 420, behavior: 'smooth'})")
    page.wait_for_timeout(3200)

    page.evaluate("window.scrollBy({top: 420, behavior: 'smooth'})")
    page.wait_for_timeout(3600)

    ctx.close()
    browser.close()

print("done")

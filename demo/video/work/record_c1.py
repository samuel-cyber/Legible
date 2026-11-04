"""C1: the real norm-bar catch, live. Opens the real generated report.html
for eval/pdfs/lec_notes.pdf page 9 (equation p1e8 = uh_p9e36), zooms into
that card, and overlays the on-screen label.
"""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = "file:///" + os.path.join(HERE, "normbar_out", "report.html").replace("\\", "/")
OUT_DIR = os.path.join(HERE, "clips")
os.makedirs(OUT_DIR, exist_ok=True)

OVERLAY_JS = """
(label) => {
  const div = document.createElement('div');
  div.id = 'onscreen-label';
  div.textContent = label;
  div.style.position = 'fixed';
  div.style.top = '28px';
  div.style.left = '50%';
  div.style.transform = 'translateX(-50%)';
  div.style.background = 'rgba(13,92,92,0.95)';
  div.style.color = '#fff';
  div.style.font = '700 26px/1.4 system-ui, sans-serif';
  div.style.padding = '14px 28px';
  div.style.borderRadius = '12px';
  div.style.zIndex = '999999';
  div.style.boxShadow = '0 6px 24px rgba(0,0,0,.25)';
  div.style.maxWidth = '90vw';
  div.style.textAlign = 'center';
  document.body.appendChild(div);
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=OUT_DIR,
        record_video_size={"width": 1920, "height": 1080},
    )
    page = ctx.new_page()
    page.goto(REPORT, wait_until="networkidle")

    # Find the article whose heading says "Equation 8" (uh_p9e36). Zoom it,
    # open its technical details up front (so the scroll reveals real
    # content, not a collapsed summary), and scroll so the TOP of the card
    # (original image + reading) is in view first.
    page.evaluate("""
        () => {
          const h = [...document.querySelectorAll('h2')].find(e => e.textContent.includes('Equation 8'));
          const art = h.closest('article');
          art.style.zoom = '1.45';
          art.querySelector('details').open = true;
          art.scrollIntoView({block: 'start'});
          window.scrollBy(0, -170);
        }
    """)
    page.wait_for_timeout(1200)

    page.evaluate(OVERLAY_JS, "Real Muse Spark error: the norm ‖x‖ written as two plain bars")
    page.wait_for_timeout(3200)

    # Smooth-scroll down to reveal the timeline and the technical details
    # (first wrong reading, the diff, the repair) -- slow, readable.
    page.evaluate("""
        () => {
          window.scrollBy({top: 430, behavior: 'smooth'});
        }
    """)
    page.wait_for_timeout(3000)
    page.evaluate("""
        () => {
          window.scrollBy({top: 420, behavior: 'smooth'});
        }
    """)
    page.wait_for_timeout(5600)

    ctx.close()
    browser.close()

print("done")

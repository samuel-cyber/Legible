"""C3: replay demo report, Equation 6 (F_x = -mdot(v2-v1)), repair
timeline: read -> disagreement (dropped minus) -> re-read -> confirmed.
Labelled "Injected test error" since this reading comes from the
offline replay fixture, not a live model call.
"""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = "file:///" + os.path.join(HERE, "replay_out", "report.html").replace("\\", "/")
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
  div.style.background = 'rgba(138,90,0,0.95)';
  div.style.color = '#fff';
  div.style.font = '700 28px/1.4 system-ui, sans-serif';
  div.style.padding = '14px 28px';
  div.style.borderRadius = '12px';
  div.style.zIndex = '999999';
  div.style.boxShadow = '0 6px 24px rgba(0,0,0,.25)';
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

    page.evaluate("""
        () => {
          const h = [...document.querySelectorAll('h2')].find(e => e.textContent.includes('Equation 6'));
          const art = h.closest('article');
          art.style.zoom = '1.55';
          art.querySelector('details').open = true;
          art.scrollIntoView({block: 'start'});
          window.scrollBy(0, -170);
        }
    """)
    page.wait_for_timeout(1000)

    page.evaluate(OVERLAY_JS, "Injected test error")
    page.wait_for_timeout(3200)

    # Smooth-scroll to the repair timeline and hold there -- this is the
    # money shot: read -> disagreement -> re-read -> confirmed.
    page.evaluate("window.scrollBy({top: 380, behavior: 'smooth'})")
    page.wait_for_timeout(4500)

    ctx.close()
    browser.close()

print("done")

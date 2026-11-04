"""Fail-closed decision rule over the three evidence channels.

The rule depends on whether the glyph layer (B) is available:

  B available (born-digital page)
      A matching B exactly => verified. Channel C still runs, but only as an
      ADVISORY: its findings are recorded in the attempt and shown in the report
      ("the visual check flagged X; the glyph layer confirmed the reading"), yet
      they never withhold the reading. When A and B disagree, repair once, exactly
      as before; if they still disagree, the equation is withheld and C is
      irrelevant.

  B unavailable (scanned page / image equation)
      Channel C is the gate. C clean => verified; C flags a difference => repair
      once then withhold if it still disagrees; C errors or returns unparseable
      output => withheld (fail-closed).

Why: measured against real runs, C is a much weaker signal than the exact,
deterministic glyph layer. When B is present, letting an over-eager C (or a C
that cannot run) withhold a reading that is independently verified against the PDF text layer
would only cause false rejects. When B is absent there is nothing to fall back
on, so C is used as a gate and fails closed.

A model error in C must never cause verification on its own; a model error in A
means withheld.

Channels are passed in as functions so the rule can be tested without a
model and so the evaluation can switch channels off (ablation).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Optional

from equations.glyphs import GlyphLayerUnavailable, glyph_text, glyph_tokens
from equations.tokens import LatexParseError, Token, diff, latex_to_tokens, spoken, to_text

VERIFIED, REPAIRED, WITHHELD = "verified", "repaired", "withheld"

# A second, clearly lower trust tier for pages with no usable glyph layer (a
# scan or a photo of handwriting): the reading can be reported but never
# proven against the source, so it is never "verified". See
# decide_scanned_equation below; this status never appears on a page that
# has a glyph layer.
AI_READ = "ai_read"


@dataclass
class Attempt:
    latex: str
    glyph_diffs: list[str]          # Channel B disagreements (plain English)
    visual_diffs: list[str]         # Channel C findings
    parse_error: Optional[str] = None
    advisory: bool = False          # True -> visual_diffs did not withhold

    @property
    def passed(self) -> bool:
        """True when nothing here withholds the attempt (advisory C does not)."""
        if self.parse_error or self.glyph_diffs:
            return False
        if self.advisory:
            return True
        return not self.visual_diffs

    @property
    def visual_clean(self) -> bool:
        """True when the visual check ran and found nothing."""
        return not self.visual_diffs


@dataclass
class EquationResult:
    id: str
    bbox: tuple
    status: str
    latex: Optional[str]            # the published LaTeX (None when withheld)
    raw_text: str                   # glyph-layer text, the fallback for withheld items
    glyph_layer: bool               # was Channel B available?
    channels: list[str]             # which channels actually ran
    attempts: list[Attempt] = field(default_factory=list)
    glyph_form: str = ""            # Channel B structure, for the report
    crop_png: Optional[str] = None
    cautions: list[str] = field(default_factory=list)   # ai_read only: never gates anything

    @property
    def explanation(self) -> str:
        last = self.attempts[-1] if self.attempts else None
        if self.status == VERIFIED:
            if self.glyph_layer:
                base = "The reading matched the PDF text layer (Channel B)."
                if "C" in self.channels and last and last.visual_diffs:
                    base += (" The visual check flagged " + "; ".join(last.visual_diffs)
                             + "; the glyph layer confirmed the reading, so the "
                               "visual finding is advisory only.")
                elif "C" in self.channels:
                    base += " The visual check found no differences."
                return base
            return "The reading passed the visual check; no glyph layer was available."
        if self.status == REPAIRED:
            first = self.attempts[0]
            issue = (first.glyph_diffs + first.visual_diffs + [first.parse_error or ""])[0]
            return f"First reading was corrected after a check found: {issue}"
        if self.status == AI_READ:
            base = "No glyph layer (Channel B) was available on this page, so Channel A's reading is reported but not proven."
            if self.cautions:
                base += " Caution: " + "; ".join(self.cautions)
            return base
        reasons = (last.glyph_diffs + last.visual_diffs + ([last.parse_error] if last and last.parse_error else [])) if last else []
        return "Could not be verified: " + (reasons[0] if reasons else "no reading available")

    @property
    def plain_explanation(self) -> str:
        """Short, jargon-free status line for students and judges.

        No "Channel A/B/C", no "glyph layer" — those stay in the report's
        expandable technical details, which read from `explanation` instead.
        """
        if self.status == VERIFIED:
            return "Checked against the PDF: correct."
        if self.status == REPAIRED:
            return "Corrected after checking."
        if self.status == AI_READ:
            if self.cautions:
                return "AI reading, not proven against the source. A check flagged something here."
            return "AI reading, not proven against the source."
        return "Couldn't be confirmed, so it isn't read as math."

    @property
    def timeline(self) -> list[str]:
        """Plain step-by-step account for the report: what was read, any
        disagreement that triggered a re-read, and the final outcome.

        Built only from the real attempts -- nothing here is synthesized.
        Shape matches the simplest case exactly ("Read" -> "Confirmed") and
        grows to the full repair loop only when a second attempt actually
        happened: Read -> disagreement with the source -> re-read with that
        evidence -> confirmed / withheld.
        """
        if not self.attempts:
            return []
        first = self.attempts[0]
        read_step = f"Read: {first.latex}" if first.latex else "Read: the reading call failed"

        def outcome() -> str:
            if self.status == VERIFIED:
                return "Confirmed"
            if self.status == REPAIRED:
                return "Confirmed after correction"
            if self.status == "ai_read":  # reserved for the scans feature
                return "Read by AI — not independently verified"
            return "Withheld"

        # advisory C notes (born-digital) and ai_read cautions (scans) never
        # gate the result, but are worth surfacing alongside a clean pass.
        notes = list(first.visual_diffs) + list(getattr(self, "cautions", []))
        if first.passed and self.status in (VERIFIED, "ai_read"):
            step = outcome()
            if notes:
                step += " (a check also noted: " + "; ".join(notes) + " — advisory only, did not change the result)"
            return [read_step, step]

        only_parse_error = first.parse_error and not first.glyph_diffs and not (first.visual_diffs and not first.advisory)
        if only_parse_error:
            disagreement = f"Could not be read: {first.parse_error}"
        else:
            problems = first.glyph_diffs + ([first.parse_error] if first.parse_error else []) + \
                (first.visual_diffs if not first.advisory else [])
            disagreement = "Disagreement with the source: " + ("; ".join(problems) if problems else "could not be checked")

        if len(self.attempts) > 1:
            second = self.attempts[1]
            return [read_step, disagreement, f"Re-read with that evidence: {second.latex}", outcome()]
        return [read_step, disagreement, outcome()]


def _visual(crop_png: Optional[str], latex: str, compare: Callable, render: Callable,
            workdir: str, tag: str) -> list[str]:
    """Run Channel C and return its findings; record an error as a finding."""
    try:
        rendered = render(latex, os.path.join(workdir, f"{tag}_render.png"), crop_png)
        return compare(crop_png, rendered)
    except Exception as e:  # model error, unparseable output, render failure, ...
        return [f"the visual check could not run ({type(e).__name__})"]


def _ocr_mismatch(ocr_text: str, latex: str) -> Optional[str]:
    """A large disagreement between an existing OCR/text-layer snippet inside
    the equation's region and Channel A's reading. Returns a plain-English
    caution, or None when they are reasonably close. This is a weak signal
    only -- it can add a caution, never verify or withhold anything."""
    import difflib
    import re

    def _chars(s: str) -> str:
        return re.sub(r"[^0-9A-Za-z]", "", s).lower()

    reading_chars = _chars(re.sub(r"\\[a-zA-Z]+", "", latex))
    ocr_chars = _chars(ocr_text)
    if not reading_chars or not ocr_chars:
        return None
    ratio = difflib.SequenceMatcher(a=ocr_chars, b=reading_chars, autojunk=False).ratio()
    if ratio < 0.4:
        return f"the page's own text here ({ocr_text!r}) does not closely match the reading ({latex!r})"
    return None


def decide_scanned_equation(
    eq_id: str,
    bbox,
    crop_png: Optional[str],
    transcribe: Callable[[str], str],
    compare: Optional[Callable[[str, str], list[str]]] = None,
    render: Optional[Callable[[str, str], str]] = None,
    ocr_text: Optional[str] = None,
    workdir: str = ".",
) -> EquationResult:
    """Decision rule for a page with no usable glyph layer (a scan or a photo
    of handwriting).

    Channel A reads the equation. Channel C (if available) and any OCR text
    found inside the region are CAUTIONS only -- neither can gate the result,
    because neither is proof. The only way to withhold here is Channel A
    itself failing or returning invalid LaTeX, exactly as elsewhere: with no
    glyph layer there is nothing to repair against, so there is no repair
    step. A successful, parseable reading is always reported as "ai_read",
    never "verified" -- that distinction is the entire point of this path.
    """
    channels = ["A"]
    if compare and render:
        channels.append("C")
    result = EquationResult(eq_id, tuple(bbox), WITHHELD, None, raw_text="",
                            glyph_layer=False, channels=channels, crop_png=crop_png)

    try:
        latex = transcribe(crop_png)
    except Exception:
        result.attempts.append(Attempt(
            "", [], [], parse_error="the reading call failed (Channel A did not return a reading)"))
        return result

    try:
        latex_to_tokens(latex)
    except LatexParseError as e:
        result.attempts.append(Attempt(latex, [], [], parse_error=f"the reading is not valid LaTeX ({e})"))
        return result

    cautions: list[str] = []
    if compare and render and crop_png:
        cautions.extend(_visual(crop_png, latex, compare, render, workdir, f"{eq_id}_scan"))
    if ocr_text:
        mismatch = _ocr_mismatch(ocr_text, latex)
        if mismatch:
            cautions.append(mismatch)

    result.attempts.append(Attempt(latex, [], [], parse_error=None))
    result.status, result.latex, result.cautions = AI_READ, latex, cautions
    return result


def _check_gate(latex: str, crop_png: Optional[str], compare: Optional[Callable],
                render: Optional[Callable], workdir: str, tag: str) -> Attempt:
    """C as a gate: any finding (including an error) will withhold the reading."""
    visual_diffs = _visual(crop_png, latex, compare, render, workdir, tag)
    return Attempt(latex, [], visual_diffs, parse_error=None, advisory=False)


def _check_with_b(latex: str, b_tokens: list[Token], crop_png: Optional[str],
                  compare: Optional[Callable], render: Optional[Callable],
                  workdir: str, tag: str) -> Attempt:
    """B decides; C runs only as advice."""
    try:
        a_tokens = latex_to_tokens(latex)
    except LatexParseError as e:
        return Attempt(latex, [], [], parse_error=f"the reading is not valid LaTeX ({e})")
    glyph_diffs = [d.explain() for d in diff(b_tokens, a_tokens)]

    visual_diffs: list[str] = []
    if compare and render and crop_png and not glyph_diffs:
        # Run C only once the cheap, exact check has already passed.
        visual_diffs = _visual(crop_png, latex, compare, render, workdir, tag)
    return Attempt(latex, glyph_diffs, visual_diffs, parse_error=None, advisory=True)


def verify_equation(
    eq_id: str,
    page,
    bbox,
    crop_png: Optional[str],
    transcribe: Callable[[str], str],
    repair: Optional[Callable[[str, str, list[str]], str]] = None,
    compare: Optional[Callable[[str, str], list[str]]] = None,
    render: Optional[Callable[[str, str], str]] = None,
    use_glyphs: bool = True,
    workdir: str = ".",
) -> EquationResult:
    channels = ["A"]
    b_tokens = None
    if use_glyphs:
        try:
            b_tokens = glyph_tokens(page, bbox)
            channels.append("B")
        except GlyphLayerUnavailable:
            b_tokens = None
    if compare and render:
        channels.append("C")

    if b_tokens:
        raw = spoken(b_tokens)
    else:
        raw = glyph_text(page, bbox) if page is not None else ""
    result = EquationResult(eq_id, tuple(bbox), WITHHELD, None, raw, b_tokens is not None, channels,
                            glyph_form=to_text(b_tokens) if b_tokens else "", crop_png=crop_png)

    # Without the glyph layer AND without the visual check there is no
    # independent evidence at all, so nothing can be verified.
    if b_tokens is None and "C" not in channels:
        try:
            latex = transcribe(crop_png)
            result.attempts.append(Attempt(latex, [], [], parse_error=None))
            result.attempts[-1].visual_diffs = ["no independent evidence available"]
        except Exception:
            pass
        return result

    try:
        latex = transcribe(crop_png)
    except Exception:
        # A model error in Channel A means withheld: it can never verify.
        result.attempts.append(Attempt(
            "", [], [],
            parse_error="the reading call failed (Channel A did not return a reading)"))
        return result

    try:
        if b_tokens is not None:
            return _decide_with_b(result, eq_id, b_tokens, crop_png, latex, repair,
                                  compare, render, workdir)
        return _decide_with_c(result, eq_id, crop_png, latex, repair, compare, render, workdir)
    except Exception:
        # A model error while re-reading (Channel A) must fail closed, never verify.
        result.status, result.latex = WITHHELD, None
        return result


def _decide_with_b(result, eq_id, b_tokens, crop_png, latex, repair, compare, render, workdir) -> EquationResult:
    """Channel B is available: it is the gate, Channel C is advisory."""
    first = _check_with_b(latex, b_tokens, crop_png, compare, render, workdir, f"{eq_id}_a1")
    result.attempts.append(first)
    if first.passed:
        result.status, result.latex = VERIFIED, latex
        return result

    # A and B disagree (or the reading was not valid LaTeX): repair once.
    if repair:
        problems = first.glyph_diffs + first.visual_diffs + ([first.parse_error] if first.parse_error else [])
        latex2 = repair(crop_png, latex, problems)
        second = _check_with_b(latex2, b_tokens, crop_png, compare, render, workdir, f"{eq_id}_a2")
        result.attempts.append(second)
        if second.passed:
            result.status, result.latex = REPAIRED, latex2
            return result

    # Still disagreeing after one repair: withheld regardless of C.
    result.status, result.latex = WITHHELD, None
    return result


def _decide_with_c(result, eq_id, crop_png, latex, repair, compare, render, workdir) -> EquationResult:
    """No glyph layer: Channel C is the gate, and it fails closed."""
    first = _check_gate(latex, crop_png, compare, render, workdir, f"{eq_id}_a1")
    result.attempts.append(first)
    if first.passed:
        result.status, result.latex = VERIFIED, latex
        return result

    if repair:
        problems = list(first.visual_diffs)
        latex2 = repair(crop_png, latex, problems)
        second = _check_gate(latex2, crop_png, compare, render, workdir, f"{eq_id}_a2")
        result.attempts.append(second)
        if second.passed:
            result.status, result.latex = REPAIRED, latex2
            return result

    result.status, result.latex = WITHHELD, None
    return result

"""Reading-order layout for born-digital lecture pages, plus the variable glossary.

Deterministic: headings are detected by font size, body lines are merged into
paragraphs (re-joining hyphenated words), and each equation is placed where it
sits on the page. Single-column pages only; multi-column layout is roadmap.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from ingest.pdf import Page


@dataclass
class Block:
    kind: str                 # "heading", "para", "equation"
    y: float
    text: str = ""
    level: int = 2
    eq_id: str = ""
    glossary: list[tuple[str, str]] = field(default_factory=list)


def _line_text(line) -> str:
    out, prev = [], None
    for g in sorted(line, key=lambda g: g.x):
        if prev is not None and g.bbox[0] - prev.bbox[2] > 1.2:
            out.append(" ")
        out.append(g.c)
        prev = g
    return "".join(out)


def _inside(line, bbox) -> bool:
    return all(bbox[0] <= g.cx <= bbox[2] and bbox[1] <= g.cy <= bbox[3] for g in line)


def page_blocks(page: Page, equations: list[tuple[str, tuple]]) -> list[Block]:
    """equations: (eq_id, bbox) pairs already located on this page."""
    body_size = Counter(round(g.size) for g in page.glyphs).most_common(1)[0][0] if page.glyphs else 10
    blocks: list[Block] = [Block("equation", bbox[1], eq_id=eid) for eid, bbox in equations]

    para: list[str] = []
    para_y = None
    last_bottom = None

    def flush():
        nonlocal para, para_y
        if para:
            text = ""
            for part in para:
                if text.endswith("-") and part[:1].islower():
                    text = text[:-1] + part           # re-join "equa-" + "tion"
                else:
                    text = (text + " " + part).strip()
            blocks.append(Block("para", para_y, text=text))
        para, para_y = [], None

    ordered_lines = sorted(page.lines, key=lambda l: min(g.bbox[1] for g in l))
    lowest = ordered_lines[-1] if ordered_lines else None
    for line in ordered_lines:
        if any(_inside(line, b) for _, b in equations):
            flush()
            last_bottom = None
            continue
        top = min(g.bbox[1] for g in line)
        size = max(g.size for g in line)
        text = _line_text(line)
        if size >= body_size + 2:
            flush()
            blocks.append(Block("heading", top, text=text, level=2 if size >= body_size + 3 else 3))
            last_bottom = None
            continue
        # Lone page numbers at the foot of the page are dropped.
        if text.strip().isdigit() and (line is lowest or top > page.height * 0.85):
            continue
        if last_bottom is not None and top - last_bottom > size * 0.9:
            flush()
        if para_y is None:
            para_y = top
        para.append(text)
        last_bottom = max(g.bbox[3] for g in line)
    flush()

    blocks.sort(key=lambda b: b.y)
    _attach_glossaries(blocks)
    return blocks


_DEF = re.compile(r"(\S{1,6}?)\s+(?:is|denotes|represents|=)\s+((?:the|a|an)\s+[^,;.]+?)(?=,|;|\.|\s+and\s+\S{1,6}\s+(?:is|denotes)|$)")


def extract_definitions(text: str) -> list[tuple[str, str]]:
    """Pull "X is the Y" definitions from a 'where ...' sentence, verbatim."""
    m = re.match(r"\s*where\s+(.*)", text, re.I | re.S)
    if not m:
        return []
    clause = m.group(1)
    out = []
    for sym, meaning in _DEF.findall(clause):
        sym = sym.strip().lstrip("(").rstrip(",")
        out.append((sym, meaning.strip()))
    return out


def _attach_glossaries(blocks: list[Block]):
    """The 'where ...' paragraph right after an equation becomes its glossary.

    The definitions are quoted verbatim, so the paragraph is folded into the
    glossary instead of being read twice by the screen reader.
    """
    consumed = set()
    for i, b in enumerate(blocks):
        if b.kind == "equation" and i + 1 < len(blocks) and blocks[i + 1].kind == "para":
            defs = extract_definitions(blocks[i + 1].text)
            if defs:
                b.glossary = defs
                consumed.add(i + 1)
    blocks[:] = [b for j, b in enumerate(blocks) if j not in consumed]

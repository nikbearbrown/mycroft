"""UI regression check: Playwright screenshots of key pages, pixel-diffed against the baseline.

Requires the optional extras: pip install 'jboss-migrator[ui]' && playwright install chromium
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger(__name__)

VIEWPORT = {"width": 1366, "height": 900}


def _slug(page: str) -> str:
    return re.sub(r"[^\w.-]+", "_", page.strip("/")) or "root"


def snapshot(base_url: str, pages: list[str], out_dir: Path) -> dict[str, str]:
    from playwright.sync_api import sync_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    shots: dict[str, str] = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport=VIEWPORT)
        page = ctx.new_page()
        for p in pages:
            url = base_url.rstrip("/") + "/" + p.lstrip("/")
            page.goto(url, wait_until="networkidle")
            # Freeze animations and carets so screenshots are deterministic.
            page.add_style_tag(content="*{animation:none!important;transition:none!important;"
                                       "caret-color:transparent!important}")
            dest = out_dir / f"{_slug(p)}.png"
            page.screenshot(path=str(dest), full_page=True)
            shots[p] = str(dest)
        browser.close()
    return shots


@dataclass
class UiResult:
    diffs: dict[str, float] = field(default_factory=dict)   # page -> ratio of differing pixels
    failed: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failed


def diff_ratio(a: Path, b: Path, diff_out: Path | None = None) -> float:
    from PIL import Image, ImageChops

    img_a, img_b = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if img_a.size != img_b.size:
        return 1.0
    diff = ImageChops.difference(img_a, img_b)
    # Ignore sub-perceptual anti-aliasing noise.
    mask = diff.convert("L").point(lambda v: 255 if v > 16 else 0)
    changed = sum(1 for v in mask.getdata() if v)
    if diff_out and changed:
        mask.save(diff_out)
    return changed / (img_a.size[0] * img_a.size[1])


def compare(baseline: dict[str, str], current: dict[str, str], threshold: float,
            out_dir: Path) -> UiResult:
    result = UiResult()
    for page, before in baseline.items():
        after = current.get(page)
        if not after:
            result.failed.append(page)
            continue
        ratio = diff_ratio(Path(before), Path(after), out_dir / f"diff-{_slug(page)}.png")
        result.diffs[page] = ratio
        if ratio > threshold:
            result.failed.append(page)
    return result

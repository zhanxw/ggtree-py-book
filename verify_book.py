#!/usr/bin/env python3
"""Comprehensive static book verification for ggtree-py documentation."""

from __future__ import annotations

import ast
from html.parser import HTMLParser
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse


DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(DOCS_DIR, "figures", "book", "manifest.json")

EXPECTED_HTML_FILES = (
    ["index.html"]
    + [f"chapter{i}.html" for i in range(1, 14)]
    + ["faq.html", "api.html", "gallery.html"]
)

EXPECTED_ASSETS = [
    os.path.join("assets", "style.css"),
    os.path.join("assets", "book.js"),
    os.path.join("assets", "search_index.json"),
    os.path.join("assets", "search_data.js"),
]


class BookPageParser(HTMLParser):
    """Extracts IDs, links, images, figure cards, gallery cards, and index rows."""

    def __init__(self, filename: str) -> None:
        super().__init__(convert_charrefs=True)
        self.filename = filename
        self.ids: Set[str] = set()
        self.links: List[str] = []
        self.images: List[str] = []
        self.cards: List[Dict[str, Any]] = []
        self.gallery_card_count: int = 0
        self.gallery_card_links: Set[str] = set()
        self.master_index_rows: int = 0
        self.master_index_links: Set[str] = set()

        self._raw_depth = 0  # script / style / svg
        self._div_stack: List[str] = []
        self._in_gallery_grid = False
        self._gallery_grid_depth = 0
        self._in_master_table = False
        self._in_master_tbody = False

        self._active_card: Optional[Dict[str, Any]] = None
        self._card_div_depth = 0
        self._in_code_fold = False
        self._in_copy_code = False
        self._code_buf: List[str] = []

    @staticmethod
    def _attr_map(attrs: List[Tuple[str, Optional[str]]]) -> Dict[str, Optional[str]]:
        return {k.lower(): v for k, v in attrs}

    @staticmethod
    def _has_class(attr_map: Dict[str, Optional[str]], cls: str) -> bool:
        val = attr_map.get("class") or ""
        return cls in val.split()

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        t = tag.lower()
        amap = self._attr_map(attrs)

        if "id" in amap and amap["id"]:
            self.ids.add(amap["id"])

        if t in ("script", "style", "svg"):
            self._raw_depth += 1
            return
        if self._raw_depth > 0:
            return

        if t == "a" and amap.get("href"):
            href = amap["href"] or ""
            self.links.append(href)
            if self._in_gallery_grid and self._active_card is not None:
                self.gallery_card_links.add(href)
            if self._in_master_tbody:
                self.master_index_links.add(href)
        elif t == "img" and amap.get("src"):
            self.images.append(amap["src"] or "")

        if t == "div":
            if amap.get("id") == "gallery-grid":
                self._in_gallery_grid = True
                self._gallery_grid_depth = 1
            elif self._in_gallery_grid:
                self._gallery_grid_depth += 1

            if self._has_class(amap, "book-figure-card") and self._active_card is None:
                self._active_card = {
                    "id": amap.get("id") or "",
                    "has_figure": False,
                    "has_details": False,
                    "details_has_open": False,
                    "details_after_figure": False,
                    "has_copy_btn": False,
                    "code_blocks": [],
                }
                self._card_div_depth = 1
                if self._in_gallery_grid:
                    self.gallery_card_count += 1
            elif self._active_card is not None:
                self._card_div_depth += 1

        if t == "table" and amap.get("id") == "gallery-index-table":
            self._in_master_table = True
        elif t == "tbody" and self._in_master_table:
            self._in_master_tbody = True
        elif t == "tr" and self._in_master_tbody:
            self.master_index_rows += 1

        if self._active_card is not None:
            if t == "figure" and self._has_class(amap, "book-figure"):
                self._active_card["has_figure"] = True
            elif t == "details" and self._has_class(amap, "code-fold"):
                self._active_card["has_details"] = True
                if "open" in amap:
                    self._active_card["details_has_open"] = True
                if self._active_card["has_figure"]:
                    self._active_card["details_after_figure"] = True
                self._in_code_fold = True
            elif t == "button" and self._has_class(amap, "copy-btn"):
                self._active_card["has_copy_btn"] = True
            elif t == "code" and self._in_code_fold:
                self._in_copy_code = True
                self._code_buf = []

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in ("script", "style", "svg"):
            if self._raw_depth > 0:
                self._raw_depth -= 1
            return
        if self._raw_depth > 0:
            return

        if t == "code" and self._in_copy_code:
            self._in_copy_code = False
            if self._active_card is not None:
                self._active_card["code_blocks"].append("".join(self._code_buf))
            self._code_buf = []
        elif t == "details" and self._in_code_fold:
            self._in_code_fold = False
        elif t == "tbody" and self._in_master_tbody:
            self._in_master_tbody = False
        elif t == "table" and self._in_master_table:
            self._in_master_table = False
        elif t == "div":
            if self._active_card is not None:
                self._card_div_depth -= 1
                if self._card_div_depth == 0:
                    self.cards.append(self._active_card)
                    self._active_card = None
            if self._in_gallery_grid:
                self._gallery_grid_depth -= 1
                if self._gallery_grid_depth == 0:
                    self._in_gallery_grid = False

    def handle_data(self, data: str) -> None:
        if self._in_copy_code:
            self._code_buf.append(data)


def main() -> int:
    errors: List[str] = []

    # 1. Core HTML and asset files
    for rel in EXPECTED_HTML_FILES + EXPECTED_ASSETS:
        full = os.path.join(DOCS_DIR, rel)
        if not os.path.isfile(full):
            errors.append(f"Missing expected file: {full}")
        elif os.path.getsize(full) == 0:
            errors.append(f"Empty expected file: {full}")

    # 2. Manifest & figure SVGs/PNGs + manifest code AST validation
    if not os.path.isfile(MANIFEST_PATH):
        errors.append(f"Missing manifest: {MANIFEST_PATH}")
        figs: List[Dict[str, Any]] = []
    else:
        with open(MANIFEST_PATH, encoding="utf-8") as fp:
            manifest = json.load(fp)
        figs = manifest if isinstance(manifest, list) else manifest.get("figures", [])
        if len(figs) < 54:
            errors.append(f"Expected >= 54 figures in manifest.json, found {len(figs)}")
        for fig in figs:
            fid = fig.get("id", "?")
            for ext_key in ("svg_path", "png_path"):
                rel = fig.get(ext_key, "")
                full = os.path.join(DOCS_DIR, rel)
                if not rel or not os.path.isfile(full) or os.path.getsize(full) == 0:
                    errors.append(f"Missing/empty figure asset for {fid}: {full}")
            code = fig.get("code", "")
            try:
                ast.parse(code)
            except SyntaxError as exc:
                errors.append(f"SyntaxError in manifest code for {fid}: {exc}")

    # 3. Validate search_index.json & search_data.js
    si_path = os.path.join(DOCS_DIR, "assets", "search_index.json")
    if os.path.isfile(si_path):
        with open(si_path, encoding="utf-8") as fp:
            si = json.load(fp)
        if not isinstance(si, list) or len(si) == 0:
            errors.append("assets/search_index.json must be a non-empty JSON list")

    # 4. Parse all 17 HTML pages
    parsed_pages: Dict[str, BookPageParser] = {}
    raw_html_pages: Dict[str, str] = {}
    for fname in EXPECTED_HTML_FILES:
        full = os.path.join(DOCS_DIR, fname)
        if not os.path.isfile(full):
            continue
        with open(full, encoding="utf-8") as fp:
            raw = fp.read()
        raw_html_pages[fname] = raw
        parser = BookPageParser(fname)
        parser.feed(raw)
        parsed_pages[fname] = parser

    # 5. Check every local <a href> and #fragment across all pages
    for fname, parser in parsed_pages.items():
        for href in parser.links:
            if href.startswith(("http://", "https://", "mailto:", "javascript:", "data:")):
                continue
            parsed = urlparse(href)
            target_file = parsed.path or fname
            target_path = os.path.normpath(os.path.join(DOCS_DIR, target_file))
            if not os.path.exists(target_path):
                errors.append(f"[{fname}] Broken local link: {href!r} -> {target_path}")
                continue
            if parsed.fragment:
                frag = parsed.fragment
                if target_file in parsed_pages:
                    if frag not in parsed_pages[target_file].ids:
                        errors.append(
                            f"[{fname}] Missing fragment #{frag} in {target_file} (href={href!r})"
                        )

        # 6. Check every <img src>
        for src in parser.images:
            if src.startswith(("http://", "https://", "data:")):
                continue
            img_path = os.path.normpath(os.path.join(DOCS_DIR, src))
            if not os.path.isfile(img_path) or os.path.getsize(img_path) == 0:
                errors.append(f"[{fname}] Missing/empty <img src={src!r}> -> {img_path}")

        # 7. Check every .book-figure-card has figure + collapsed details.code-fold + valid AST code
        for idx, card in enumerate(parser.cards, start=1):
            cid = card["id"] or f"card#{idx}"
            if not card["has_figure"]:
                errors.append(f"[{fname}:{cid}] Missing <figure class='book-figure'> inside card")
            if not card["has_details"]:
                errors.append(f"[{fname}:{cid}] Missing <details class='code-fold'> inside card")
            if card["details_has_open"]:
                errors.append(f"[{fname}:{cid}] <details class='code-fold'> MUST be collapsed (no open attr)")
            if not card["details_after_figure"]:
                errors.append(f"[{fname}:{cid}] <details class='code-fold'> does not follow <figure>")
            if not card["has_copy_btn"]:
                errors.append(f"[{fname}:{cid}] Missing .copy-btn button inside card")
            if not card["code_blocks"]:
                errors.append(f"[{fname}:{cid}] Missing <code> block inside <details class='code-fold'>")
            for cblock in card["code_blocks"]:
                try:
                    ast.parse(cblock)
                except SyntaxError as exc:
                    errors.append(f"[{fname}:{cid}] SyntaxError in rendered HTML code block: {exc}")

    expected_total = len(figs)

    # 8. Gallery coverage: all figures in visual cards AND Master Index Table
    gal = parsed_pages.get("gallery.html")
    if gal is None:
        errors.append("gallery.html was not parsed")
    else:
        if expected_total and gal.gallery_card_count != expected_total:
            errors.append(f"[gallery.html] Expected {expected_total} cards in #gallery-grid, found {gal.gallery_card_count}")
        if expected_total and gal.master_index_rows != expected_total:
            errors.append(f"[gallery.html] Expected {expected_total} rows in #gallery-index-table tbody, found {gal.master_index_rows}")
        for fig in figs:
            chap = fig["chapter"]
            anchor = f"fig-{fig['num'].replace('.', '-')}"
            expected_href = f"faq.html#{anchor}" if chap == 14 else f"chapter{chap}.html#{anchor}"
            if expected_href not in gal.gallery_card_links:
                errors.append(f"[gallery.html] Missing figure card link {expected_href!r} in #gallery-grid")
            if expected_href not in gal.master_index_links:
                errors.append(f"[gallery.html] Missing figure row link {expected_href!r} in #gallery-index-table")

    # 9. Chapter 12 interactive SVG verification (fig_12_11)
    ch12_raw = raw_html_pages.get("chapter12.html", "")
    if "<svg" not in ch12_raw:
        errors.append("[chapter12.html] Expected inline interactive <svg> elements")
    if "data-tooltip=" not in ch12_raw:
        errors.append("[chapter12.html] Expected data-tooltip attributes on interactive SVG elements")
    if "ggtree-tooltip-box" not in ch12_raw:
        errors.append("[chapter12.html] Expected ggtree-tooltip-box interactive tooltip layer in SVG")

    # 10. Verify total figure cards across content chapters (Ch.1..Ch.13 + FAQ) == manifest count
    chapter_cards = sum(
        len(parsed_pages[f].cards)
        for f in [f"chapter{i}.html" for i in range(1, 14)] + ["faq.html"]
        if f in parsed_pages
    )
    if expected_total and chapter_cards != expected_total:
        errors.append(f"Expected {expected_total} figure cards across chapters+FAQ, found {chapter_cards}")

    if errors:
        print(f"VERIFICATION FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(
        f"VERIFICATION PASSED: {len(parsed_pages)} HTML pages, {len(figs)} manifest figures, "
        f"{chapter_cards} chapter/FAQ figure cards (all collapsed by default), "
        f"{gal.gallery_card_count} gallery cards, {gal.master_index_rows} master index rows, "
        f"0 broken links, 0 AST syntax errors."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

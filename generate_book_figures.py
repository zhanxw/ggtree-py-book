"""Generate all canonical treedata-book figures in SVG + PNG and emit manifest.json.

Every generated figure has a matching figure caption and self-contained Python
snippet so docs/build_book.py can place code directly beneath each figure inside a
collapsed <details> block.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = Path(__file__).resolve().parent
if (ROOT / "ggtree" / "__init__.py").is_file() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(DOCS_DIR) not in sys.path:
    sys.path.insert(0, str(DOCS_DIR))

from ggtree import ggtree_unset_interactive  # noqa: E402
from book_chapters.registry import (  # noqa: F401,E402
    APPENDIX,
    FIG_DIR,
    FIGURES,
    PART_I,
    PART_II,
    PART_III,
    PART_IV,
    _extract_code,
    register_figure,
)
import book_chapters  # noqa: F401,E402

# Re-export Chapter 10 and Chapter 13 figure callables expected by tests/test_book_features.py
from book_chapters.ch10 import (  # noqa: F401,E402
    _fig_10_1,
    _fig_10_2,
    _fig_10_3,
    _fig_10_4,
    _fig_10_5,
)
from book_chapters.ch13 import (  # noqa: F401,E402
    _fig_13_1,
    _fig_13_2,
    _fig_13_3,
    _fig_13_4,
    _fig_13_5,
)


def generate_all(chapters: Optional[Set[int]] = None) -> List[Dict[str, Any]]:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    # Remove retired figure assets from earlier layouts
    valid_ids = {entry["id"] for entry in FIGURES}
    for ext in ("svg", "png"):
        stale = FIG_DIR / f"fig_1_5.{ext}"
        if stale.exists():
            stale.unlink()
        if chapters is None:
            for p in FIG_DIR.glob(f"fig_*.{ext}"):
                if p.stem not in valid_ids:
                    p.unlink()

    manifest: List[Dict[str, Any]] = []
    for entry in FIGURES:
        fid = entry["id"]
        w, h = entry["width"], entry["height"]
        ch_num = int(entry["chapter"])
        svg_path = FIG_DIR / f"{fid}.svg"
        png_path = FIG_DIR / f"{fid}.png"
        should_render = chapters is None or ch_num in chapters or not (svg_path.exists() and png_path.exists())

        if should_render:
            ggtree_unset_interactive()
            plot_obj = entry["fn"]()
            svg_str = plot_obj.to_svg(width=w, height=h)
            png_bytes = plot_obj.to_png(width=w, height=h)
            svg_path.write_text(svg_str, encoding="utf-8")
            png_path.write_bytes(png_bytes)
            print(f"Generated {fid} ({w}x{h}) -> {png_path.name} [{len(png_bytes)} bytes]")

        code = _extract_code(entry["fn"])
        manifest.append(
            {
                "id": fid,
                "num": entry["num"],
                "chapter": entry["chapter"],
                "part": entry["part"],
                "section": entry["section"],
                "title": entry["title"],
                "caption": entry["caption"],
                "apis": entry["apis"],
                "width": w,
                "height": h,
                "interactive": entry["interactive"],
                "svg_path": f"figures/book/{fid}.svg",
                "png_path": f"figures/book/{fid}.png",
                "code": code,
            }
        )

    manifest_path = FIG_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote manifest with {len(manifest)} figures -> {manifest_path}")
    return manifest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ggtree-py book figures and manifest.json")
    parser.add_argument(
        "--chapters",
        type=str,
        default=None,
        help="Comma-separated chapter numbers (e.g. 1,2,3 or 14 for FAQ) to regenerate; omits rebuilding unchanged chapters.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    sel = {int(tok.strip()) for tok in args.chapters.split(",") if tok.strip()} if args.chapters else None
    generate_all(chapters=sel)

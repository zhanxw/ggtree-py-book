"""Shared figure registry and metadata helpers for book chapter generators."""

from __future__ import annotations

import ast
import inspect
import textwrap
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

FIG_DIR = Path(__file__).resolve().parent.parent / "figures" / "book"
FIGURES: List[Dict[str, Any]] = []

PART_I = "Part I: Tree Data Input, Output and Manipulation"
PART_II = "Part II: Tree Visualization, Interpretation and Annotation"
PART_III = "Part III: ggtree Extensions"
PART_IV = "Part IV: Miscellaneous Topics"
APPENDIX = "Appendix"


def register_figure(
    fig_id: str,
    num: str,
    chapter: int,
    part: str,
    section: str,
    title: str,
    caption: str,
    apis: List[str],
    size: Tuple[int, int] = (780, 480),
    interactive: bool = False,
) -> Callable[[Callable[[], Any]], Callable[[], Any]]:
    def _dec(fn: Callable[[], Any]) -> Callable[[], Any]:
        FIGURES.append(
            {
                "id": fig_id,
                "num": num,
                "chapter": chapter,
                "part": part,
                "section": section,
                "title": title,
                "caption": caption,
                "apis": list(apis),
                "width": int(size[0]),
                "height": int(size[1]),
                "interactive": bool(interactive),
                "fn": fn,
            }
        )
        return fn

    return _dec


def _extract_code(fn: Callable[[], Any]) -> str:
    src = inspect.getsource(fn)
    lines = src.splitlines()
    def_idx = next((i for i, ln in enumerate(lines) if ln.lstrip().startswith("def ")), 0)
    body = textwrap.dedent("\n".join(lines[def_idx + 1 :])).strip("\n")
    out_lines = body.splitlines()
    if out_lines and out_lines[-1].strip().startswith("return "):
        expr = out_lines[-1].strip()[len("return ") :].strip()
        out_lines[-1] = expr
    code = "\n".join(out_lines) + "\n"
    ast.parse(code)
    return code

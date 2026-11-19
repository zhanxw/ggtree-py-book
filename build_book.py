"""Build the static multi-chapter treedata-book documentation website in docs/."""

from __future__ import annotations

import html
import io
import json
import keyword
import sys
import tokenize
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
if (ROOT / "ggtree" / "__init__.py").is_file() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import ggtree as gg

DOCS_DIR = Path(__file__).resolve().parent
ASSETS_DIR = DOCS_DIR / "assets"
MANIFEST_PATH = DOCS_DIR / "figures" / "book" / "manifest.json"


# ------------------------------------------------------------------------------
# Pure-Python Syntax Highlighter (via stdlib tokenize)
# ------------------------------------------------------------------------------

def highlight_python(code: str) -> str:
    """Highlight Python code into HTML <span> tokens using stdlib tokenize."""
    lines = code.splitlines(keepends=True)
    if not lines:
        return ""
    tokens_out: List[str] = []
    cur_row = 1
    cur_col = 0
    call_next_check = True
    try:
        tok_list = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except tokenize.TokenError:
        return html.escape(code)

    def _emit_gap(to_row: int, to_col: int) -> None:
        nonlocal cur_row, cur_col
        while cur_row < to_row:
            line_text = lines[cur_row - 1] if cur_row - 1 < len(lines) else ""
            if cur_col < len(line_text):
                tokens_out.append(html.escape(line_text[cur_col:]))
            cur_row += 1
            cur_col = 0
        if cur_col < to_col and cur_row - 1 < len(lines):
            tokens_out.append(html.escape(lines[cur_row - 1][cur_col:to_col]))
            cur_col = to_col

    n = len(tok_list)
    for idx, tok in enumerate(tok_list):
        ttype, tstr, (srow, scol), (erow, ecol), _ = tok
        if ttype in (tokenize.ENCODING, tokenize.ENDMARKER, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
            if erow > cur_row or ecol > cur_col:
                _emit_gap(erow, ecol)
            continue
        _emit_gap(srow, scol)
        esc = html.escape(tstr)
        if ttype == tokenize.COMMENT:
            tokens_out.append(f'<span class="tok-com">{esc}</span>')
        elif ttype == tokenize.STRING:
            tokens_out.append(f'<span class="tok-str">{esc}</span>')
        elif ttype == tokenize.NUMBER:
            tokens_out.append(f'<span class="tok-num">{esc}</span>')
        elif ttype == tokenize.NAME:
            if keyword.iskeyword(tstr):
                tokens_out.append(f'<span class="tok-kw">{esc}</span>')
            elif idx + 1 < n and tok_list[idx + 1].string == "(":
                tokens_out.append(f'<span class="tok-call">{esc}</span>')
            else:
                tokens_out.append(esc)
        elif ttype == tokenize.OP:
            tokens_out.append(f'<span class="tok-op">{esc}</span>')
        else:
            tokens_out.append(esc)
        cur_row, cur_col = erow, ecol

    return "".join(tokens_out)


# ------------------------------------------------------------------------------
# Book Metadata & Chapter Definitions
# ------------------------------------------------------------------------------

NAV_SECTIONS: List[Tuple[str, List[Tuple[str, str, str]]]] = [
    ("Preface", [("index.html", "", "Welcome & Overview")]),
    (
        "Part I: Tree Data I/O & Manipulation",
        [
            ("chapter1.html", "1.", "Importing Tree with Data"),
            ("chapter2.html", "2.", "Manipulating Tree with Data"),
            ("chapter3.html", "3.", "Exporting Trees with Data"),
        ],
    ),
    (
        "Part II: Visualization & Annotation",
        [
            ("chapter4.html", "4.", "Phylogenetic Tree Visualization"),
            ("chapter5.html", "5.", "Phylogenetic Tree Annotation"),
            ("chapter6.html", "6.", "Visual Exploration of Trees"),
            ("chapter7.html", "7.", "Plotting Tree with Data"),
            ("chapter8.html", "8.", "Silhouettes & Sub-plots"),
        ],
    ),
    (
        "Part III: ggtree Extensions",
        [
            ("chapter9.html", "9.", "Other Tree-like Structures"),
            ("chapter10.html", "10.", "ggtreeExtra Circular Rings"),
            ("chapter11.html", "11.", "Other ggtree Extensions"),
            ("chapter12.html", "12.", "ggtree Utilities"),
        ],
    ),
    (
        "Part IV: Miscellaneous Topics",
        [
            ("chapter13.html", "13.", "Gallery of Examples"),
        ],
    ),
    (
        "Appendix & Index",
        [
            ("faq.html", "A.", "Frequently Asked Questions"),
            ("api.html", "B.", "ggtree-py API Reference"),
            ("gallery.html", "★", "All Figures Gallery & Index"),
        ],
    ),
]

ORDERED_PAGES: List[Tuple[str, str]] = [
    ("index.html", "Preface & Overview"),
    ("chapter1.html", "1. Importing Tree with Data"),
    ("chapter2.html", "2. Manipulating Tree with Data"),
    ("chapter3.html", "3. Exporting Trees with Data"),
    ("chapter4.html", "4. Phylogenetic Tree Visualization"),
    ("chapter5.html", "5. Phylogenetic Tree Annotation"),
    ("chapter6.html", "6. Visual Exploration of Trees"),
    ("chapter7.html", "7. Plotting Tree with Data"),
    ("chapter8.html", "8. Silhouettes & Sub-plots"),
    ("chapter9.html", "9. Other Tree-like Structures"),
    ("chapter10.html", "10. ggtreeExtra Circular Rings"),
    ("chapter11.html", "11. Other ggtree Extensions"),
    ("chapter12.html", "12. ggtree Utilities"),
    ("chapter13.html", "13. Gallery of Examples"),
    ("faq.html", "Appendix A: FAQ"),
    ("api.html", "Appendix B: API Reference"),
    ("gallery.html", "All Figures Gallery & Index"),
]

_CODE_SEQ = 0


def next_code_id() -> str:
    global _CODE_SEQ
    _CODE_SEQ += 1
    return f"code-blk-{_CODE_SEQ}"


def render_code_snippet(title: str, code: str) -> str:
    cid = next_code_id()
    return (
        f'<div class="standalone-code">'
        f'<div class="standalone-code-head"><span>{html.escape(title)}</span>'
        f'<button type="button" class="copy-btn" data-code-target="{cid}">Copy</button></div>'
        f'<pre><code id="{cid}">{highlight_python(code)}</code></pre></div>'
    )


def render_figure_card(fig: Dict[str, Any], inline_svg: bool = False, gallery_mode: bool = False) -> str:
    fid = fig["id"]
    anchor = f"fig-{fig['num'].replace('.', '-')}"
    cid = next_code_id()
    pills = "".join(f'<span class="api-pill">{html.escape(a)}</span>' for a in fig["apis"][:4])
    media_html = ""
    if inline_svg:
        svg_file = DOCS_DIR / fig["svg_path"]
        raw_svg = svg_file.read_text(encoding="utf-8")
        # Ensure responsive width/height scaling while preserving exact viewBox
        media_html = raw_svg
    else:
        media_html = f'<img src="{html.escape(fig["svg_path"])}" alt="Figure {html.escape(fig["num"])}: {html.escape(fig["title"])}" loading="lazy"/>'

    chap = fig["chapter"]
    chap_href = f"faq.html#{anchor}" if chap == 14 else f"chapter{chap}.html#{anchor}"
    head_bar = ""
    if gallery_mode:
        head_bar = (
            f'<div class="gallery-card-head">'
            f'<span><span class="gallery-badge">Figure {html.escape(fig["num"])}</span> · {html.escape(fig["title"])}</span>'
            f'<a href="{chap_href}">Go to Ch. {"A" if chap == 14 else chap} &rarr;</a>'
            f'</div>'
        )

    part_slug = "part1" if chap in (1, 2, 3) else ("part2" if chap in (4, 5, 6, 7, 8) else ("part3" if chap in (9, 10, 11, 12) else ("part4" if chap == 13 else "appendix")))
    search_blob = f"Figure {fig['num']} {fig['title']} {fig['section']} {fig['caption']} {' '.join(fig['apis'])}"
    card_cls = "book-figure-card gallery-card" if gallery_mode else "book-figure-card"
    card_attrs = (
        f' data-part="{part_slug}" data-chapter="{chap}" data-search="{html.escape(search_blob, quote=True)}"'
        if gallery_mode
        else f' id="{anchor}"'
    )

    # IMPORTANT: <details class="code-fold"> intentionally OMITS `open` so all figure code is collapsed by default.
    return (
        f'<div class="{card_cls}"{card_attrs}>\n'
        f'  {head_bar}\n'
        f'  <figure class="book-figure">\n'
        f'    <div class="figure-media">{media_html}</div>\n'
        f'    <figcaption class="figure-caption"><strong>Figure {html.escape(fig["num"])}: {html.escape(fig["title"])}.</strong> {html.escape(fig["caption"])}</figcaption>\n'
        f'  </figure>\n'
        f'  <details class="code-fold">\n'
        f'    <summary>\n'
        f'      <span class="summary-left"><span class="summary-caret">&#9654;</span> Show / Hide Python Code</span>\n'
        f'      <span class="summary-actions">{pills}<button type="button" class="copy-btn" data-code-target="{cid}">Copy</button></span>\n'
        f'    </summary>\n'
        f'    <pre><code id="{cid}">{highlight_python(fig["code"])}</code></pre>\n'
        f'  </details>\n'
        f'</div>'
    )


def build_chapter_spec() -> Dict[int, Dict[str, Any]]:
    """Structured narrative sections for Chapters 1..13 + Appendix A (14)."""
    return {
        1: {
            "part": "Part I: Tree Data Input, Output and Manipulation",
            "title": "1. Importing Tree with Data",
            "intro": (
                "Phylogenetic trees rarely exist in isolation: evolutionary analyses pair branching topologies "
                "with divergence times, posterior probabilities, substitution rates, placement counts, or "
                "gene-level selection statistics. In <code>ggtree-py</code>, <code>Phylo</code> holds core "
                "ape-compatible structure (<code>edge</code>, <code>tip_label</code>, <code>edge_length</code>, "
                "<code>node_label</code>), while <code>TreeData</code> binds rich node- and branch-indexed "
                "annotations in <code>td.data</code> and <code>td.extraInfo</code>."
            ),
            "sections": [
                (
                    "overview",
                    "1.1 Overview",
                    "<p>Standard readers in <code>ggtree-py</code> mirror both <code>ape</code> and <code>treeio</code>: "
                    "plain Newick/Nexus files return a lightweight <code>Phylo</code> (or <code>MultiPhylo</code>), "
                    "whereas BEAST, NHX, EPA/pplacer, jtree, RAxML, CodeML, and Nextstrain Auspice JSON parsers return a "
                    "unified <code>TreeData</code> object ready for <code>aes()</code> aesthetic mapping.</p>",
                    None,
                ),
                (
                    "tree-structure",
                    "1.2 Understanding Phylogenetic Tree Structure",
                    "<p>A phylogenetic tree comprises tips (leaves), internal nodes representing ancestral lineages, "
                    "a root node, and branch lengths encoding evolutionary divergence or time. <code>read_tree()</code> "
                    "parses Newick strings from files or inline <code>text=...</code> arguments, and layers such as "
                    "<code>geom_tippoint()</code>, <code>geom_nodepoint()</code>, <code>geom_rootpoint()</code>, and "
                    "<code>geom_label()</code> inspect these structural elements directly.</p>",
                    ["fig_1_1", "fig_1_2"],
                ),
                (
                    "treeio-import",
                    "1.3 Importing Tree with treeio",
                    "<p>Evolutionary analyses save annotations across heterogeneous file conventions—inline "
                    "<code>[&amp;...]</code> BEAST tags, colon-delimited NHX attributes, PAML CodeML <code>rst</code>/<code>mlc</code> "
                    "files, Nextstrain Auspice JSON, and JSON placements. <code>treeio</code> normalizes these parsers into common "
                    "<code>Phylo</code> and <code>TreeData</code> containers seamlessly consumable by <code>tidytree</code> and <code>ggtree</code>.</p>",
                    "fig_1_3",
                ),
                (
                    "extract-data",
                    "1.4 Extracting Data from Tree Object",
                    "<p>Once imported into a <code>TreeData</code> (or converted via <code>as_tibble()</code> / <code>fortify()</code>), "
                    "node and branch attributes such as <code>AA_subs</code> from <code>read_jtree()</code> become directly "
                    "mappable columns inside <code>aes()</code>.</p>",
                    "fig_1_4",
                ),
                (
                    "auspice-json",
                    "1.5 Importing Nextstrain Auspice JSON Trees",
                    "<p>Nextstrain builds export rich phylogenetic JSON files (Auspice v1 and v2) containing topology, "
                    "<code>node_attrs</code> (e.g., <code>country</code>, <code>region</code>, cumulative genetic divergence "
                    "<code>div</code>, and decimal-year <code>num_date</code> with optional confidence intervals), "
                    "<code>branch_attrs</code> (nucleotide/protein <code>mutations</code> and clade <code>labels</code>), and "
                    "<code>meta</code> color/geographic definitions. Parse Auspice JSON explicitly with "
                    "<code>read_auspice_json()</code> / <code>read_nextstrain_json()</code> (or R-style "
                    "<code>read.nextstrain.json()</code>), or pass an Auspice <code>.json</code> file path, "
                    "<code>pathlib.Path</code>, inline JSON string, or parsed <code>dict</code> directly into "
                    "<code>ggtree()</code>, <code>fortify()</code>, <code>as_phylo()</code>, or <code>as_treedata()</code>. "
                    "Switch effortlessly between root-to-tip divergence and calendar-year time scales using "
                    "<code>branch_length='div'</code> vs <code>branch_length='num_date'</code>.</p>",
                    "fig_1_5",
                ),
            ],
        },
        2: {
            "part": "Part I: Tree Data Input, Output and Manipulation",
            "title": "2. Manipulating Tree with Data",
            "intro": (
                "Integrating evolutionary inference outputs and external experimental metadata should never require fragile "
                "row-reordering hacks. <code>ggtree-py</code> implements <code>tidytree</code> tidy verbs, tree-data "
                "merging, rerooting, rescaling, subsetting, and multi-tree co-plotting helpers."
            ),
            "sections": [
                (
                    "merge-tree",
                    "2.1 Combining Tree Data with merge_tree()",
                    "<p>Separate analyses run on the same taxon topology—such as a dated BEAST tree and a CodeML "
                    "selection run—can be combined with <code>merge_tree()</code> so joint distributions of rates, "
                    "<code>dN</code>, <code>dS</code>, and <code>dN/dS</code> can be explored cleanly via "
                    "<code>fortify()</code>, <code>gather()</code>, and <code>geom_hex()</code>.</p>",
                    "fig_2_1",
                ),
                (
                    "join-reroot",
                    "2.2 Joining External Tables &amp; Rerooting Trees",
                    "<p>Using <code>left_join()</code> merges tip and internal-node attribute tables (resolving duplicate "
                    "columns with suffixes like <code>.x</code> and <code>.y</code>), while <code>root(trda, outgroup=..., edgelabel=True)</code> "
                    "reroots topologies while keeping edge and node annotations properly synchronized.</p>",
                    "fig_2_2",
                ),
                (
                    "rescale-tree",
                    "2.3 Rescaling Tree Branches",
                    "<p><code>rescale_tree(merged_tree, branch_length='dN')</code> replaces raw branch lengths with any "
                    "numeric annotation column (such as <code>dN</code> or evolutionary <code>rate</code>), enabling "
                    "side-by-side evolutionary comparisons.</p>",
                    "fig_2_3",
                ),
                (
                    "drop-subset",
                    "2.4 Subsetting and Pruning Trees",
                    "<p><code>drop_tip()</code> prunes unwanted taxa while remapping associated <code>TreeData</code> "
                    "attributes cleanly. For large phylogenies, <code>tree_subset()</code> isolates local focal neighborhoods "
                    "by tip label or internal node ID—tracking ancestry groups, preserved node data, and optional "
                    "<code>root_edge</code> stems via <code>geom_rootedge()</code>.</p>",
                    ["fig_2_4", "fig_2_5", "fig_2_6"],
                ),
                (
                    "multi-tree",
                    "2.5 Visualizing Multiple Trees Together",
                    "<p>Shifted or mirrored fortified tree frames (<code>fortify(tr)</code>) can be layered into a single "
                    "canvas via <code>geom_tree(data=d2, layout=...)</code> alongside dual independent highlight scales "
                    "(<code>new_scale_fill()</code>), shadowtext labels, and cross-tree correspondence lines.</p>",
                    ["fig_2_7", "fig_2_8"],
                ),
            ],
        },
        3: {
            "part": "Part I: Tree Data Input, Output and Manipulation",
            "title": "3. Exporting Tree with Data",
            "intro": (
                "Preserving node- and branch-level annotations during serialization allows reproducible archival and sharing "
                "across downstream phylogenetic tools such as FigTree without losing associated metadata."
            ),
            "sections": [
                (
                    "newick-export",
                    "3.1 Exporting Topologies via write_tree()",
                    "<p><code>write_tree(phy, file=...)</code> emits standard parenthetical Newick strings preserving internal "
                    "node labels, branch lengths, and optional root stem edges.</p>",
                    None,
                ),
                (
                    "beast-jtree",
                    "3.2 Exporting Tree Data to BEAST Nexus &amp; JSON",
                    "<p><code>write_beast()</code> serializes any annotated <code>TreeData</code>—such as NHX species tags "
                    "or PAML CodeML substitution statistics—into inline NEXUS <code>[&amp;...]</code> metadata comments that "
                    "<code>read_beast()</code> restores cleanly into mappable branch attributes, whereas <code>write_jtree()</code> / "
                    "<code>read_jtree()</code> exchanges structured JSON tree objects.</p>",
                    "fig_3_1",
                ),
            ],
        },
        4: {
            "part": "Part II: Tree Visualization, Interpretation and Annotation",
            "title": "4. Phylogenetic Tree Visualization",
            "intro": (
                "Visualizing evolutionary relationships effectively relies on choosing the right coordinate geometry, "
                "visual hierarchy, theme, and time axis. Extending <code>ggplot2</code>'s layered grammar, "
                "<code>ggtree()</code> turns any <code>Phylo</code>, <code>TreeData</code>, or <code>Hclust</code> "
                "into a customizable SVG/PNG canvas."
            ),
            "sections": [
                (
                    "basic-viz",
                    "4.1 Visualizing Phylogenetic Tree with ggtree",
                    "<p>The <code>ggtree()</code> function is a specialized wrapper around <code>ggplot() + geom_tree() + theme_tree()</code> "
                    "with built-in support for ladderization, cladograms (<code>branch_length='none'</code>), and uniform branch styling.</p>",
                    "fig_4_1",
                ),
                (
                    "layouts",
                    "4.2 Layouts and Derived Coordinate Systems",
                    "<p>Supported layouts span phylograms and cladograms across <code>rectangular</code>, <code>roundrect</code>, "
                    "<code>slanted</code>, <code>ellipse</code>, <code>circular</code>, <code>fan</code>, <code>equal_angle</code>, "
                    "and <code>daylight</code>, plus derived orientations via <code>scale_x_reverse()</code>, <code>coord_flip()</code>, "
                    "<code>layout_dendrogram()</code>, <code>layout_inward_circular()</code>, and rotated insets via <code>as_ggplot()</code>.</p>",
                    ["fig_4_2", "fig_4_3"],
                ),
                (
                    "timescale-2d",
                    "4.2.2–4.2.3 Time-Scaled Trees and Two-Dimensional Layouts",
                    "<p>Specifying the most recent sampling date (<code>mrsd</code>) calibrates horizontal coordinates in calendar years, "
                    "and setting <code>yscale</code> with <code>yscale_mapping</code> projects trees into two-dimensional trait-by-time space.</p>",
                    ["fig_4_4", "fig_4_5"],
                ),
                (
                    "display-geoms",
                    "4.3.1–4.3.4 Scale Bars, Nodes, Labels, and Root Edges",
                    "<p>Add evolutionary distance bars with <code>geom_treescale()</code> or axis ticks with <code>theme_tree2()</code>, "
                    "mark internal and tip nodes with <code>geom_nodepoint()</code> and <code>geom_tippoint()</code>, format radial or "
                    "y-axis tip labels via <code>geom_tiplab()</code>, and draw outgroup stems via <code>geom_rootedge()</code>.</p>",
                    ["fig_4_6", "fig_4_7", "fig_4_8", "fig_4_9"],
                ),
                (
                    "color-continuous",
                    "4.3.5 Coloring Branches and Continuous Trait Transitions",
                    "<p>Map node rates continuously along tree branches, reconstruct ancestral continuous states with <code>fastAnc()</code> "
                    "for interpolated branch transitions (<code>continuous='colour'</code>), and render trait phenograms via <code>yscale='trait'</code>.</p>",
                    ["fig_4_10", "fig_4_11", "fig_4_12"],
                ),
                (
                    "rescale-themes",
                    "4.3.6–4.3.7 Rescaling Branches and Customizing Themes",
                    "<p>Rescale branch lengths by any numeric node variable (substitution rate or <code>dN_vs_dS</code>) and customize "
                    "background canvas colors through <code>theme_tree()</code> and theme modifiers.</p>",
                    ["fig_4_13", "fig_4_14"],
                ),
                (
                    "multi-trees",
                    "4.4 Visualizing a List of Trees (multiPhylo, TreeDataList, DensiTree)",
                    "<p>Visualize multiple dated, bootstrapped, or annotated trees simultaneously via <code>facet_wrap('~.id')</code> "
                    "with per-panel aesthetic filtering (<code>td_filter()</code>, <code>new_scale_colour()</code>), or stack ensembles in "
                    "<code>ggdensitree()</code>.</p>",
                    ["fig_4_15", "fig_4_16", "fig_4_17", "fig_4_18"],
                ),
            ],
        },
        5: {
            "part": "Part II: Tree Visualization, Interpretation and Annotation",
            "title": "5. Phylogenetic Tree Annotation",
            "intro": (
                "Publication-quality phylogenies layer NHX attributes, clade brackets, shaded highlights, taxa links, "
                "uncertainty bars, and molecular selection statistics directly onto layout coordinates."
            ),
            "sections": [
                (
                    "grammar-nhx",
                    "5.1 Manipulating Tree Annotation with Grammar of Graphics",
                    "<p>All tree metadata columns (such as NHX species tags <code>S</code>, duplication flags <code>D</code>, and bootstrap "
                    "values <code>B</code>) bind directly to <code>geom_tiplab()</code>, <code>geom_label()</code>, and <code>geom_text()</code> "
                    "layers using midpoint coordinates (<code>x='branch'</code>).</p>",
                    "fig_5_1",
                ),
                (
                    "cladelab-strip",
                    "5.2.1–5.2.2 Labeling Clades and Associated Taxa",
                    "<p><code>geom_cladelab()</code> places aligned bars, rotated text, boxed labels, or organism silhouettes "
                    "(<code>geom='phylopic'</code>) beside monophyletic clades, while <code>geom_strip()</code> spans arbitrary taxa pairs.</p>",
                    ["fig_5_2", "fig_5_3", "fig_5_4"],
                ),
                (
                    "hilight-taxalink",
                    "5.2.3–5.2.4 Highlighting Clades and Linking Related Taxa",
                    "<p>Shade monophyletic groups across rectangular, circular, and unrooted layouts with <code>geom_hilight()</code> "
                    "(<code>rect</code>, <code>roundrect</code>, <code>encircle</code>, <code>gradient</code>) and <code>geom_balance()</code>, "
                    "and connect evolutionary partners using curved arrows from <code>geom_taxalink()</code>.</p>",
                    ["fig_5_5", "fig_5_6"],
                ),
                (
                    "uncertainty-software",
                    "5.2.5–5.3 Evolutionary Uncertainty Intervals and Software Annotations",
                    "<p>Overlay Bayesian or RelTime confidence intervals via <code>geom_range()</code> + <code>scale_x_range()</code>, "
                    "and display BEAST, HyPhy, and CODEML amino-acid substitutions and <code>dN/dS</code> ratios directly on branches.</p>",
                    ["fig_5_7", "fig_5_8", "fig_5_9", "fig_5_10"],
                ),
            ],
        },
        6: {
            "part": "Part II: Tree Visualization, Interpretation and Annotation",
            "title": "6. Visual Exploration of Phylogenetic Trees",
            "intro": (
                "Exploring large trees requires zooming onto focal clades, collapsing redundant subtrees, grouping OTUs, "
                "adjusting sister-node ordering, and rotating circular sectors without mutating underlying evolutionary relationships."
            ),
            "sections": [
                (
                    "view-scale",
                    "6.1–6.2 Viewing Selected Clades and Rescaling Vertical Span",
                    "<p><code>viewClade()</code> focuses the coordinate window onto any MRCA clade, while <code>scaleClade()</code> "
                    "compresses or expands clade spacing vertically without altering branch lengths.</p>",
                    ["fig_6_1", "fig_6_2"],
                ),
                (
                    "collapse-expand",
                    "6.3 Collapsing and Expanding Clades",
                    "<p><code>collapse()</code> hides subtrees or summarizes them as triangular wedges (<code>mode='max'</code>, <code>'min'</code>, "
                    "or <code>'mixed'</code>) with full reversibility via <code>expand()</code>.</p>",
                    ["fig_6_3", "fig_6_4"],
                ),
                (
                    "group-otu",
                    "6.4 Grouping OTUs on Clustering Trees",
                    "<p><code>dist()</code> and <code>bionj()</code> compute neighbor-joining trees directly from tabular traits, and "
                    "<code>groupOTU()</code> assigns shared ancestral clade memberships across taxon sets.</p>",
                    "fig_6_5",
                ),
                (
                    "rotate-open",
                    "6.5–6.7 Rotating Clades, Opening Sectors, and Rotating Circular Trees",
                    "<p>Reverse sibling order cleanly with <code>rotate()</code> and <code>flip()</code>, open closed circular trees "
                    "into fans with <code>open_tree()</code>, and reorient entire polar trees using <code>rotate_tree()</code>.</p>",
                    ["fig_6_6", "fig_6_7", "fig_6_8", "fig_6_9", "fig_6_10", "fig_6_11"],
                ),
            ],
        },
        7: {
            "part": "Part II: Tree Visualization, Interpretation and Annotation",
            "title": "7. Plotting Tree with Data",
            "intro": (
                "Modern phylogenomics integrates heterogeneous traits—tip measurements, internal node "
                "support values, SNP alleles, sequence alignments, and arbitrary ggplot2 panels—directly "
                "alongside tree tips with synchronized coordinate ordering."
            ),
            "sections": [
                (
                    "attaching-data",
                    "7.1 Attaching External Tables via %<+%",
                    "<p>Attach external tip and internal-node metadata frames via <code>%<+%</code> (or Python "
                    "<code>%</code>) so discrete shapes, continuous fills, and point sizes map seamlessly across "
                    "multiple layers.</p>",
                    "fig_7_1",
                ),
                (
                    "geom-facet",
                    "7.2 Aligning Panels with Tree Tips via geom_facet()",
                    "<p><code>geom_facet()</code> aligns external datasets in horizontal panels paired row-for-row "
                    "with tree tips using layers such as SNP <code>geom_point(shape='|')</code> and horizontal "
                    "<code>geom_col</code> trait bars.</p>",
                    "fig_7_2",
                ),
                (
                    "gheatmap",
                    "7.3 Matrix Heatmaps and Multiple Fill Scales",
                    "<p><code>gheatmap()</code> aligns discrete or continuous matrices to rectangular or circular trees, "
                    "while <code>new_scale_fill()</code> cleanly resets fill scales between concentric heatmaps.</p>",
                    ["fig_7_3", "fig_7_4"],
                ),
                (
                    "msaplot",
                    "7.4 Visualizing Multiple Sequence Alignments via msaplot()",
                    "<p><code>msaplot()</code> reads FASTA sequences via <code>read_fasta()</code> and maps residue "
                    "windows cleanly onto both rectangular and circular phylogenetic layouts.</p>",
                    "fig_7_5",
                ),
                (
                    "composite",
                    "7.5 Tree-Aligned Composite Plots (aplot)",
                    "<p>Unlike naive <code>plot_grid()</code> stacking, composite methods <code>insert_left()</code> and "
                    "<code>insert_right()</code> automatically reorder external <code>ggplot()</code> heatmaps and bar "
                    "charts by tree tip y-coordinates.</p>",
                    "fig_7_6",
                ),
            ],
        },
        8: {
            "part": "Part II: Tree Visualization, Interpretation and Annotation",
            "title": "8. Annotating Tree with Silhouette Images and Sub-plots",
            "intro": (
                "Photographic tip images, taxonomic silhouettes, ancestral probability subplots, and "
                "phylomoji icons communicate biological identity immediately alongside branch structure."
            ),
            "sections": [
                (
                    "frog-images",
                    "8.1 Annotating Trees with Images (geom_tiplab & geom_image)",
                    "<p>Map local JPEG/PNG image paths directly via <code>geom_tiplab(geom='image')</code> aligned to "
                    "tips or embed standalone canvas badges using <code>geom_image()</code>.</p>",
                    "fig_8_1",
                ),
                (
                    "phylopic",
                    "8.2 PhyloPic Organism Silhouettes",
                    "<p>Resolve taxon names cleanly via <code>phylopic_uid()</code> and color vector silhouettes along "
                    "discrete or continuous biological covariates such as body mass.</p>",
                    "fig_8_2",
                ),
                (
                    "insets",
                    "8.3 Ancestral State Reconstruction & Sub-plot Insets",
                    "<p>Compute marginal ancestral likelihoods with <code>ace(..., model='ER', type='discrete')</code>, "
                    "construct <code>nodebar()</code> and <code>nodepie()</code> micro-charts (including mixed mixes), "
                    "and overlay them using <code>geom_inset()</code>.</p>",
                    ["fig_8_3", "fig_8_4"],
                ),
                (
                    "phylomoji",
                    "8.4 Phylomoji and Apple Color Emoji",
                    "<p>Render tip labels, circular/fan leaves, and monochrome clade annotations using "
                    "<code>parse='emoji'</code> on rectangular, rotated fan, and Apple Color Emoji trees.</p>",
                    ["fig_8_5", "fig_8_6", "fig_8_7", "fig_8_8"],
                ),
            ],
        },
        9: {
            "part": "Part III: ggtree Extensions",
            "title": "9. ggtree for Other Tree-like Objects",
            "intro": (
                "Phylogenetic trait containers, taxonomic hierarchies, microbiome abundance tables, "
                "agglomerative clustering dendrograms, directed k-ary graphs, and general parent-child "
                "edge lists fortify into a uniform tree coordinate grammar."
            ),
            "sections": [
                (
                    "phylobase-ade4",
                    "9.1 phylo4d, ade4 Phylog, and phyloseq Objects",
                    "<p><code>ggtree()</code> natively visualizes <code>phylo4</code>/<code>phylo4d</code> trait tables, "
                    "<code>taxo2phylog()</code> rank hierarchies, and <code>phyloseq()</code> microbiome abundance "
                    "staggers and <code>geom_density_ridges</code> facets.</p>",
                    ["fig_9_1", "fig_9_2", "fig_9_3", "fig_9_4"],
                ),
                (
                    "hclust",
                    "9.2 Hierarchical Clustering Dendrograms (hclust & cutree)",
                    "<p>Cluster distance matrices via <code>hclust()</code>, cut subtrees with <code>cutree()</code>, "
                    "highlight clades via <code>groupClade()</code>, and orient top-down with <code>layout_dendrogram()</code>.</p>",
                    "fig_9_5",
                ),
                (
                    "treegraph",
                    "9.3 Directed Tree Graphs (graph_tree)",
                    "<p>Convert directed k-ary <code>graph_tree()</code> graphs into slanted dendrograms with selective "
                    "per-edge <code>arrow(length=unit(...))</code> arrowheads.</p>",
                    "fig_9_6",
                ),
                (
                    "edgelist",
                    "9.4 Arbitrary Hierarchical Edge Lists",
                    "<p>Any two-column parent–child table converts via <code>as_phylo()</code> into a hierarchical tree "
                    "ready for circular layouts and covariate mapping.</p>",
                    "fig_9_7",
                ),
            ],
        },
        10: {
            "part": "Part III: ggtree Extensions",
            "title": "10. ggtreeExtra for Presenting Data on Circular Layout",
            "intro": (
                "While <code>geom_facet()</code> excels in side-by-side rectangular panels, radial metagenomics, "
                "microbiome, and population-genomics datasets frequently arrange external data layers around circular "
                "or fan trees using <code>geom_fruit()</code>."
            ),
            "sections": [
                (
                    "fruit-intro",
                    "10.1 Introduction",
                    "<p>The <code>ggtreeExtra</code> grammar—<code>geom_fruit()</code> alongside <code>geom_star()</code>, "
                    "<code>new_scale_fill()</code>, and <code>new_scale_colour()</code>—aligns boxplots, symbol rings, "
                    "heatmaps, and barplots radially onto circular or rectangular phylogenies using a unified tidy API.</p>",
                    None,
                ),
                (
                    "fruit-structure",
                    "10.2 Aligning Graphs to the Tree Based on a Tree Structure",
                    "<p>Pair <code>ggtree(..., layout='fan', open_angle=10)</code> and <code>rotate_tree(..., -90)</code> with "
                    "<code>geom_fruit(data=melt_simple, geom=geom_boxplot, mapping=aes(y='OTU', x='val', group='label', fill='Phylum'))</code> "
                    "plus <code>axis_params</code> and <code>grid_params</code> to project abundance distributions radially per OTU.</p>",
                    "fig_10_1",
                ),
                (
                    "fruit-multi",
                    "10.3 Aligning Multiple Graphs to the Tree for Multi-dimensional Data",
                    "<p>Chain clade highlights (<code>geom_hilight</code>), curved italic clade labels (<code>geom_cladelab</code>), "
                    "tip star glyphs (<code>geom_star</code>), body-site tile rings (<code>geom_fruit(geom=geom_tile, aes(alpha=...))</code>), "
                    "and outer prevalence bars (<code>geom_fruit(geom=geom_bar)</code>)—and switch seamlessly between circular and "
                    "rectangular coordinates using <code>layout_rectangular()</code>.</p>",
                    ["fig_10_2", "fig_10_3"],
                ),
                (
                    "fruit-popgen",
                    "10.4 Examples for Population Genetics",
                    "<p>Combine lineage coloring via <code>groupOTU()</code>, dotted country tip connectors via <code>geom_tiplab(align=True)</code>, "
                    "antifungal susceptibility heatmap rings, and point-mutation or haplotype spike rings (<code>geom_star(starshape=26)</code>) "
                    "on large population cohorts such as <em>Candida auris</em> and 1,832 <em>S. Typhi</em> isolates.</p>",
                    ["fig_10_4", "fig_10_5"],
                ),
                (
                    "fruit-summary",
                    "10.5 Summary",
                    "<p>Because <code>geom_fruit()</code> tracks cumulative radial offsets and coordinates dynamically with the underlying "
                    "tree layout, multi-ring annotations remain aligned across rectangular, circular, and fan topologies.</p>",
                    None,
                ),
            ],
        },
        11: {
            "part": "Part III: ggtree Extensions",
            "title": "11. Other ggtree Extensions",
            "intro": (
                "Replicating Chapter 11 extensions in <code>ggtree-py</code>, including differential taxonomic clade "
                "cladograms via <code>ggdiffclade()</code> (ported from <em>MicrobiotaProcess</em>) and phylogenetic "
                "split networks via <code>read_nexus_networx()</code> + <code>ggsplitnet()</code> (ported from "
                "<em>phangorn</em> / <em>tanggle</em>)."
            ),
            "sections": [
                (
                    "microbiota-diffclade",
                    "11.1 Visualizing Quantitative Data with Tree Structure (ggdiffclade)",
                    "<p><code>ggdiffclade()</code> constructs a hierarchical taxonomy cladogram directly from taxonomic "
                    "assignment tables, highlights statistically enriched lineages radially, and annotates macro phyla "
                    "alongside alphabetical legend keys for finer clades.</p>",
                    "fig_11_1",
                ),
                (
                    "phylo-network",
                    "11.2 Visualizing Phylogenetic Network Using Tanggle (ggsplitnet)",
                    "<p>Parses Nexus <code>NETWORK</code> split-network blocks with <code>read_nexus_networx()</code> and "
                    "renders reticulate evolutionary edges via <code>ggsplitnet()</code> and <code>geom_splitnet()</code>.</p>",
                    "fig_11_2",
                ),
            ],
        },
        12: {
            "part": "Part III: ggtree Extensions",
            "title": "12. ggtree Utilities",
            "intro": (
                "Complete reproduction of all 11 Chapter 12 utility workflows in <code>ggtree-py</code>: facet "
                "proportion and label control, subset-aware geometric layers, dynamic layout transformations, "
                "per-panel axis limits, tidy filtering and unnesting, tip-order extraction, padded tip labels, "
                "and interactive SVG clade annotation."
            ),
            "sections": [
                (
                    "facet-widths",
                    "12.1.1 facet_widths",
                    "<p><code>facet_widths()</code> adjusts relative panel column widths consistently for both composite "
                    "<code>ggtree + geom_facet</code> plates and standard multi-facet <code>ggplot</code> panels.</p>",
                    "fig_12_1",
                ),
                (
                    "facet-labeller",
                    "12.1.2 facet_labeller",
                    "<p><code>facet_labeller()</code> renames one or more facet strip headers and composes seamlessly "
                    "with <code>facet_widths()</code>.</p>",
                    "fig_12_2",
                ),
                (
                    "geom-layers-subset",
                    "12.2 Geometric Layers",
                    "<p><code>geom_text2()</code> and <code>geom_label2()</code> evaluate row-level <code>subset</code> "
                    "predicates identically in both Cartesian <code>ggplot</code> charts and phylogenetic trees.</p>",
                    "fig_12_3",
                ),
                (
                    "layout-utilities",
                    "12.3 Layout Utilities",
                    "<p>Layout modifiers (<code>layout_dendrogram()</code>, <code>layout_rectangular()</code>, "
                    "<code>layout_circular()</code>, <code>layout_fan()</code>, <code>layout_inward_circular()</code>) "
                    "recompute coordinate geometry dynamically without rebuilding tree layers.</p>",
                    "fig_12_4",
                ),
                (
                    "xlim-expand",
                    "12.4.1 Expand x Limit for a Specific Facet Panel",
                    "<p>Combine <code>xlim_tree()</code> and <code>xlim_expand(limits, panel)</code> to tune axis spans "
                    "for individual <code>geom_facet()</code> or <code>facet_grid()</code> panels independently.</p>",
                    "fig_12_5",
                ),
                (
                    "hexpand-vexpand",
                    "12.4.2 Expand Plot Limit by Ratio (hexpand / vexpand)",
                    "<p><code>hexpand()</code> and <code>vexpand()</code> enlarge data bounds by a relative fraction in "
                    "either direction (<code>direction=-1</code> expands left/bottom).</p>",
                    "fig_12_6",
                ),
                (
                    "td-filter",
                    "12.5.1 Filter Tree Data (td_filter)",
                    "<p>Pass <code>td_filter(...)</code> as layer <code>data</code> to restrict geometric layers to "
                    "computed node subsets such as <code>offspring()</code> of an internal ancestor.</p>",
                    "fig_12_7",
                ),
                (
                    "td-unnest",
                    "12.5.2 Flatten List-Column Tree Data (td_unnest)",
                    "<p>Use <code>nest()</code> to store multi-observation list columns per tip and <code>td_unnest()</code> "
                    "(optionally composed with <code>_f=td_filter(...)</code>) to expand them during plotting.</p>",
                    "fig_12_8",
                ),
                (
                    "get-taxa-name",
                    "12.6.1 Extract Tip Order (get_taxa_name)",
                    "<p><code>get_taxa_name(p)</code> returns displayed tip labels in vertical top-to-bottom visual order "
                    "matching the plotted tree topology.</p>",
                    "fig_12_9",
                ),
                (
                    "label-pad",
                    "12.6.2 Padding Taxa Labels (label_pad)",
                    "<p><code>label_pad()</code> left-pads tip names with dots or spaces to uniform character width for "
                    "crisp monospace right-alignment alongside <code>geom_tiplab(..., align=True)</code>.</p>",
                    "fig_12_10",
                ),
                (
                    "interactive-identify",
                    "12.7 Interactive ggtree Annotation (identify)",
                    "<p>Interactive clade highlighting, labeling, and hover inspection powered by embedded SVG tooltips "
                    "(<code>geom_hilight_interactive</code>, <code>geom_cladelab_interactive</code>, "
                    "<code>geom_point_interactive</code>, <code>geom_tiplab_interactive</code>). Hover over nodes, tips, "
                    "or highlighted clades below to test live tooltips.</p>",
                    "fig_12_11",
                ),
            ],
        },
        13: {
            "part": "Part IV: Miscellaneous Topics",
            "title": "13. Gallery of Reproducible Examples",
            "intro": (
                "Reproducing the four published case studies from Chapter 13 of <em>Data Integration, Manipulation "
                "and Visualization of Phylogenetic Trees</em> plus a phylogeographic circular-map showcase in "
                "<code>ggtree-py</code>—spanning HPV58 sequence distances, discrete bootstrap symbols, groupOTU "
                "circular clade highlights, BioNJ genome locus structures, and an inward circular SARS-CoV-2 "
                "phylogeny wrapped around a NearsidePerspective map of Europe."
            ),
            "sections": [
                (
                    "hpv58-distance",
                    "13.1 Visualizing Pairwise Nucleotide Sequence Distance with Phylogenetic Tree",
                    "<p>Pairs the HPV58 complete-genome phylogeny with nested monophyletic/paraphyletic clade annotations "
                    "(<code>geom_cladelab</code> and <code>geom_strip</code>), internal support markers, and an adjacent "
                    "<code>Sequence Distance</code> facet panel plotting pairwise Hamming differences (%) via "
                    "<code>geom_point()</code> and <code>geom_path()</code>.</p>",
                    "fig_13_1",
                ),
                (
                    "bootstrap-points",
                    "13.2 Displaying Different Symbolic Points for Bootstrap Values",
                    "<p>Parses <code>text_RMI_tree</code> via <code>read_newick(..., node_label='support')</code>, right-ladderizes "
                    "the tree, bins internal support values with <code>cut(support, c(0, 700, 900, 1000))</code>, and encodes "
                    "bootstrap intervals as white, grey, and black <code>shape=21</code> circles with an inset legend.</p>",
                    "fig_13_2",
                ),
                (
                    "group-highlights",
                    "13.3 Highlighting Different Groups",
                    "<p>Partitions avian (<code>^ch</code>) vs non-chicken lineages using <code>groupOTU()</code>, applies "
                    "node rotations and swaps (<code>flip()</code>/<code>rotate()</code>), overlays four radial "
                    "<code>geom_hilight()</code> sectors extending to radius <code>1.4</code>, and adds bootstrap &gt; 50 "
                    "labels alongside curved subgroup <code>geom_cladelab()</code> annotations.</p>",
                    "fig_13_3",
                ),
                (
                    "genome-locus",
                    "13.4 Phylogenetic Tree with Genome Locus Structure",
                    "<p>Reconstructs a <code>bionj()</code> tree from pairwise Jaccard gene-content distances across "
                    "<code>example_genes</code> and pairs it cleanly via <code>geom_facet(..., geom=geom_motif, on='genE', "
                    "label='gene', align='left')</code> with Brewer <code>Set3</code> fills.</p>",
                    "fig_13_4",
                ),
                (
                    "circular-phylogeography",
                    "13.5 Inward Circular Phylogeny Wrapped Around a Geographic Map",
                    "<p>Re-implements Figure 1 of Potter et al. (2026, <a href=\"https://doi.org/10.64898/2026.09.20.752947\" "
                    "target=\"_blank\" rel=\"noopener noreferrer\"><em>baltic</em></a>; SARS-CoV-2 lineage B.1.620 data from "
                    "Dudas et al., 2021, CC-BY) purely in <code>ggtree-py</code>: combines <code>ggtree(..., "
                    "layout='inward_circular', open_angle=21.0, xlim=51.92)</code> and <code>rotate_tree(..., 102.3)</code> "
                    "with compound NearsidePerspective Europe map polygons (<code>geom_polygon</code> with <code>subgroup</code> "
                    "holes), 20 concentric dotted mutation rings, 77 shouldered tip-to-map <code>geom_path()</code> connectors, "
                    "size-tiered sampling locations, and white-haloed country legends.</p>",
                    "fig_13_5",
                ),
            ],
        },
        14: {
            "part": "Appendix A: Frequently Asked Questions",
            "title": "Appendix A. Frequently Asked Questions",
            "intro": (
                "All 16 practical visual solutions adapted from Appendix A of "
                "<em>Data Integration, Manipulation and Visualization of Phylogenetic Trees</em>—covering tip label clipping, "
                "plotmath/HTML rich text, label repulsion, custom branch colors/linetypes, axis breaks, and margin trimming."
            ),
            "sections": [
                (
                    "faq-truncated-tip",
                    "A.4.1 Tip Label Truncated",
                    "<p>Prevent long tip names from clipping at panel edges by widening limits with <code>xlim()</code> or "
                    "disabling clipping via <code>coord_cartesian(clip='off')</code> with expanded right <code>plot_margin</code>.</p>",
                    "fig_A_1",
                ),
                (
                    "faq-modify-labels",
                    "A.4.2 Modify (Tip) Labels",
                    "<p>Substitute display tip labels cleanly using <code>rename_taxa()</code> or external metadata joins "
                    "via <code>%</code> paired with <code>geom_tiplab(aes(label=...))</code>.</p>",
                    "fig_A_2",
                ),
                (
                    "faq-format-labels",
                    "A.4.3 Formatting (Tip) Labels (Plotmath & ggtext)",
                    "<p>Render mixed italic/bold typography via R-style plotmath expressions (<code>parse=True</code>) "
                    "or HTML/Markdown rich text labels via <code>geom_richtext(..., label_color=NA)</code>.</p>",
                    "fig_A_3",
                ),
                (
                    "faq-repel-labels",
                    "A.4.4 Avoid Overlapping Text Labels (ggrepel)",
                    "<p>Use <code>geom_label_repel()</code> or <code>geom_text_repel()</code> to repel dense bootstrap "
                    "annotations with leader segments and viridis fill scales.</p>",
                    "fig_A_4",
                ),
                (
                    "faq-newick-bootstrap",
                    "A.4.5 Bootstrap Values from Newick Format",
                    "<p>Filter numeric support values embedded inside Newick internal node strings using "
                    "<code>subset='~is_na(as_numeric(label)) & (as_numeric(label) &gt; 80)'</code>.</p>",
                    "fig_A_5",
                ),
                (
                    "faq-plot-phylo",
                    "A.5.1 Plot the Same Tree as plot.phylo()",
                    "<p>Compare non-ladderized <code>plot_phylo(x)</code> and <code>ggtree(x, ladderize=False)</code> "
                    "against default ladderized <code>ggtree(x)</code> output.</p>",
                    "fig_A_6",
                ),
                (
                    "faq-rotate-constr",
                    "A.5.2 Specifying the Order of Tips (rotateConstr)",
                    "<p>Enforce a desired bottom-to-top tip ordering with <code>rotateConstr()</code> and preserve it "
                    "during rendering via <code>ladderize=False</code>.</p>",
                    "fig_A_7",
                ),
                (
                    "faq-shrink-branch",
                    "A.5.3 Shrink Outlier Long Branch (scale_x_break)",
                    "<p>Handle extreme outgroup branch lengths either by compressing coordinates in <code>p.data</code> "
                    "or by introducing an axis gap via <code>scale_x_break([0.03, 0.09])</code>.</p>",
                    "fig_A_8",
                ),
                (
                    "faq-bind-tip",
                    "A.5.4 Attach a New Tip to a Tree (bind_tip)",
                    "<p>Insert a new taxon onto a chosen branch with <code>bind_tip()</code>, distinguish its dashed edge "
                    "via <code>scale_linetype_manual()</code>, and overlay attachment uncertainty with <code>geom_errorbarh()</code>.</p>",
                    "fig_A_9",
                ),
                (
                    "faq-arbitrary-style",
                    "A.5.5 Arbitrarily Colored & Styled Branches",
                    "<p>Bind literal per-node color strings and numeric/named linetypes directly via identity mapping "
                    "<code>aes(colour='I(colour)', linetype='I(lty)')</code> without generating extra legends.</p>",
                    "fig_A_10",
                ),
                (
                    "faq-point-on-branch",
                    "A.5.6 Add an Arbitrary Point on a Branch",
                    "<p>Place markers along branches by offsetting <code>x</code> by an absolute constant or proportionally "
                    "using <code>x - branch_length * frac</code> in <code>geom_nodepoint()</code>.</p>",
                    "fig_A_11",
                ),
                (
                    "faq-facet-x-titles",
                    "A.6 Different X-Axis Labels for Facet Panels",
                    "<p>Pass a <code>.panel</code>-keyed DataFrame to <code>geom_text()</code> with negative <code>y</code>, "
                    "<code>coord_cartesian(clip='off')</code>, and increased bottom margin to draw per-facet X-axis titles.</p>",
                    "fig_A_12",
                ),
                (
                    "faq-layer-order",
                    "A.7 Plot Something Behind the Phylogeny",
                    "<p>Move clade highlights behind tree branches either by reversing <code>p.layers</code> or by "
                    "building from <code>ggplot(x) + geom_hilight(...) + geom_tree()</code>.</p>",
                    "fig_A_13",
                ),
                (
                    "faq-circular-center",
                    "A.8 Enlarge Center Space in Circular/Fan Tree",
                    "<p>Open central radial whitespace in circular layouts using negative lower <code>xlim(-10, NA)</code> "
                    "or by adding an extended <code>geom_rootedge(5)</code>.</p>",
                    "fig_A_14",
                ),
                (
                    "faq-backward-time",
                    "A.9 Most Distant Tip as Origin of Timescale (revts)",
                    "<p>Transform forward root-to-tip branch coordinates to backward time before present with "
                    "<code>revts(p) + scale_x_continuous(labels=abs)</code>.</p>",
                    "fig_A_15",
                ),
                (
                    "faq-trim-space",
                    "A.10 Remove Blank Margins (magick / image_trim)",
                    "<p>Render circular graphics via <code>ggsave()</code>, auto-crop transparent margins using "
                    "<code>image_read()</code> + <code>image_trim()</code>, and re-wrap with <code>image_ggplot()</code>.</p>",
                    "fig_A_16",
                ),
            ],
        },
    }


def render_page_shell(
    filename: str,
    page_title: str,
    part_kicker: str,
    main_html: str,
    toc_items: List[Tuple[str, str, bool]],
    is_gallery: bool = False,
) -> str:
    """Wrap page content inside the 3-column treedata-book chrome."""
    sb_blocks: List[str] = []
    for part_name, links in NAV_SECTIONS:
        sb_blocks.append(f'<div class="nav-part">{html.escape(part_name)}</div><ul class="nav-list">')
        for href, num, label in links:
            act = " active" if href == filename else ""
            num_span = f'<span class="nav-num">{html.escape(num)}</span>' if num else ""
            sb_blocks.append(f'<li><a class="nav-link{act}" href="{href}">{num_span}{html.escape(label)}</a></li>')
        sb_blocks.append("</ul>")
    sidebar_nav = "\n".join(sb_blocks)

    # Prev / Next links
    idx = next((i for i, (fn, _) in enumerate(ORDERED_PAGES) if fn == filename), -1)
    prev_link = ""
    next_link = ""
    if idx > 0:
        phref, ptitle = ORDERED_PAGES[idx - 1]
        prev_link = f'<a class="pager-link" href="{phref}"><span class="pager-dir">&larr; Previous</span><span class="pager-title">{html.escape(ptitle)}</span></a>'
    if 0 <= idx < len(ORDERED_PAGES) - 1:
        nhref, ntitle = ORDERED_PAGES[idx + 1]
        next_link = f'<a class="pager-link pager-next" href="{nhref}"><span class="pager-dir">Next &rarr;</span><span class="pager-title">{html.escape(ntitle)}</span></a>'
    pager_html = f'<nav class="chapter-pager" aria-label="Chapter Navigation">{prev_link}{next_link}</nav>'

    # Right TOC
    if toc_items:
        toc_lis = "".join(
            f'<li><a class="{"toc-fig-link" if is_sub else ""}" href="#{html.escape(anc)}">{html.escape(lbl)}</a></li>'
            for anc, lbl, is_sub in toc_items
        )
        toc_rail = (
            '<aside class="book-toc" aria-label="On this page">\n'
            '  <div class="toc-heading">On This Page</div>\n'
            f'  <ul class="toc-list">{toc_lis}</ul>\n'
            '</aside>'
        )
    else:
        toc_rail = ""

    body_cls = ' class="gallery-page"' if is_gallery else ""

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{html.escape(page_title)} | Data Integration, Manipulation and Visualization of Phylogenetic Trees (ggtree-py)</title>
  <link rel="stylesheet" href="assets/style.css"/>
</head>
<body{body_cls}>
  <header class="topbar">
    <div class="topbar-left">
      <button type="button" class="sidebar-toggle" id="sidebar-toggle-btn" aria-label="Toggle Menu">&#9776;</button>
      <a class="topbar-brand" href="index.html">
        Data Integration, Manipulation and Visualization of Phylogenetic Trees
        <span class="topbar-sub">(ggtree-py Edition)</span>
      </a>
    </div>
    <div class="topbar-actions">
      <a class="tool-btn" href="gallery.html">Gallery Index</a>
      <button type="button" class="tool-btn" id="toggle-all-code-btn">Expand All Code</button>
      <button type="button" class="tool-btn" id="theme-toggle-btn">Theme: Light</button>
    </div>
  </header>

  <div class="book-shell">
    <nav class="book-sidebar" id="book-sidebar" aria-label="Book Chapters">
      <div class="sidebar-search-wrap">
        <input type="search" class="sidebar-search" id="book-search-input" placeholder="Search chapters, figures, APIs..." autocomplete="off"/>
        <div class="search-results" id="book-search-results"></div>
      </div>
      {sidebar_nav}
    </nav>

    <main class="book-main">
      <article class="book-article">
        <div class="part-kicker">{html.escape(part_kicker)}</div>
        {main_html}
        {pager_html}
      </article>
    </main>

    {toc_rail}
  </div>

  <script src="assets/search_data.js"></script>
  <script src="assets/book.js"></script>
</body>
</html>
"""


def build_index_page(figs: List[Dict[str, Any]]) -> str:
    featured_ids = ["fig_1_2", "fig_7_3", "fig_13_4", "fig_10_2", "fig_13_5"]
    by_id = {f["id"]: f for f in figs}
    featured_html = "".join(render_figure_card(by_id[fid]) for fid in featured_ids if fid in by_id)

    quick_code = """from ggtree import read_beast, system_file, ggtree, aes, geom_range, geom_tiplab, theme_tree2, hexpand

beast = read_beast(system_file("extdata", "MCC_FluA_H3.tree"))
p = (
    ggtree(beast, aes(color="rate"))
    + geom_range(range="height_0.95_HPD", color="red", alpha=0.55)
    + geom_tiplab(size=2.3)
    + hexpand(0.28)
    + theme_tree2()
)
p.save("flu_h3_tree.svg", width=8, height=6)"""

    py_ver = html.escape(gg.__version__)
    r_ver = html.escape(getattr(gg, "__r_ggtree_version__", "4.3.2"))
    main_html = f"""
<h1 class="chapter-title">Data Integration, Manipulation and Visualization of Phylogenetic Trees</h1>
<p>Welcome to the complete Python edition of Guangchuang Yu's <a href="https://yulab-smu.top/treedata-book/" target="_blank" rel="noopener noreferrer"><em>treedata-book</em></a>, powered by <strong>ggtree-py</strong> (v{py_ver}; <a href="https://github.com/zhanxw/ggtree-py" target="_blank" rel="noopener noreferrer">GitHub</a> · <a href="https://pypi.org/project/ggtree-py/" target="_blank" rel="noopener noreferrer">PyPI</a>), a Python port of the R/Bioconductor <a href="https://github.com/YuLab-SMU/ggtree" target="_blank" rel="noopener noreferrer"><code>ggtree</code></a> package (v{r_ver}). This interactive online book reproduces all major workflows across Newick/Nexus, BEAST, RAxML, PAML CodeML, EPA/pplacer, Nextstrain Auspice JSON, <code>gheatmap</code>, <code>msaplot</code>, <code>geom_facet</code>, <code>geom_motif</code>, vector PhyloPic silhouettes, circular <code>geom_fruit</code> rings, and hover-interactive SVG tooltips—running purely in Python with zero external runtime dependencies beyond NumPy.</p>

<div class="callout">
  <strong>Interactive Code &amp; Visual Gallery:</strong> Every figure card in Chapters 1–13 and Appendix A pairs a vector plot directly with its exact self-contained Python code (collapsed by default right under the caption). Use <strong>Expand All Code</strong> in the top bar or browse all {len(figs)} reproducible examples at once in the <a href="gallery.html"><strong>All Figures Gallery &amp; Master Index</strong></a>.
</div>

<h2 id="book-structure">Structure of the Book</h2>
<div class="parts-grid">
  <div class="part-card">
    <h3>Part I: Tree Data I/O &amp; Manipulation</h3>
    <p>Parsing Newick, BEAST, RAxML, CodeML, Nextstrain Auspice JSON, and <code>.jplace</code> data structures; joining trait metadata with <code>%</code>; tidy manipulation and tree export.</p>
    <ul>
      <li><a href="chapter1.html">Ch. 1 Importing Tree with Data</a></li>
      <li><a href="chapter2.html">Ch. 2 Manipulating Tree with Data</a></li>
      <li><a href="chapter3.html">Ch. 3 Exporting Trees with Data</a></li>
    </ul>
  </div>
  <div class="part-card">
    <h3>Part II: Visualization &amp; Annotation</h3>
    <p>Phylogram, circular, fan, and unrooted layouts; clade highlights and links; clade exploration; <code>gheatmap</code>, <code>msaplot</code>, <code>geom_motif</code>, and PhyloPic silhouettes.</p>
    <ul>
      <li><a href="chapter4.html">Ch. 4 Tree Visualization</a> &amp; <a href="chapter5.html">Ch. 5 Annotation</a></li>
      <li><a href="chapter6.html">Ch. 6 Visual Exploration</a> &amp; <a href="chapter7.html">Ch. 7 Plot with Data</a></li>
      <li><a href="chapter8.html">Ch. 8 Silhouettes &amp; Sub-plots</a></li>
    </ul>
  </div>
  <div class="part-card">
    <h3>Part III: ggtree Extensions</h3>
    <p>Clustering dendrograms, <code>ggdensitree</code> ensembles, <code>ggdoubletree</code> tanglegrams, <code>ggtreeExtra::geom_fruit</code> radial rings, interactive SVG tooltips, and Patchwork grids.</p>
    <ul>
      <li><a href="chapter9.html">Ch. 9 Other Tree-like Structures</a></li>
      <li><a href="chapter10.html">Ch. 10 ggtreeExtra Circular Rings</a></li>
      <li><a href="chapter11.html">Ch. 11 Extensions</a> &amp; <a href="chapter12.html">Ch. 12 Utilities</a></li>
    </ul>
  </div>
  <div class="part-card">
    <h3>Part IV &amp; Appendices</h3>
    <p>Publication-ready integrative case studies, frequently asked questions, complete API reference, and searchable Master Figure Index.</p>
    <ul>
      <li><a href="chapter13.html">Ch. 13 Gallery of Examples</a></li>
      <li><a href="faq.html">Appendix A: FAQ</a> &amp; <a href="api.html">Appendix B: API</a></li>
      <li><a href="gallery.html">&#9733; Complete Visual Figure Gallery ({len(figs)} Figures)</a></li>
    </ul>
  </div>
</div>

<h2 id="quick-start">Quick Start in Python</h2>
<p>Every snippet across this book uses native Python syntax closely paralleling R's <code>ggplot2</code> + <code>ggtree</code> grammar:</p>
{render_code_snippet("Quick Example (Python)", quick_code)}

<h2 id="highlights">Selected Book Highlights</h2>
{featured_html}
"""
    toc = [
        ("book-structure", "Structure of the Book", False),
        ("quick-start", "Quick Start in Python", False),
        ("highlights", "Selected Book Highlights", False),
    ]
    return render_page_shell("index.html", "Welcome", "Welcome · Preface", main_html, toc)


def build_chapter_page(chap_num: int, spec: Dict[str, Any], figs_by_id: Dict[str, Dict[str, Any]]) -> Tuple[str, str, List[Dict[str, str]]]:
    fname = "faq.html" if chap_num == 14 else f"chapter{chap_num}.html"
    parts_html = [f'<h1 class="chapter-title">{html.escape(spec["title"])}</h1>', f'<p>{spec["intro"]}</p>']
    toc: List[Tuple[str, str, bool]] = []
    search_hits: List[Dict[str, str]] = [
        {
            "title": spec["title"],
            "section": spec["title"],
            "context": spec["part"],
            "href": fname,
            "keywords": spec["intro"],
        }
    ]

    for sec_id, sec_title, sec_body, fig_spec in spec["sections"]:
        parts_html.append(f'<h2 id="{sec_id}">{html.escape(sec_title)}</h2>')
        parts_html.append(sec_body)
        toc.append((sec_id, sec_title, False))
        search_hits.append(
            {
                "title": sec_title,
                "section": spec["title"],
                "context": spec["title"],
                "href": f"{fname}#{sec_id}",
                "keywords": sec_body,
            }
        )
        fig_ids = (
            list(fig_spec)
            if isinstance(fig_spec, (list, tuple))
            else ([fig_spec] if fig_spec else [])
        )
        for fig_id in fig_ids:
            if fig_id and fig_id in figs_by_id:
                fobj = figs_by_id[fig_id]
                use_inline = bool(fobj.get("interactive"))
                parts_html.append(render_figure_card(fobj, inline_svg=use_inline, gallery_mode=False))
                fanc = f"fig-{fobj['num'].replace('.', '-')}"
                toc.append((fanc, f"Fig. {fobj['num']}: {fobj['title']}", True))
                search_hits.append(
                    {
                        "title": f"Figure {fobj['num']}: {fobj['title']}",
                        "section": sec_title,
                        "context": f"{spec['title']} · {sec_title}",
                        "href": f"{fname}#{fanc}",
                        "keywords": f"{fobj['caption']} {' '.join(fobj['apis'])}",
                    }
                )

    html_str = render_page_shell(fname, spec["title"], spec["part"], "\n".join(parts_html), toc)
    return fname, html_str, search_hits


def build_api_page(figs: List[Dict[str, Any]]) -> str:
    # Build mapping api_token -> list of figures showcasing it
    api_examples: Dict[str, List[Dict[str, Any]]] = {}
    for f in figs:
        for tok in f["apis"]:
            clean_tok = tok.split("(")[0].split("=")[0].strip()
            api_examples.setdefault(clean_tok, []).append(f)

    groups: List[Tuple[str, List[Tuple[str, str, str]]]] = [
        (
            "Tree Parsers, Writers & Converters",
            [
                ("read_tree", "Read Newick or Nexus files / strings into Phylo or MultiPhylo", "tree.py"),
                ("read_newick", "Parse Newick strings or files and optionally cast internal node labels (e.g. support) to numeric TreeData columns", "tree.py"),
                ("nj / bionj", "Reconstruct Neighbor-Joining and BioNJ distance phylogenies (ape::nj / ape::bionj)", "tree.py"),
                ("read_beast", "Parse BEAST Nexus trees with [ &... ] node metadata and HPD intervals", "tree.py"),
                ("read_codeml / read_codeml_mlc", "Parse PAML CodeML rst & mlc selection/ancestral substitution files", "tree.py"),
                ("read_raxml", "Parse RAxML bipartitions & bootstrap support trees", "tree.py"),
                ("read_jplace", "Parse EPA/pplacer JSON placements with nplace read counts", "tree.py"),
                ("read_auspice_json / read_nextstrain_json", "Parse Nextstrain Auspice v1/v2 JSON trees with divergence/date branch lengths, node_attrs, branch_attrs, and geo metadata", "tree.py"),
                ("read_nhx / read_fasta", "Parse NHX extended trees and FASTA sequence alignments", "tree.py"),
                ("write_tree / write_beast / write_jtree / read_jtree", "Serialize Phylo or TreeData across Newick, BEAST NEXUS, and jtree JSON", "tree.py"),
                ("drop_tip / keep_tip / merge_tree", "Prune taxa preserving annotations, or merge compatible TreeData objects", "tree.py"),
                ("as_tibble / as_phylo / as_treedata", "Convert between Phylo, TreeData, and tidy TblTree data frames", "tree.py"),
            ],
        ),
        (
            "Tidy Manipulation & Clade Operations",
            [
                ("MRCA / child / parent / offspring / ancestor / sibling", "Resolve ancestral, descendant, and sister node IDs cleanly", "tidytree.py"),
                ("groupClade / groupOTU", "Partition clade subtrees or trace OTU backbone lineages", "tidytree.py"),
                ("tree_subset / td_filter / td_mutate / td_unnest", "Extract local neighborhoods and transform node annotations lazily", "tidytree.py"),
                ("collapse / expand / scaleClade", "Collapse subtrees into wedges, restore collapsed nodes, scale vertical span", "manipulate.py"),
                ("rotate / flip / open_tree / rotate_tree / layout_rectangular / viewClade / gzoom", "Reorder sister clades, adjust circular sectors, switch circular/rectangular layout, zoom subtrees", "manipulate.py"),
            ],
        ),
        (
            "Layouts, Geoms, Scales & Themes",
            [
                ("ggtree / aes / % (%<+%)", "Create layered tree canvas, map columns, attach external DataFrame metadata", "plot.py"),
                ("geom_tree / geom_tiplab / geom_nodelab / geom_tippoint / geom_nodepoint", "Render core branches, markers, and formatted/plotmath labels", "geoms.py"),
                ("geom_hilight / geom_cladelab / geom_strip / geom_balance / geom_taxalink / geom_range", "Annotate clades, bars, evolutionary balance, arcs, and HPD error ranges", "geoms.py"),
                ("geom_star / geom_motif / geom_phylopic / geom_image", "Render ggstar polygons/spikes, gene-arrow operons via on=, and built-in silhouettes", "geoms.py"),
                ("geom_point_interactive / geom_tiplab_interactive / ggtree_set_interactive", "Emit interactive SVG hover tooltips cleanly with coordinate transforms", "geoms.py"),
                ("scale_color_gradientn / scale_fill_viridis_c / scale_fill_discrete / scale_shape_manual / scale_starshape_manual / scale_alpha_continuous / scale_x_reverse / new_scale_fill", "Custom continuous/discrete palettes, shape/starshape/alpha mapping, axis reversal, dual scales", "themes_scales.py"),
                ("theme_tree / theme_tree2 / theme_dendrogram / theme_bw / revts / hexpand / xlim_tree", "Control coordinate axes, time reversal, and responsive canvas padding", "themes_scales.py"),
            ],
        ),
        (
            "Composite Facets, Circular Rings & Multiplot",
            [
                ("gheatmap / msaplot", "Attach discrete/continuous heatmaps and sequence alignments directly to tips", "compose.py"),
                ("geom_facet / facet_plot / facet_widths", "Compose multi-panel rectangular bar, boxplot, line, and interval facets", "compose.py"),
                ("geom_fruit", "Ring boxplot, star/symbol, tile heatmap, and barplot data onto fan/circular/rectangular trees", "compose.py"),
                ("nodepie / nodebar / inset", "Overlay micro pie/bar charts on internal nodes or branches", "compose.py"),
                ("hclust / ggdensitree / as_tanglegram / ggdoubletree", "Visualize clustering dendrograms, tree clouds, and co-phylogenies", "compose.py"),
                ("plot_list / multiplot / | / /", "Assemble multi-panel publication grids with panel tags and widths", "compose.py"),
            ],
        ),
    ]

    sections_html: List[str] = [
        '<h1 class="chapter-title">Appendix B. ggtree-py API Reference</h1>',
        "<p>Quick reference table mapping every public Python function in <code>ggtree</code> to its module and reproducible book figure examples.</p>",
    ]
    toc: List[Tuple[str, str, bool]] = []

    for gidx, (gname, rows) in enumerate(groups, start=1):
        gid = f"api-grp-{gidx}"
        toc.append((gid, gname, False))
        sections_html.append(f'<h2 id="{gid}">{html.escape(gname)}</h2>')
        sections_html.append('<table class="book-table"><thead><tr><th>Function(s)</th><th>Description</th><th>Module</th><th>Book Examples</th></tr></thead><tbody>')
        for fn_names, desc, mod_name in rows:
            # Find matching figures for any slash-separated symbol
            matched: List[Dict[str, Any]] = []
            seen_ids = set()
            for part in fn_names.split("/"):
                key = part.strip()
                for f in api_examples.get(key, []):
                    if f["id"] not in seen_ids:
                        seen_ids.add(f["id"])
                        matched.append(f)
            link_parts = []
            for f in matched[:5]:
                ch_href = "faq.html" if f["chapter"] == 14 else f"chapter{f['chapter']}.html"
                anchor = f"fig-{f['num'].replace('.', '-')}"
                link_parts.append(f'<a href="{ch_href}#{anchor}">Fig {html.escape(f["num"])}</a>')
            links_str = ", ".join(link_parts) or "&mdash;"
            sections_html.append(
                f"<tr><td><code>{html.escape(fn_names)}</code></td><td>{html.escape(desc)}</td><td><code>ggtree/{html.escape(mod_name)}</code></td><td>{links_str}</td></tr>"
            )
        sections_html.append("</tbody></table>")

    return render_page_shell("api.html", "Appendix B: API Reference", "Appendix B", "\n".join(sections_html), toc)


def build_gallery_page(figs: List[Dict[str, Any]]) -> str:
    # Part filter pills + Chapter filter pills
    part_pills = [
        ("all", "All Parts"),
        ("part1", "Part I (Ch. 1–3)"),
        ("part2", "Part II (Ch. 4–8)"),
        ("part3", "Part III (Ch. 9–12)"),
        ("part4", "Part IV (Ch. 13)"),
        ("appendix", "Appendix (FAQ)"),
    ]
    part_btns = "".join(
        f'<button type="button" class="filter-pill{" active" if k == "all" else ""}" data-filter-part="{k}">{html.escape(lbl)}</button>'
        for k, lbl in part_pills
    )
    chap_btns = '<button type="button" class="filter-pill active" data-filter-chapter="all">All Ch.</button>' + "".join(
        f'<button type="button" class="filter-pill" data-filter-chapter="{c}">{"FAQ" if c == 14 else f"Ch.{c}"}</button>'
        for c in range(1, 15)
    )

    cards_html = "\n".join(render_figure_card(f, inline_svg=False, gallery_mode=True) for f in figs)

    # Master Index Table
    rows_html: List[str] = []
    for f in figs:
        c = f["chapter"]
        p_slug = "part1" if c in (1, 2, 3) else ("part2" if c in (4, 5, 6, 7, 8) else ("part3" if c in (9, 10, 11, 12) else ("part4" if c == 13 else "appendix")))
        anchor = f"fig-{f['num'].replace('.', '-')}"
        ch_href = f"faq.html#{anchor}" if c == 14 else f"chapter{c}.html#{anchor}"
        api_tags = " ".join(f'<span class="api-pill">{html.escape(a)}</span>' for a in f["apis"][:5])
        sblob = f"Figure {f['num']} {f['title']} {f['section']} {f['caption']} {' '.join(f['apis'])}"
        rows_html.append(
            f'<tr data-part="{p_slug}" data-chapter="{c}" data-search="{html.escape(sblob, quote=True)}">'
            f'<td><a href="{ch_href}"><strong>Fig {html.escape(f["num"])}</strong></a></td>'
            f'<td>{"FAQ" if c == 14 else f"Ch. {c}"}</td>'
            f'<td>{html.escape(f["section"])}</td>'
            f'<td><a href="{ch_href}">{html.escape(f["title"])}</a></td>'
            f'<td>{api_tags}</td>'
            f'</tr>'
        )

    main_html = f"""
<h1 class="chapter-title">Gallery &amp; Master Index of All Figure Examples</h1>
<p>Browse all <strong>{len(figs)} reproducible phylogenetic figures</strong> across Chapters 1–13 and Appendix A. Filter by book Part, Chapter, or API symbol below, inspect crisp vector renderings, expand any figure's attached reproducible Python snippet inline, or jump straight to its detailed narrative section.</p>

<div class="gallery-controls">
  <div class="filter-row">
    <strong style="font-size:13px;">Part:</strong> {part_btns}
  </div>
  <div class="filter-row">
    <strong style="font-size:13px;">Chapter:</strong> {chap_btns}
  </div>
  <div class="filter-row">
    <input type="search" id="gallery-search-input" class="gallery-search" placeholder="Filter by keyword, layout, geom, or parser (e.g., codeml, geom_fruit, motif, phylopic)..."/>
    <span id="gallery-visible-count" style="font-size:13px; color:var(--text-muted); font-weight:600;">Showing {len(figs)} of {len(figs)} figures</span>
  </div>
</div>

<h2 id="visual-gallery">Visual Figure Gallery</h2>
<div class="gallery-grid" id="gallery-grid">
{cards_html}
</div>

<h2 id="master-index">Master Index Table of All Book Figures</h2>
<table class="book-table" id="gallery-index-table">
  <thead>
    <tr>
      <th>Figure</th>
      <th>Chapter</th>
      <th>Book Section</th>
      <th>Title (Link to Section)</th>
      <th>Key ggtree-py APIs</th>
    </tr>
  </thead>
  <tbody>
    {"".join(rows_html)}
  </tbody>
</table>
"""
    toc = [
        ("visual-gallery", "Visual Figure Gallery", False),
        ("master-index", "Master Index Table", False),
    ]
    return render_page_shell("gallery.html", "All Figures Gallery & Master Index", "Gallery & Complete Index", main_html, toc, is_gallery=True)


def build_all() -> None:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing manifest: {MANIFEST_PATH}. Run generate_book_figures.py first.")
    figs: List[Dict[str, Any]] = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    figs_by_id = {f["id"]: f for f in figs}
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    search_index: List[Dict[str, str]] = [
        {
            "title": "Welcome & Book Overview",
            "section": "Preface",
            "context": "Home · Structure & Quick Start",
            "href": "index.html",
            "keywords": "ggtree-py install quickstart treedata-book parts overview",
        },
        {
            "title": f"All Figures Gallery & Master Index ({len(figs)} figures)",
            "section": "Gallery",
            "context": "Visual Gallery · Master Table",
            "href": "gallery.html",
            "keywords": "gallery index all figures examples filter search",
        },
        {
            "title": "Appendix B: ggtree-py API Reference",
            "section": "API",
            "context": "Complete Function Cross-Reference",
            "href": "api.html",
            "keywords": "read_tree read_beast read_codeml read_raxml read_auspice_json read_nextstrain_json auspice nextstrain gheatmap msaplot geom_fruit geom_motif geom_phylopic",
        },
    ]

    # Write chapters 1..13 and faq (14)
    chap_specs = build_chapter_spec()
    for cnum in sorted(chap_specs.keys()):
        fname, c_html, ch_hits = build_chapter_page(cnum, chap_specs[cnum], figs_by_id)
        (DOCS_DIR / fname).write_text(c_html, encoding="utf-8")
        search_index.extend(ch_hits)
        print(f"Built {fname}")

    # Write index.html, api.html, gallery.html
    (DOCS_DIR / "index.html").write_text(build_index_page(figs), encoding="utf-8")
    (DOCS_DIR / "api.html").write_text(build_api_page(figs), encoding="utf-8")
    (DOCS_DIR / "gallery.html").write_text(build_gallery_page(figs), encoding="utf-8")

    # Write client-side search index (both JSON and inline JS variable so file:// works cleanly)
    (ASSETS_DIR / "search_index.json").write_text(json.dumps(search_index, indent=2), encoding="utf-8")
    (ASSETS_DIR / "search_data.js").write_text(
        f"window.BOOK_SEARCH_INDEX = {json.dumps(search_index)};\n",
        encoding="utf-8",
    )
    print(f"Built index.html, api.html, gallery.html, search_index.json ({len(search_index)} entries)")


if __name__ == "__main__":
    build_all()

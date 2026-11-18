# Data Integration, Manipulation and Visualization of Phylogenetic Trees (*ggtree-py* Edition)

🌐 **Read the Live Book Online:** [https://zhanxw.github.io/ggtree-py-book/](https://zhanxw.github.io/ggtree-py-book/)
🖼️ **Visual Gallery & Master Index (112 Figures):** [https://zhanxw.github.io/ggtree-py-book/gallery.html](https://zhanxw.github.io/ggtree-py-book/gallery.html)

---

This repository hosts the complete Python edition of Guangchuang Yu's [*treedata-book*](https://yulab-smu.top/treedata-book/), powered by [**ggtree-py**](https://github.com/zhanxw/ggtree-py) (`v0.1.4` on [PyPI](https://pypi.org/project/ggtree-py/)), a Python port of the R/Bioconductor [`ggtree`](https://github.com/YuLab-SMU/ggtree) package (`v4.3.2`).

## Contents

- **Preface & Overview** (`index.html`)
- **Part I — Tree Data Input, Output and Manipulation:** Chapters 1–3 (`read_tree`, `read_beast`, `read_codeml`, `read_raxml`, `read_jplace`, `tidytree` verbs, `write_beast`, `write_jtree`)
- **Part II — Tree Visualization, Interpretation and Annotation:** Chapters 4–8 (phylogenetic layouts, `ggdensitree`, `geom_cladelab`, `geom_hilight`, `geom_taxalink`, `geom_range`, `gheatmap`, `msaplot`, `geom_facet`, PhyloPic silhouettes, insets, Phylomoji)
- **Part III — `ggtree` Extensions:** Chapters 9–12 (`phylo4d`, `hclust`, `geom_fruit` & `geom_star` circular rings, `ggdiffclade`, `ggsplitnet`, interactive SVG tooltips, utilities)
- **Part IV — Miscellaneous Topics:** Chapter 13 (5 integrative publication case studies)
- **Appendices & Gallery:** Appendix A (16 FAQs), Appendix B (`ggtree-py` API Reference), and the searchable Master Gallery & Index of all **112 reproducible figures** (with collapsible Python code under every figure).

## Preview & Rebuild Locally

Preview the static HTML site locally:

```bash
python3 -m http.server 8000
```

Verify links, figure assets, collapsed code blocks, and HTML structure:

```bash
python3 verify_book.py
```

Rebuild the HTML pages from `book_chapters/` and `figures/book/manifest.json` (requires `ggtree-py` installed):

```bash
python3 build_book.py
python3 verify_book.py
```

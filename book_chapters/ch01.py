"""Figure generators for Chapter 1: Importing Tree with Data."""

from __future__ import annotations

from ggtree import *
from .registry import PART_I, register_figure


@register_figure(
    fig_id="fig_1_1",
    num="1.1",
    chapter=1,
    part=PART_I,
    section="1.2 Understanding Phylogenetic Tree Structure",
    title="Phylogenetic tree components: tips, internal nodes, root, and branch lengths",
    caption=(
        "A rooted phylogeny showing tip nodes (green), internal nodes (blue), the root node (red), "
        "numeric branch lengths displayed along edges, and an evolutionary distance scale bar."
    ),
    apis=["read_tree", "ggtree", "geom_tippoint", "geom_nodepoint", "geom_rootpoint", "geom_tiplab", "geom_treescale"],
    size=(720, 480),
)
def _fig_1_1():
    nwk = (
        "(((virus1:0.28,virus2:0.52):0.34,((virus3:0.61,virus4:0.19):0.41,"
        "(virus5:0.47,virus6:0.33):0.25):0.22):0.38,"
        "((virus7:0.54,virus8:0.29):0.46,(virus9:0.31,virus10:0.64):0.18):0.44);"
    )
    tr = read_tree(text=nwk)
    p = (
        ggtree(tr)
        + geom_text(aes(x="branch", label="branch.length"), color="#6B7280", vjust=-0.45, size=2.9)
        + geom_tippoint(color="#00BA38", size=3.2)
        + geom_nodepoint(color="#619CFF", size=3.2)
        + geom_rootpoint(color="#F8766D", size=3.4)
        + geom_tiplab(offset=0.04, size=3.8)
        + geom_treescale(x=0.1, y=0.6)
        + hexpand(0.14)
    )
    return p


@register_figure(
    fig_id="fig_1_2",
    num="1.2",
    chapter=1,
    part=PART_I,
    section="1.2 Understanding Phylogenetic Tree Structure",
    title="Random Newick tree with aligned tip labels and branch-length labels",
    caption=(
        "Phylogeny parsed directly from an inline Newick text string with thick branches, "
        "dotted alignment guides via geom_tiplab(align=True), and boxed branch-length labels."
    ),
    apis=["read_tree", "ggtree", "geom_tiplab", "geom_label", "aes"],
    size=(700, 420),
)
def _fig_1_2():
    tr = read_tree(text="((t2:0.04,t1:0.34):0.89,(t5:0.37,(t4:0.03,t3:0.67):0.9):0.59);")
    p = (
        ggtree(tr, size=2)
        + geom_tiplab(align=True, linetype="dotted", linesize=0.5, size=4.2)
        + geom_label(aes(x="branch", label="branch.length"), size=3.4)
        + hexpand(0.12)
    )
    return p


@register_figure(
    fig_id="fig_1_3",
    num="1.3",
    chapter=1,
    part=PART_I,
    section="1.3 Importing Tree with treeio",
    title="Overview of treeio data integration and conversion workflow",
    caption=(
        "Workflow architecture illustrating how treeio parses diverse evolutionary formats into "
        "unified Phylo and TreeData structures, integrates external tables via tidytree, and passes data to ggtree."
    ),
    apis=["treeio_diagram", "TreeDiagram"],
    size=(860, 480),
)
def _fig_1_3():
    return treeio_diagram()


@register_figure(
    fig_id="fig_1_4",
    num="1.4",
    chapter=1,
    part=PART_I,
    section="1.4 Extracting Data from Tree Object",
    title="Visualizing jtree amino-acid substitutions stored along branches",
    caption=(
        "Tree imported from jtree format via read_jtree() with reconstructed amino-acid substitution tags "
        "(AA_subs) rendered directly above each internal and terminal branch."
    ),
    apis=["read_jtree", "ggtree", "geom_text", "geom_tiplab", "system_file"],
    size=(780, 520),
)
def _fig_1_4():
    pmltree = read_jtree(system_file("extdata", "TDbook", "pmltree.jtree"))
    p = (
        ggtree(pmltree)
        + geom_text(aes(x="branch", label="AA_subs"), vjust=-0.5, size=2.3)
        + hexpand(0.18)
    )
    return p


@register_figure(
    fig_id="fig_1_5",
    num="1.5",
    chapter=1,
    part=PART_I,
    section="1.5 Importing Nextstrain Auspice JSON Trees",
    title="Nextstrain Auspice v2 Zika phylogeny: divergence vs calendar-year time tree",
    caption=(
        "Zika Nextstrain Auspice v2 JSON imported via read_auspice_json() (and directly via ggtree(path)), "
        "comparing root-to-tip genetic divergence (panel A) with calendar-year time scaling via branch_length='num_date' (panel B) colored by region."
    ),
    apis=["read_auspice_json", "read_nextstrain_json", "ggtree", "plot_list", "theme_tree2", "system_file"],
    size=(960, 500),
)
def _fig_1_5():
    zika_json = system_file("extdata", "nextstrain.json", "minimal_v2.json")
    zika_td = read_auspice_json(zika_json, include_geo=True)
    region_cols = {
        "Southeast Asia": "#1B9E77",
        "Oceania": "#7570B3",
        "South America": "#E7298A",
        "North America": "#D95F02",
    }
    p_div = (
        ggtree(zika_json, aes(color="region"))
        + geom_tippoint(size=2.1)
        + geom_tiplab(size=2.0, offset=0.00018)
        + scale_color_manual(values=region_cols, name="Region")
        + hexpand(0.32)
        + theme_tree2(legend_position=(0.18, 0.84))
        + xlab("Divergence (substitutions / site)")
    )
    p_time = (
        ggtree(zika_td, aes(color="region"), branch_length="num_date")
        + geom_tippoint(size=2.1)
        + geom_tiplab(size=2.0, offset=0.14)
        + scale_color_manual(values=region_cols, name="Region")
        + hexpand(0.30)
        + theme_tree2(legend_position="none")
        + xlab("Calendar Year (num_date)")
    )
    return plot_list(p_div, p_time, ncol=2, tag_levels="A")

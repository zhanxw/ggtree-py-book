"""Figure generators for Chapter 2: Manipulating Tree with Data."""

from __future__ import annotations

from ggtree import *
from .registry import PART_I, register_figure


@register_figure(
    fig_id="fig_2_1",
    num="2.1",
    chapter=2,
    part=PART_I,
    section="2.2 Combining Tree Data via merge_tree()",
    title="Joint distribution of BEAST evolutionary rate vs. CodeML dN/dS, dN, and dS",
    caption=(
        "Correlating BEAST branch substitution rates with CodeML synonymous (dS), non-synonymous (dN), "
        "and dN/dS ratios after combining outputs via merge_tree() and reshaping with gather()."
    ),
    apis=["read_beast", "read_codeml", "merge_tree", "fortify", "gather", "ggplot", "geom_hex", "facet_wrap"],
    size=(860, 380),
)
def _fig_2_1():
    beast_tree = read_beast(system_file("extdata", "MCC_FluA_H3.tree"))
    codeml_tree = read_codeml(
        system_file("extdata", "rst"),
        system_file("extdata", "mlc"),
    )
    merged_tree = merge_tree(beast_tree, codeml_tree)
    raw = fortify(merged_tree)
    recs = [
        r for r in raw.to_records()
        if isinstance(r.get("dN_vs_dS"), (int, float))
        and isinstance(r.get("rate"), (int, float))
        and 0.0 <= float(r["dN_vs_dS"]) <= 1.5
    ]
    df = DataFrame({
        "rate": [float(r["rate"]) for r in recs],
        "dN_vs_dS": [float(r["dN_vs_dS"]) for r in recs],
        "dN": [float(r["dN"]) if r.get("dN") is not None else float("nan") for r in recs],
        "dS": [float(r["dS"]) if r.get("dS") is not None else float("nan") for r in recs],
    })
    df_long = gather(df, "type", "value", "dN_vs_dS", "dN", "dS")
    remap = {"dN_vs_dS": "dN/dS", "dN": "dN", "dS": "dS"}
    df_long["type"] = factor(
        [remap.get(str(v), str(v)) for v in df_long["type"].tolist()],
        levels=["dN/dS", "dN", "dS"],
    )
    p = (
        ggplot(df_long, aes("rate", "value"))
        + geom_hex(bins=22)
        + facet_wrap("~type", scales="free_y")
        + xlab("rate")
        + ylab("")
    )
    return p


@register_figure(
    fig_id="fig_2_2",
    num="2.2",
    chapter=2,
    part=PART_I,
    section="2.2 Joining External Annotations and Rerooting",
    title="Joining tip/node metadata and rerooting a phylogeny with root()",
    caption=(
        "Comparison of a carnivoran tree joined with tip and internal-node annotations before (A) and after (B) "
        "rerooting on Suricata_suricatta via root(..., edgelabel=True), keeping clade labels, posterior support fills, "
        "and tip traits aligned."
    ),
    apis=["read_tree", "read_table", "left_join", "root", "ggtree", "geom_nodelab", "scale_fill_distiller", "plot_list"],
    size=(1020, 540),
)
def _fig_2_2():
    tr_boots = read_tree(system_file("extdata", "TDbook", "tree_boots.nwk"))
    df_tip = read_table(system_file("extdata", "TDbook", "df_tip_data.tsv"), header=True, sep="\t")
    df_inode = read_table(system_file("extdata", "TDbook", "df_inode_data.tsv"), header=True, sep="\t")

    trda = left_join(tr_boots, df_tip, by={"label": "Newick_label"})
    trda = left_join(trda, df_inode, by={"label": "newick_label"})
    trda2 = root(trda, outgroup="Suricata_suricatta", edgelabel=True)

    def _build_panel(td, x_hi: float, show_legend: bool):
        p = (
            ggtree(td)
            + geom_nodelab(aes(x="branch", label="bootstrap"), nudge_y=0.36, hjust=0.5, size=2.7)
            + geom_tippoint(aes(shape="trophic_habit", color="trophic_habit", size="mass_in_kg"))
            + scale_size_continuous(range=(2.0, 5.2))
            + geom_tiplab(offset=0.14, size=2.9)
            + geom_nodelab(aes(label="vernacularName.y", fill="posterior"), geom="label", size=2.6)
            + scale_fill_gradientn(colors=["#EDF8B1", "#7FCDBB", "#2C7FB8"])
            + xlim(-0.1, x_hi)
        )
        if not show_legend:
            p = p + theme(legend_position="none")
        return p

    return plot_list(_build_panel(trda, 4.8, False), _build_panel(trda2, 5.8, True), ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_2_3",
    num="2.3",
    chapter=2,
    part=PART_I,
    section="2.3 Rescaling Tree Branches",
    title="Rescaling branch lengths using CodeML dN and BEAST evolutionary rate",
    caption=(
        "The merged Flu A H3 tree plotted with original divergence times (A), rescaled by synonymous-normalized "
        "non-synonymous substitutions dN (B), and rescaled by BEAST molecular clock rate (C) via rescale_tree()."
    ),
    apis=["merge_tree", "rescale_tree", "ggtree", "theme_tree2", "plot_list"],
    size=(920, 420),
)
def _fig_2_3():
    beast_tree = read_beast(system_file("extdata", "MCC_FluA_H3.tree"))
    codeml_tree = read_codeml(
        system_file("extdata", "rst"),
        system_file("extdata", "mlc"),
    )
    merged_tree = merge_tree(beast_tree, codeml_tree)
    p1 = ggtree(merged_tree) + theme_tree2()
    p2 = ggtree(rescale_tree(merged_tree, "dN")) + theme_tree2()
    p3 = ggtree(rescale_tree(merged_tree, "rate")) + theme_tree2()
    return plot_list(p1, p2, p3, ncol=3, tag_levels="A")


@register_figure(
    fig_id="fig_2_4",
    num="2.4",
    chapter=2,
    part=PART_I,
    section="2.4 Subsetting and Pruning Trees",
    title="Pruning taxa from an NHX TreeData object while preserving node tags",
    caption=(
        "Original phyldog NHX tree with three target tips highlighted in red (A) compared against the pruned subtree "
        "obtained via drop_tip(nhx, to_drop) (B)."
    ),
    apis=["read_nhx", "drop_tip", "ggtree", "scale_color_manual", "geom_tiplab", "plot_list"],
    size=(860, 440),
)
def _fig_2_4():
    nhx = read_nhx(system_file("extdata", "NHX", "phyldog.nhx"))
    to_drop = [
        "Physonect_sp_@2066767",
        "Lychnagalma_utricularia@2253871",
        "Kephyes_ovata@2606431",
    ]
    p1 = (
        ggtree(nhx)
        + geom_tiplab(aes(color="label %in% to_drop"), size=2.8)
        + scale_color_manual(values=["black", "red"])
        + xlim(0, 0.85)
    )
    nhx_reduced = drop_tip(nhx, to_drop)
    p2 = (
        ggtree(nhx_reduced)
        + geom_tiplab(size=2.8)
        + xlim(0, 0.85)
    )
    return plot_list(p1, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_2_5",
    num="2.5",
    chapter=2,
    part=PART_I,
    section="2.4 Subsetting and Extracting Subtrees by Tip",
    title="Subsetting around a focal tip with preserved annotations and root-edge placement",
    caption=(
        "Full Flu A H3 BEAST tree (A); 4-level subset around A/Swine/HK/168/2012 highlighting the focal lineage (B); "
        "subset annotated with preserved rate values (C); positioned at its ancestral root coordinate (D); and rendered "
        "with geom_rootedge() on the original time scale (E)."
    ),
    apis=["read_beast", "tree_subset", "ggtree", "geom_rootedge", "scale_fill_continuous", "plot_list"],
    size=(1020, 580),
)
def _fig_2_5():
    beast_tree = read_beast(system_file("extdata", "MCC_FluA_H3.tree"))
    tree2 = tree_subset(beast_tree, "A/Swine/HK/168/2012", levels_back=4)
    p1 = ggtree(beast_tree) + geom_tiplab(offset=0.05, size=1.8) + xlim(0, 40) + theme_tree2()
    p2 = (
        ggtree(tree2, aes(color="group"))
        + scale_color_manual(values=["black", "red"], guide="none")
        + geom_tiplab(offset=0.2, size=2.4)
        + xlim(0, 4.5)
        + theme_tree2()
    )
    p3 = (
        p2
        + geom_point(aes(fill="rate"), color="black", shape=21, size=3.4)
        + scale_fill_continuous(low="blue", high="red")
        + xlim(0, 5.2)
        + theme(legend_position="right")
    )
    p4 = (
        ggtree(tree2, aes(color="group"), root_position=tree2.root_edge)
        + geom_tiplab(size=2.4)
        + xlim(18, 24)
        + scale_color_manual(values=["black", "red"], guide="none")
        + theme_tree2()
    )
    p5 = p4 + geom_rootedge(rootedge=tree2.root_edge) + xlim(0, 50)
    return plot_list(p1, p2, p3, p4, p5, design="AABBCC\nAADDEE", tag_levels="A")


@register_figure(
    fig_id="fig_2_6",
    num="2.6",
    chapter=2,
    part=PART_I,
    section="2.4 Subsetting Trees by Internal Node and Taxonomic Group",
    title="Extracting clade neighborhoods by internal node ID and taxonomic group",
    caption=(
        "Clade extraction at internal node 121 with levels_back=0 (A) and levels_back=2 (B); highlighting Plecotus "
        "bats via groupOTU() in a 916-tip chiroptera phylogeny (C); and zooming into the Plecotus clade via "
        "MRCA() and tree_subset() (D)."
    ),
    apis=["read_beast", "read_tree", "MRCA", "tree_subset", "groupOTU", "ggtree", "plot_list"],
    size=(960, 680),
)
def _fig_2_6():
    beast_tree = read_beast(system_file("extdata", "MCC_FluA_H3.tree"))
    clade = tree_subset(beast_tree, 121, levels_back=0)
    clade2 = tree_subset(beast_tree, 121, levels_back=2)
    p1 = ggtree(clade) + geom_tiplab(size=2.1) + hexpand(0.55)
    p2 = (
        ggtree(clade2, aes(color="group"))
        + geom_tiplab(size=1.9)
        + scale_color_manual(values=["black", "red"])
        + hexpand(0.55)
    )

    chiroptera = read_tree(system_file("extdata", "TDbook", "chiroptera.nwk"))
    plecotus_tips = [t for t in chiroptera.tip_label if "Plecotus" in t]
    ch_grp = groupOTU(chiroptera, plecotus_tips)
    plec_clade = MRCA(chiroptera, plecotus_tips)
    sub_plec = tree_subset(chiroptera, plec_clade, levels_back=0)
    p3 = (
        ggtree(ch_grp, aes(color="group"), size=0.35)
        + scale_color_manual(values=["black", "red"])
        + theme(legend_position="none")
    )
    p4 = ggtree(sub_plec) + geom_tiplab(size=2.8) + xlim(0, 6.0)
    return plot_list(p1, p2, p3, p4, ncol=2, nrow=2, tag_levels="A")


@register_figure(
    fig_id="fig_2_7",
    num="2.7",
    chapter=2,
    part=PART_I,
    section="2.5 Visualizing Multiple Trees Together",
    title="Mirrored two-tree co-phylogeny with highlighted clades and tip connectors",
    caption=(
        "Two facing 30-tip trees rendered using roundrect (left) and mirrored ellipse (right) layouts, each carrying "
        "independent discrete clade highlight scales separated by new_scale_fill(), shadowtext tip labels, and tip links."
    ),
    apis=["rtree", "ggtree", "geom_tree", "geom_hilight", "new_scale_fill", "geom_line", "geom_tiplab"],
    size=(920, 540),
)
def _fig_2_7():
    set_seed(1024)
    x = rtree(30)
    y = rtree(30)
    p1 = ggtree(x, layout="roundrect")
    d1 = fortify(x)
    d2 = fortify(y)
    max_d1 = max(d1["x"].tolist())
    max_d2 = max(d2["x"].tolist())
    d2["x"] = [max_d2 - float(vx) + max_d1 + 1.8 for vx in d2["x"].tolist()]
    tip1 = [r for r in d1.to_records() if r.get("isTip")]
    tip2 = [r for r in d2.to_records() if r.get("isTip")]
    dd = DataFrame({
        "label": [str(r["label"]) for r in tip1] + [str(r["label"]) for r in tip2],
        "x": [float(r["x"]) for r in tip1] + [float(r["x"]) for r in tip2],
        "y": [float(r["y"]) for r in tip1] + [float(r["y"]) for r in tip2],
    })
    p = (
        p1
        + geom_hilight(mapping=aes(subset="node %in% c(38, 48, 58, 36)", fill="as.factor(node)"))
        + labs(fill="clades for tree in left")
        + new_scale_fill()
        + geom_hilight(data=d2, mapping=aes(subset="node %in% c(38, 48, 58)", fill="as.factor(node)"))
        + labs(fill="clades for tree in right")
        + geom_tree(data=d2, layout="ellipse")
        + geom_line(aes("x", "y", group="label"), data=dd, color="#9CA3AF")
        + geom_tiplab(color="white", geom="shadowtext", bg_colour="#CA6767", size=2.9)
        + geom_tiplab(data=d2, hjust=1, color="white", geom="shadowtext", bg_colour="#CA6767", size=2.9)
    )
    return p


@register_figure(
    fig_id="fig_2_8",
    num="2.8",
    chapter=2,
    part=PART_I,
    section="2.5 Visualizing Multiple Trees Together",
    title="Comparing three phylogenetic trees side-by-side with tip linkage",
    caption=(
        "Three 15-tip phylogenies arranged sequentially in a single coordinate space with translucent tip-correspondence "
        "lines colored by whether node indices belong to tips (node <= 15)."
    ),
    apis=["rtree", "fortify", "ggtree", "geom_tree", "geom_line", "geom_tiplab"],
    size=(920, 480),
)
def _fig_2_8():
    set_seed(2020)
    x = rtree(15)
    y = rtree(15)
    z = rtree(15)
    d1 = fortify(x)
    d2 = fortify(y)
    d3 = fortify(z)
    shift2 = max(d1["x"].tolist()) + 2.4
    d2["x"] = [float(vx) + shift2 for vx in d2["x"].tolist()]
    shift3 = max(d2["x"].tolist()) + 2.4
    d3["x"] = [float(vx) + shift3 for vx in d3["x"].tolist()]
    tips = [r for r in (d1.to_records() + d2.to_records() + d3.to_records()) if r.get("isTip")]
    dd = DataFrame({
        "label": [str(r["label"]) for r in tips],
        "x": [float(r["x"]) for r in tips],
        "y": [float(r["y"]) for r in tips],
        "node": [int(r["node"]) for r in tips],
    })
    p = (
        ggtree(x, layout="roundrect")
        + geom_tree(data=d2)
        + geom_tree(data=d3)
        + geom_line(aes("x", "y", group="label", color="node < 15"), data=dd, alpha=0.35)
        + geom_tiplab(size=2.9)
        + geom_tiplab(data=d2, size=2.9)
        + geom_tiplab(data=d3, size=2.9)
        + hexpand(0.08)
    )
    return p

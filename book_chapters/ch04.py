"""Chapter 4 figure generators (Phylogenetic Tree Visualization)."""

from __future__ import annotations

from .registry import PART_II, register_figure


@register_figure(
    fig_id="fig_4_1",
    num="4.1",
    chapter=4,
    part=PART_II,
    section="4.1.1 Visualizing Phylogenetic Tree with ggtree",
    title="Basic tree visualization",
    caption=(
        "Basic tree visualization. Default ggtree output with ladderized effect (A), "
        "non-variable setting (e.g., color, size, line type) (B), non-ladderized tree (C), "
        "and cladogram that only displays tree topology without branch length information (D)."
    ),
    apis=["ggplot", "ggtree", "geom_tree", "theme_tree", "read_tree"],
    size=(960, 720),
)
def fig_4_1():
    from ggtree import (
        aes,
        geom_tree,
        ggplot,
        ggtree,
        plot_list,
        read_tree,
        system_file,
        theme_tree,
    )

    nwk = system_file("extdata", "sample.nwk")
    tree = read_tree(nwk)

    p1 = ggplot(tree, aes("x", "y")) + geom_tree() + theme_tree()
    p2 = ggtree(tree, color="firebrick", size=2, linetype="dotted")
    p3 = ggtree(tree, ladderize=False)
    p4 = ggtree(tree, branch_length="none")

    return plot_list(p1, p2, p3, p4, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_4_2",
    num="4.2",
    chapter=4,
    part=PART_II,
    section="4.2.1 Tree Layouts",
    title="Tree layouts",
    caption=(
        "Tree layouts. Phylogram: rectangular layout (A), rounded rectangular layout (B), "
        "slanted layout (C), ellipse layout (D), circular layout (E), and fan layout (F). "
        "Unrooted: equal-angle method (G) and daylight method (H). Cladogram: rectangular layout (I), "
        "ellipse (J), circular layout (K), and unrooted layout (L)."
    ),
    apis=["ggtree", "rtree", "set_seed", "plot_list"],
    size=(1150, 860),
)
def fig_4_2():
    from ggtree import ggtree, plot_list, rtree, set_seed

    set_seed(2017 - 2 - 16)
    tree = rtree(50)

    pA = ggtree(tree)
    pB = ggtree(tree, layout="roundrect")
    pC = ggtree(tree, layout="slanted")
    pD = ggtree(tree, layout="ellipse")
    pE = ggtree(tree, layout="circular")
    pF = ggtree(tree, layout="fan", open_angle=120)
    pG = ggtree(tree, layout="equal_angle")
    pH = ggtree(tree, layout="daylight")
    pI = ggtree(tree, branch_length="none")
    pJ = ggtree(tree, layout="ellipse", branch_length="none")
    pK = ggtree(tree, branch_length="none", layout="circular")
    pL = ggtree(tree, layout="daylight", branch_length="none")

    return plot_list(
        pA, pB, pC, pD, pE, pF, pG, pH, pI, pJ, pK, pL,
        ncol=4,
        tag_levels="A",
    )


@register_figure(
    fig_id="fig_4_3",
    num="4.3",
    chapter=4,
    part=PART_II,
    section="4.2.1 Tree Layouts",
    title="Derived Tree layouts",
    caption=(
        "Derived Tree layouts: right-to-left rectangular layout (A), bottom-up rectangular layout (B), "
        "top-down rectangular layout (Dendrogram) (C), rotated rectangular layout (D), "
        "bottom-up slanted layout (E), top-down slanted layout (Cladogram) (F), "
        "circular layout (G), and circular inward layout (H and I)."
    ),
    apis=[
        "ggtree",
        "scale_x_reverse",
        "coord_flip",
        "layout_dendrogram",
        "layout_inward_circular",
        "as_ggplot",
        "xlim",
    ],
    size=(1050, 960),
)
def fig_4_3():
    from ggtree import (
        as_ggplot,
        coord_flip,
        ggtree,
        layout_dendrogram,
        layout_inward_circular,
        plot_list,
        rtree,
        scale_x_reverse,
        set_seed,
        xlim,
    )

    set_seed(2017 - 2 - 16)
    tree = rtree(50)

    pA = ggtree(tree) + scale_x_reverse()
    pB = ggtree(tree) + coord_flip()
    pC = ggtree(tree) + layout_dendrogram()
    pD = as_ggplot(ggtree(tree), angle=-30, scale=0.9)
    pE = ggtree(tree, layout="slanted") + coord_flip()
    pF = ggtree(tree, layout="slanted", branch_length="none") + layout_dendrogram()
    pG = ggtree(tree, layout="circular") + xlim(-10, None)
    pH = ggtree(tree) + layout_inward_circular()
    pI = ggtree(tree) + layout_inward_circular(xlim=15)

    return plot_list(
        pA, pB, pC, pD, pE, pF, pG, pH, pI,
        ncol=3,
        tag_levels="A",
    )


@register_figure(
    fig_id="fig_4_4",
    num="4.4",
    chapter=4,
    part=PART_II,
    section="4.2.2 Displaying Tree Scale",
    title="Timescaled layout",
    caption=(
        "Timescaled layout. The x-axis is the timescale (in units of the year). "
        "The divergence time in this example was inferred by BEAST using the molecular clock model."
    ),
    apis=["read_beast", "ggtree", "theme_tree2"],
    size=(860, 600),
)
def fig_4_4():
    from ggtree import ggtree, read_beast, system_file, theme_tree2

    beast_file = system_file("extdata", "MCC_FluA_H3.tree")
    beast_tree = read_beast(beast_file)
    return ggtree(beast_tree, mrsd="2013-01-01") + theme_tree2()


@register_figure(
    fig_id="fig_4_5",
    num="4.5",
    chapter=4,
    part=PART_II,
    section="4.2.3 Two-Dimensional Tree Layout",
    title="Two-dimensional tree layout",
    caption=(
        "Two-dimensional tree layout. The trunk and other branches are highlighted in red (for swine) "
        "and blue (for humans). The x-axis is scaled to the branch length (in units of year) of the "
        "timescaled tree. The y-axis is scaled to the number of predicted N-linked glycosylation sites "
        "(NLG) on the hemagglutinin protein."
    ),
    apis=[
        "read_beast",
        "groupOTU",
        "ggtree",
        "theme_classic",
        "scale_color_manual",
        "geom_nodepoint",
        "geom_rootpoint",
        "geom_tippoint",
        "annotate",
        "ylab",
    ],
    size=(920, 620),
)
def fig_4_5():
    from ggtree import (
        aes,
        annotate,
        geom_nodepoint,
        geom_rootpoint,
        geom_tippoint,
        ggtree,
        groupOTU,
        read_beast,
        scale_color_manual,
        system_file,
        theme,
        theme_classic,
        ylab,
    )

    beast_file = system_file("extdata", "MCC_FluA_H3.tree")
    beast_tree = read_beast(beast_file)

    nag_file = system_file("extdata", "NAG_inHA1.txt")
    with open(nag_file, encoding="utf-8") as fh:
        rows = [line.strip().split("\t") for line in fh if line.strip()]
    nag = {r[0]: float(r[1]) for r in rows}

    tips = beast_tree.phylo.tip_label
    swine_tips = [t for t in tips if "Swine" in t]
    beast_tree = groupOTU(beast_tree, swine_tips, group_name="host")

    p = (
        ggtree(beast_tree, aes(color="host"), mrsd="2013-01-01", yscale="label", yscale_mapping=nag)
        + theme_classic()
        + theme(legend_position="none")
        + scale_color_manual(values=["blue", "red"], labels=["human", "swine"])
        + ylab("Number of predicted N-linked glycosylation sites")
    )

    return (
        p
        + geom_nodepoint(color="grey", size=3, alpha=0.8)
        + geom_rootpoint(color="black", size=3)
        + geom_tippoint(size=3, alpha=0.5)
        + annotate("point", 1992, 5.6, size=3, color="black")
        + annotate("point", 1992, 5.4, size=3, color="grey")
        + annotate("point", 1991.6, 5.2, size=3, color="blue")
        + annotate("point", 1992, 5.2, size=3, color="red")
        + annotate("text", 1992.3, 5.6, hjust=0, size=4, label="Root node")
        + annotate("text", 1992.3, 5.4, hjust=0, size=4, label="Internal nodes")
        + annotate("text", 1992.3, 5.2, hjust=0, size=4, label="Tip nodes (blue: human; red: swine)")
    )


@register_figure(
    fig_id="fig_4_6",
    num="4.6",
    chapter=4,
    part=PART_II,
    section="4.3.1 Displaying Tree Scale (Evolution Distance)",
    title="Display treescale",
    caption=(
        "Display treescale. geom_treescale() automatically adds a scale bar for evolutionary "
        "distance (A). Users can modify the color, width, and position of the scale (B) as well as "
        "the size of the scale bar and text and their relative position (C). Another possible solution "
        "is to enable the x-axis which is useful for the timescaled tree (D)."
    ),
    apis=["ggtree", "geom_treescale", "theme_tree2", "plot_list"],
    size=(960, 740),
)
def fig_4_6():
    from ggtree import geom_treescale, ggtree, plot_list, rtree, set_seed, theme_tree2

    set_seed(2017 - 2 - 16)
    tree = rtree(50)

    p1 = ggtree(tree) + geom_treescale()
    p2 = ggtree(tree) + geom_treescale(x=0, y=45, width=1, color="red")
    p3 = ggtree(tree) + geom_treescale(fontsize=6, linesize=2, offset=1)
    p4 = ggtree(tree) + theme_tree2()

    return plot_list(p1, p2, p3, p4, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_4_7",
    num="4.7",
    chapter=4,
    part=PART_II,
    section="4.3.2 Displaying Nodes/Tips",
    title="Display external and internal nodes",
    caption=(
        "Display external and internal nodes. geom_point() automatically adds symbolic points of all "
        "nodes (A). geom_nodepoint() adds symbolic points for internal nodes and geom_tippoint() adds "
        "symbolic points for external nodes (B)."
    ),
    apis=["ggtree", "geom_point", "geom_nodepoint", "geom_tippoint", "plot_list"],
    size=(980, 500),
)
def fig_4_7():
    from ggtree import (
        aes,
        geom_nodepoint,
        geom_point,
        geom_tippoint,
        ggtree,
        plot_list,
        rtree,
        set_seed,
    )

    set_seed(2017 - 2 - 16)
    tree = rtree(50)

    p1 = ggtree(tree) + geom_point(aes(shape="isTip", color="isTip"), size=3)
    p2 = (
        ggtree(tree)
        + geom_nodepoint(color="#b5e521", alpha=1 / 4, size=10)
        + geom_tippoint(color="#FDAC4F", shape=8, size=3)
    )

    return plot_list(p1, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_4_8",
    num="4.8",
    chapter=4,
    part=PART_II,
    section="4.3.3 Displaying Labels",
    title="Display tip labels",
    caption=(
        "Display tip labels. geom_tiplab() supports displaying tip labels (A). For the circular, fan, "
        "or unrooted tree layouts, the labels can be rotated to fit the angle of the branches (B). "
        "For rectangular/dendrogram layout, tip labels can be displayed as y-axis labels (C)."
    ),
    apis=["ggtree", "geom_tiplab", "geom_nodepoint", "plot_list"],
    size=(1260, 520),
)
def fig_4_8():
    from ggtree import aes, geom_nodepoint, geom_tiplab, ggtree, plot_list, rtree, set_seed

    set_seed(2017 - 2 - 16)
    tree = rtree(50)

    p1 = (
        ggtree(tree)
        + geom_nodepoint(color="#b5e521", alpha=1 / 4, size=10)
        + geom_tiplab(size=3, color="purple")
    )
    p2 = ggtree(tree, layout="circular") + geom_tiplab(aes(angle="angle"), color="blue")
    p3 = ggtree(tree) + geom_tiplab(as_ylab=True, color="firebrick")

    return plot_list(p1, p2, p3, ncol=3, tag_levels="A")


@register_figure(
    fig_id="fig_4_9",
    num="4.9",
    chapter=4,
    part=PART_II,
    section="4.3.4 Displaying Root-Edge",
    title="Display root-edge",
    caption=(
        "Display root-edge. geom_rootedge() supports displaying root-edge if the root edge was "
        "present (A). It shows nothing if there is no root-edge (B). Users can manually set the "
        "root edge for the tree (C) or specify the root edge length directly for plotting (D)."
    ),
    apis=["read_tree", "ggtree", "geom_tiplab", "geom_rootedge", "plot_list"],
    size=(920, 680),
)
def fig_4_9():
    from ggtree import geom_rootedge, geom_tiplab, ggtree, plot_list, read_tree

    tree1 = read_tree(text="((A:1,B:2):3,C:2):1;")
    pA = ggtree(tree1) + geom_tiplab() + geom_rootedge()

    tree2 = read_tree(text="((A:1,B:2):3,C:2);")
    pB = ggtree(tree2) + geom_tiplab() + geom_rootedge()

    tree3 = read_tree(text="((A:1,B:2):3,C:2);")
    tree3.root_edge = 2
    pC = ggtree(tree3) + geom_tiplab() + geom_rootedge()

    pD = ggtree(tree2) + geom_tiplab() + geom_rootedge(rootedge=3)

    return plot_list(pA, pB, pC, pD, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_4_10",
    num="4.10",
    chapter=4,
    part=PART_II,
    section="4.3.5 Color Tree",
    title="Color tree by continuous or discrete feature",
    caption=(
        "Color tree by continuous or discrete feature. Edges are colored by values "
        "associated with the child nodes."
    ),
    apis=["read_beast", "ggtree", "scale_color_continuous", "theme"],
    size=(920, 640),
)
def fig_4_10():
    from ggtree import aes, ggtree, read_beast, scale_color_continuous, system_file, theme

    beast_file = system_file("extdata", "MCC_FluA_H3.tree")
    beast_tree = read_beast(beast_file)

    return (
        ggtree(beast_tree, aes(color="rate"))
        + scale_color_continuous(low="darkgreen", high="red")
        + theme(legend_position="right")
    )


@register_figure(
    fig_id="fig_4_11",
    num="4.11",
    chapter=4,
    part=PART_II,
    section="4.3.5 Color Tree",
    title="Continuous state transition in edges",
    caption=(
        "Continuous state transition in edges. Edges are colored by interpolated ancestral-to-offspring "
        "trait values reconstructed using fastAnc()."
    ),
    apis=[
        "read_tree",
        "fastAnc",
        "nodeid",
        "full_join",
        "ggtree",
        "geom_tree",
        "geom_tiplab",
        "scale_color_gradientn",
    ],
    size=(1220, 620),
)
def fig_4_11():
    from ggtree import (
        DataFrame,
        aes,
        fastAnc,
        full_join,
        geom_tiplab,
        geom_tree,
        ggtree,
        nodeid,
        plot_list,
        read_tree,
        scale_color_gradientn,
        system_file,
        theme,
        xlim,
    )

    tree_anole = read_tree(system_file("extdata", "TDbook", "tree_anole.nwk"))
    svl_path = system_file("extdata", "TDbook", "df_svl.tsv")
    with open(svl_path, encoding="utf-8") as fh:
        lines = [line.strip() for line in fh if line.strip()]
    svl = {k: float(v) for line in lines[1:] for k, v in [line.split("\t")]}

    fit = fastAnc(tree_anole, svl, vars=True, CI=True)
    tip_names = list(svl.keys())
    tip_nodes = nodeid(tree_anole, tip_names)
    td_nodes = [int(n) for n in tip_nodes]
    td_vals = [svl[name] for name in tip_names]
    nd_nodes = [int(n) for n in fit.ace.keys()]
    nd_vals = [float(v) for v in fit.ace.values()]

    d = DataFrame({"node": td_nodes + nd_nodes, "trait": td_vals + nd_vals})
    tree = full_join(tree_anole, d, by="node")

    cols = ["red", "orange", "green", "cyan", "blue"]
    p1 = (
        ggtree(tree, aes(color="trait"), layout="circular", ladderize=False, continuous="colour", size=2)
        + scale_color_gradientn(colours=cols)
        + geom_tiplab(hjust=-0.1)
        + xlim(0, 1.2)
        + theme(legend_position=(0.05, 0.85))
    )
    p2 = (
        ggtree(tree, layout="circular", ladderize=False, size=2.8)
        + geom_tree(aes(color="trait"), continuous="colour", size=2)
        + scale_color_gradientn(colours=cols)
        + geom_tiplab(aes(color="trait"), hjust=-0.1)
        + xlim(0, 1.2)
        + theme(legend_position=(0.05, 0.85))
    )

    return plot_list(p1, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_4_12",
    num="4.12",
    chapter=4,
    part=PART_II,
    section="4.3.5 Color Tree",
    title="Phenogram",
    caption=(
        "Phenogram. Projecting the tree into a space defined by time (or genetic distance) "
        "on the horizontal axis and phenotype on the vertical dimension."
    ),
    apis=["fastAnc", "full_join", "ggtree", "scale_color_viridis_c", "theme_minimal"],
    size=(760, 820),
)
def fig_4_12():
    from ggtree import (
        DataFrame,
        aes,
        fastAnc,
        full_join,
        ggtree,
        nodeid,
        read_tree,
        scale_color_viridis_c,
        system_file,
        theme_minimal,
    )

    tree_anole = read_tree(system_file("extdata", "TDbook", "tree_anole.nwk"))
    svl_path = system_file("extdata", "TDbook", "df_svl.tsv")
    with open(svl_path, encoding="utf-8") as fh:
        lines = [line.strip() for line in fh if line.strip()]
    svl = {k: float(v) for line in lines[1:] for k, v in [line.split("\t")]}

    fit = fastAnc(tree_anole, svl, vars=True, CI=True)
    tip_names = list(svl.keys())
    td_nodes = [int(n) for n in nodeid(tree_anole, tip_names)]
    td_vals = [svl[name] for name in tip_names]
    nd_nodes = [int(n) for n in fit.ace.keys()]
    nd_vals = [float(v) for v in fit.ace.values()]

    d = DataFrame({"node": td_nodes + nd_nodes, "trait": td_vals + nd_vals})
    tree = full_join(tree_anole, d, by="node")

    return (
        ggtree(tree, aes(color="trait"), continuous="colour", yscale="trait")
        + scale_color_viridis_c()
        + theme_minimal()
    )


@register_figure(
    fig_id="fig_4_13",
    num="4.13",
    chapter=4,
    part=PART_II,
    section="4.3.6 Rescale Tree Branches",
    title="Rescale tree branches",
    caption=(
        "Rescale tree branches. A time-scaled tree inferred by BEAST (A) and its branches rescaled by "
        "substitution rate (B). A tree inferred by CodeML (C) and its branches rescaled by dN/dS values (D)."
    ),
    apis=["read_beast", "read_codeml_mlc", "ggtree", "theme_tree2", "labs", "plot_list"],
    size=(960, 780),
)
def fig_4_13():
    from ggtree import (
        ggtree,
        labs,
        plot_list,
        read_beast,
        read_codeml_mlc,
        system_file,
        theme_tree2,
    )

    beast_file = system_file("extdata", "MCC_FluA_H3.tree")
    beast_tree = read_beast(beast_file)
    p1 = ggtree(beast_tree, mrsd="2013-01-01") + theme_tree2() + labs(caption="Divergence time")
    p2 = ggtree(beast_tree, branch_length="rate") + theme_tree2() + labs(caption="Substitution rate")

    mlcfile = system_file("extdata", "treeio", "PAML_Codeml", "mlc")
    mlc_tree = read_codeml_mlc(mlcfile)
    p3 = ggtree(mlc_tree) + theme_tree2() + labs(caption="nucleotide substitutions per codon")
    p4 = ggtree(mlc_tree, branch_length="dN_vs_dS") + theme_tree2() + labs(caption="dN/dS tree")

    return plot_list(p1, p2, p3, p4, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_4_14",
    num="4.14",
    chapter=4,
    part=PART_II,
    section="4.3.7 Modify Compoment Themes",
    title="Tree background and color themes",
    caption=(
        "Tree themes. Background and foreground colors can be customized cleanly with theme_tree() "
        "and theme components."
    ),
    apis=["ggtree", "theme_tree", "rtree", "set_seed", "plot_list"],
    size=(960, 440),
)
def fig_4_14():
    from ggtree import ggtree, plot_list, rtree, set_seed, theme_tree

    set_seed(2019)
    x = rtree(30)
    p1 = ggtree(x, color="#0808E5", size=1) + theme_tree("#FEE4E9")
    p2 = ggtree(x, color="orange", size=1) + theme_tree("grey30")

    return plot_list(p1, p2, ncol=2)


@register_figure(
    fig_id="fig_4_15",
    num="4.15",
    chapter=4,
    part=PART_II,
    section="4.4 Visualizing a list of trees",
    title="Visualizing multiPhylo object",
    caption=(
        "Visualizing multiPhylo object. The ggtree() function supports visualizing multiple trees "
        "stored in multiPhylo or TreeDataList objects using facet_wrap()."
    ),
    apis=["read_r8s", "ggtree", "facet_wrap", "theme_tree2"],
    size=(1140, 380),
)
def fig_4_15():
    from ggtree import facet_wrap, ggtree, read_r8s, system_file, theme_tree2

    r8s = read_r8s(system_file("extdata", "r8s", "H3_r8s_output.log"))
    return ggtree(r8s) + facet_wrap("~.id", scales="free") + theme_tree2()


@register_figure(
    fig_id="fig_4_16",
    num="4.16",
    chapter=4,
    part=PART_II,
    section="4.4 Visualizing a list of trees",
    title="Visualizing one hundred bootstrap trees simultaneously",
    caption="Visualizing one hundred bootstrap trees simultaneously.",
    apis=["read_tree", "ggtree", "facet_wrap"],
    size=(1160, 1080),
)
def fig_4_16():
    from ggtree import facet_wrap, ggtree, read_tree, system_file

    btrees = read_tree(system_file("extdata", "RAxML", "RAxML_bootstrap.H3"))
    return ggtree(btrees) + facet_wrap("~.id", ncol=10)


@register_figure(
    fig_id="fig_4_17",
    num="4.17",
    chapter=4,
    part=PART_II,
    section="4.4 Visualizing a list of trees",
    title="Annotate one tree with values from different variables",
    caption=(
        "Annotate one tree with values from different variables. Using subset aesthetic mapping "
        "(TREE1 panel) or td_filter() (TREE2 panel) to filter variables to be displayed on the "
        "specific panel with independent color scales."
    ),
    apis=[
        "TreeDataList",
        "facet_wrap",
        "geom_tippoint",
        "td_filter",
        "new_scale_colour",
        "scale_colour_gradient",
        "scale_colour_viridis_c",
    ],
    size=(1060, 520),
)
def fig_4_17():
    import numpy as np

    from ggtree import (
        DataFrame,
        TreeDataList,
        aes,
        facet_wrap,
        full_join,
        geom_tippoint,
        ggtree,
        new_scale_colour,
        rtree,
        scale_colour_gradient,
        scale_colour_viridis_c,
        set_seed,
        td_filter,
    )

    set_seed(2020)
    rng = np.random.default_rng(2020)
    x = rtree(30)
    d = DataFrame(
        {
            "label": x.tip_label,
            "var1": np.abs(rng.normal(size=30)).tolist(),
            "var2": np.abs(rng.normal(size=30)).tolist(),
        }
    )
    tree = full_join(x, d, by="label")
    trs = TreeDataList({"TREE1": tree, "TREE2": tree})

    return (
        ggtree(trs)
        + facet_wrap("~.id")
        + geom_tippoint(aes(subset='.id == "TREE1"', colour="var1"))
        + scale_colour_gradient(low="blue", high="red")
        + new_scale_colour()
        + geom_tippoint(aes(colour="var2"), data=td_filter('.id == "TREE2"'))
        + scale_colour_viridis_c()
    )


@register_figure(
    fig_id="fig_4_18",
    num="4.18",
    chapter=4,
    part=PART_II,
    section="4.4 Visualizing a list of trees",
    title="DensiTree",
    caption=(
        "DensiTree. Trees are stacked on top of each other and the structures of the trees are "
        "rotated to ensure the consistency of the tip order."
    ),
    apis=["read_tree", "ggdensitree", "geom_tiplab", "hexpand"],
    size=(1020, 660),
)
def fig_4_18():
    from ggtree import geom_tiplab, ggdensitree, hexpand, read_tree, system_file

    btrees = read_tree(system_file("extdata", "RAxML", "RAxML_bootstrap.H3"))
    return (
        ggdensitree(btrees, alpha=0.3, colour="steelblue")
        + geom_tiplab(size=3)
        + hexpand(0.35)
    )

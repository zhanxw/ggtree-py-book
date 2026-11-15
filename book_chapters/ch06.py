"""Chapter 6 figure generators (Visual Exploration of Phylogenetic Trees)."""

from __future__ import annotations

from .registry import PART_II, register_figure


@register_figure(
    fig_id="fig_6_1",
    num="6.1",
    chapter=6,
    part=PART_II,
    section="6.1 Viewing Selected Clade",
    title="Viewing a selected clade of a tree",
    caption=(
        "Viewing a selected clade of a tree. An example tree used to demonstrate how ggtree "
        "supports exploring or manipulating a phylogenetic tree visually (A), and viewing a "
        "selected clade defined by MRCA('I', 'L') via viewClade() (B)."
    ),
    apis=["ggtree", "geom_tiplab", "viewClade", "MRCA", "plot_list"],
    size=(920, 480),
)
def fig_6_1():
    from ggtree import MRCA, geom_tiplab, ggtree, plot_list, read_tree, system_file, viewClade

    nwk = system_file("extdata", "sample.nwk")
    tree = read_tree(nwk)
    p = ggtree(tree) + geom_tiplab()
    p2 = viewClade(p, MRCA(p, "I", "L"))

    return plot_list(p, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_6_2",
    num="6.2",
    chapter=6,
    part=PART_II,
    section="6.2 Scaling Clades",
    title="Scaling selected clade",
    caption=(
        "Scaling selected clade. Clades can be zoomed in (scale > 1) to highlight "
        "or zoomed out (scale < 1) via scaleClade() to save vertical space."
    ),
    apis=["groupClade", "ggtree", "scale_color_manual", "scaleClade", "plot_list"],
    size=(920, 480),
)
def fig_6_2():
    from ggtree import (
        aes,
        ggtree,
        groupClade,
        plot_list,
        read_tree,
        scaleClade,
        scale_color_manual,
        system_file,
        theme,
    )

    nwk = system_file("extdata", "sample.nwk")
    tree = read_tree(nwk)
    tree2 = groupClade(tree, [17, 21])
    p = (
        ggtree(tree2, aes(color="group"))
        + theme(legend_position="none")
        + scale_color_manual(values=["black", "firebrick", "steelblue"])
    )
    p2 = scaleClade(p, node=17, scale=0.1)

    return plot_list(p, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_6_3",
    num="6.3",
    chapter=6,
    part=PART_II,
    section="6.3 Collapsing and Expanding a Clade",
    title="Collapsing selected clades and expanding collapsed clades",
    caption=(
        "Collapsing selected clades and expanding collapsed clades. Selected clades can be collapsed "
        "(A) and expanded back cleanly via expand() (B). Green and red symbols mark the collapsed nodes."
    ),
    apis=["collapse", "expand", "geom_point2", "groupClade", "plot_list"],
    size=(920, 480),
)
def fig_6_3():
    from ggtree import (
        aes,
        collapse,
        expand,
        geom_point2,
        ggtree,
        groupClade,
        plot_list,
        read_tree,
        scale_color_manual,
        system_file,
        theme,
    )

    nwk = system_file("extdata", "sample.nwk")
    tree = read_tree(nwk)
    tree2 = groupClade(tree, [17, 21])
    p = (
        ggtree(tree2, aes(color="group"))
        + theme(legend_position="none")
        + scale_color_manual(values=["black", "firebrick", "steelblue"])
    )

    p2 = collapse(p, node=21) + geom_point2(aes(subset="node == 21"), shape=21, size=5, fill="green")
    p2 = collapse(p2, node=23) + geom_point2(aes(subset="node == 23"), shape=23, size=5, fill="red")
    p3 = expand(expand(p2, node=23), node=21)

    return plot_list(p2, p3, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_6_4",
    num="6.4",
    chapter=6,
    part=PART_II,
    section="6.3 Collapsing and Expanding a Clade",
    title="Collapse clade as a triangle",
    caption=(
        "Collapse clade as a triangle. 'max' takes the most distant tip (A), 'min' takes the "
        "closest tip (B), 'mixed' spans both closest and distant tips (C), custom triangle fill/border/alpha "
        "styling (D), and combining scaleClade() with collapse() (E)."
    ),
    apis=["collapse", "scaleClade", "geom_tiplab", "groupClade", "plot_list"],
    size=(1120, 760),
)
def fig_6_4():
    from ggtree import (
        aes,
        collapse,
        expand,
        geom_tiplab,
        ggtree,
        groupClade,
        plot_list,
        read_tree,
        scaleClade,
        scale_color_manual,
        system_file,
        theme,
    )

    nwk = system_file("extdata", "sample.nwk")
    tree = read_tree(nwk)
    tree2 = groupClade(tree, [17, 21])
    p = (
        ggtree(tree2, aes(color="group"))
        + theme(legend_position="none")
        + scale_color_manual(values=["black", "firebrick", "steelblue"])
    )
    p2 = p + geom_tiplab()
    node = 21

    pA = expand(collapse(p2, node, "max", fill="grey20", alpha=0.85), node)
    pB = expand(collapse(p2, node, "min", fill="grey20", alpha=0.85), node)
    pC = expand(collapse(p2, node, "mixed", fill="grey20", alpha=0.85), node)
    pD = collapse(collapse(p, 21, "mixed", fill="steelblue", alpha=0.4), 23, "mixed", fill="firebrick", color="blue")
    pE = collapse(scaleClade(p, 23, 0.2), 23, "min", fill="darkgreen")

    return plot_list(pA, pB, pC, pD, pE, ncol=3, tag_levels="A")


@register_figure(
    fig_id="fig_6_5",
    num="6.5",
    chapter=6,
    part=PART_II,
    section="6.4 Grouping OTUs",
    title="Grouping OTUs",
    caption=(
        "Grouping OTUs. A BioNJ clustering tree computed from Manhattan distances on the Iris "
        "dataset with species grouped via groupOTU() and colored by shared ancestry."
    ),
    apis=["DataFrame", "dist", "bionj", "ggtree", "groupOTU"],
    size=(860, 620),
)
def fig_6_5():
    from ggtree import (
        DataFrame,
        aes,
        bionj,
        dist,
        ggtree,
        groupOTU,
        system_file,
        theme,
    )

    iris_path = system_file("extdata", "TDbook", "iris.tsv")
    with open(iris_path, encoding="utf-8") as fh:
        lines = [line.strip() for line in fh if line.strip()]
    rows = [line.split("\t") for line in lines[1:]]
    rn = [f"{r[4]}_{i}" for i, r in enumerate(rows, 1)]
    df_iris = DataFrame(
        {
            "Sepal.Length": [float(r[0]) for r in rows],
            "Sepal.Width": [float(r[1]) for r in rows],
            "Petal.Length": [float(r[2]) for r in rows],
            "Petal.Width": [float(r[3]) for r in rows],
        },
        index=rn,
    )

    d_iris = dist(df_iris, method="man")
    tree_iris = bionj(d_iris)
    grp = {
        "setosa": rn[:50],
        "versicolor": rn[50:100],
        "virginica": rn[100:150],
    }

    p_iris = ggtree(tree_iris, layout="circular", branch_length="none")
    return groupOTU(p_iris, grp, "Species") + aes(color="Species") + theme(legend_position="right")


@register_figure(
    fig_id="fig_6_6",
    num="6.6",
    chapter=6,
    part=PART_II,
    section="6.5 Rotating Clades",
    title="Exploring tree structure via rotate and flip",
    caption=(
        "Exploring tree structure. A clade (indicated by a dark green circle) in a tree (A) "
        "can be rotated by 180 degrees via rotate() (B), and the positions of its immediate "
        "descendant clades (red and blue) can be exchanged via flip() (C)."
    ),
    apis=["groupClade", "geom_point2", "rotate", "flip", "plot_list"],
    size=(1140, 480),
)
def fig_6_6():
    from ggtree import (
        aes,
        flip,
        geom_point2,
        ggtree,
        groupClade,
        plot_list,
        read_tree,
        rotate,
        scale_color_manual,
        system_file,
        theme,
    )

    nwk = system_file("extdata", "sample.nwk")
    tree = read_tree(nwk)
    tree2 = groupClade(tree, [17, 21])
    p = (
        ggtree(tree2, aes(color="group"))
        + theme(legend_position="none")
        + scale_color_manual(values=["black", "firebrick", "steelblue"])
    )

    p1 = p + geom_point2(aes(subset="node == 16"), color="darkgreen", size=5)
    p2 = rotate(p1, 16)
    p3 = flip(p2, 17, 21)

    return plot_list(p1, p2, p3, ncol=3, tag_levels="A")


@register_figure(
    fig_id="fig_6_7",
    num="6.7",
    chapter=6,
    part=PART_II,
    section="6.6 Open Tree",
    title="Transforming a tree to fan layout",
    caption="Transforming a tree to a fan layout by opening a circular sector using open_tree(p, 180).",
    apis=["open_tree", "geom_tiplab", "groupClade", "ggtree"],
    size=(840, 520),
)
def fig_6_7():
    from ggtree import (
        aes,
        geom_tiplab,
        ggtree,
        groupClade,
        open_tree,
        read_tree,
        scale_color_manual,
        system_file,
        theme,
    )

    nwk = system_file("extdata", "sample.nwk")
    tree = read_tree(nwk)
    tree2 = groupClade(tree, [17, 21])
    p = (
        ggtree(tree2, aes(color="group"))
        + theme(legend_position="none")
        + scale_color_manual(values=["black", "firebrick", "steelblue"])
    )
    return open_tree(p, 180) + geom_tiplab()


@register_figure(
    fig_id="fig_6_8",
    num="6.8",
    chapter=6,
    part=PART_II,
    section="6.7 Rotate Tree",
    title="Rotating tree",
    caption="Rotating tree. A circular or fan layout tree can be rotated by any specific angle using rotate_tree().",
    apis=["open_tree", "rotate_tree", "geom_tiplab", "ggtree"],
    size=(840, 520),
)
def fig_6_8():
    from ggtree import (
        aes,
        geom_tiplab,
        ggtree,
        groupClade,
        open_tree,
        read_tree,
        rotate_tree,
        scale_color_manual,
        system_file,
        theme,
    )

    nwk = system_file("extdata", "sample.nwk")
    tree = read_tree(nwk)
    tree2 = groupClade(tree, [17, 21])
    p = (
        ggtree(tree2, aes(color="group"))
        + theme(legend_position="none")
        + scale_color_manual(values=["black", "firebrick", "steelblue"])
    )
    p3 = open_tree(p, 180) + geom_tiplab()
    return rotate_tree(p3, 180)


@register_figure(
    fig_id="fig_6_9",
    num="6.9",
    chapter=6,
    part=PART_II,
    section="6.5 Rotating Clades",
    title="Rotate selected clades",
    caption="Rotate selected clades. Four internal nodes were selected to rotate independently (red symbols).",
    apis=["rtree", "set_seed", "ggtree", "geom_tiplab", "rotate", "geom_point2", "plot_list"],
    size=(1280, 540),
)
def fig_6_9():
    import random

    from ggtree import (
        aes,
        geom_point2,
        geom_tiplab,
        ggtree,
        plot_list,
        rotate,
        rtree,
        set_seed,
    )

    set_seed(2016 - 5 - 29)
    x = rtree(50)
    p = ggtree(x) + geom_tiplab()

    internal_nodes = sorted({int(v) for v in x.edge[:, 0]})
    nn = random.Random(2016 - 5 - 29).sample(internal_nodes, 4)

    pp = []
    for n in nn:
        pr = rotate(p, n) + geom_point2(aes(subset=f"node == {n}"), color="red", size=3)
        pp.append(pr)

    return plot_list(*pp, ncol=4, tag_levels="A")


@register_figure(
    fig_id="fig_6_10",
    num="6.10",
    chapter=6,
    part=PART_II,
    section="6.6 Open Tree",
    title="Open tree with different angles",
    caption="Open tree with different angles (0 to 270 degrees) converting a circular layout into progressively narrower fans.",
    apis=["rtree", "set_seed", "ggtree", "open_tree", "ggtitle", "plot_list"],
    size=(1100, 760),
)
def fig_6_10():
    from ggtree import ggtree, ggtitle, open_tree, plot_list, rtree, set_seed

    set_seed(123)
    tr = rtree(50)
    p = ggtree(tr, layout="circular")
    angles = [0, 54, 108, 162, 216, 270]
    pp = [open_tree(p, angle=a) + ggtitle(f"open angle: {a}") for a in angles]

    return plot_list(*pp, ncol=3, tag_levels="A")


@register_figure(
    fig_id="fig_6_11",
    num="6.11",
    chapter=6,
    part=PART_II,
    section="6.7 Rotate Tree",
    title="Rotate tree with different angles",
    caption="Rotate tree with different angles (0 to 270 degrees) spinning the circular layout while highlighting focal node 6.",
    apis=["rtree", "set_seed", "ggtree", "geom_point2", "rotate_tree", "ggtitle", "plot_list"],
    size=(1100, 760),
)
def fig_6_11():
    from ggtree import aes, geom_point2, ggtree, ggtitle, plot_list, rotate_tree, rtree, set_seed

    set_seed(123)
    tr = rtree(50)
    p = ggtree(tr, layout="circular") + geom_point2(aes(subset="node == 6"), color="red", size=3)
    angles = [0, 54, 108, 162, 216, 270]
    pp = [rotate_tree(p, angle=a) + ggtitle(f"rotate angle: {a}") for a in angles]

    return plot_list(*pp, ncol=3, tag_levels="A")

"""Figure generators for faq."""

from __future__ import annotations

from ggtree import *
from .registry import PART_I, PART_II, PART_III, PART_IV, APPENDIX, register_figure


@register_figure(
    fig_id="fig_A_1",
    num="A.1",
    chapter=14,
    part=APPENDIX,
    section="A.4.1 Allocating Space for Truncated Tip Labels",
    title="Allocating more spaces for truncated tip labels.",
    caption="Allocating more spaces for truncated tip labels. Long tip labels may be truncated (A). One solution is to allocate more spaces for plot panel (B), and another solution is to allow plotting labels outside the plot panel (C).",
    apis=["xlim", "coord_cartesian", "theme_tree2", "margin", "plot_list"],
    size=(940, 380),
)
def _fig_A_1():
    from ggtree import (
        read_tree, ggtree, geom_tiplab, xlim, coord_cartesian,
        theme_tree2, margin, plot_list,
    )

    tree = read_tree(
        text="(Organism1.006G249400.1:0.03977,"
             "(Organism2.022118m:0.01337,(Organism3.J34265.1:0.00284,"
             "Organism4.G02633.1:0.00468)0.51:0.0104):0.02469);"
    )
    p = ggtree(tree) + geom_tiplab()
    p_b = p + xlim(0, 0.08)
    p_c = p + coord_cartesian(clip="off") + theme_tree2(plot_margin=margin(6, 120, 6, 6))
    return plot_list(p, p_b, p_c, ncol=3, tag_levels="A")


@register_figure(
    fig_id="fig_A_2",
    num="A.2",
    chapter=14,
    part=APPENDIX,
    section="A.4.2 Modify (Tip) Labels",
    title="Alternative tip labels.",
    caption="Alternative tip labels. Original tip labels (A) and a modified version (B).",
    apis=["rename_taxa", "geom_tiplab", "xlim", "plot_list"],
    size=(800, 380),
)
def _fig_A_2():
    from ggtree import read_tree, data_frame, ggtree, geom_tiplab, xlim, aes, NA, plot_list

    tree = read_tree(text="((A, B), (C, D));")
    d = data_frame(
        label=["A", "B", "C", "D"],
        label2=["sunflower", "tree", "snail", "mushroom"],
    )
    p = ggtree(tree) + xlim(NA, 3)
    p1 = p + geom_tiplab()
    p2 = p % d + geom_tiplab(aes(label="label2"))
    return plot_list(p1, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_A_3",
    num="A.3",
    chapter=14,
    part=APPENDIX,
    section="A.4.3 Formatting (Tip) Labels",
    title="Formatting labels.",
    caption="Formatting labels. Formatting specific tip labels using plotmath expression (A), and Markdown/HTML (B).",
    apis=["geom_tiplab", "geom_richtext", "td_filter", "hexpand", "plot_list"],
    size=(860, 380),
)
def _fig_A_3():
    from ggtree import (
        read_tree, data_frame, ggtree, aes, xlim, NA, geom_tiplab,
        geom_richtext, td_filter, hexpand, plot_list,
    )

    tree = read_tree(text="((a,(b,c)),d);")
    genus = ["Gorilla", "Pan", "Homo", "Pongo"]
    species = ["gorilla", "spp.", "sapiens", "pygmaeus"]
    geo = ["Africa", "Africa", "World", "Asia"]
    colors = ["#E495A5", "#ABB065", "#39BEB1", "#ACA4E2"]
    d2 = data_frame(
        label=tree.tip_label,
        genus=genus,
        species=species,
        geo=geo,
        lab=[f"italic({g})~bolditalic({s})~({ge})" for g, s, ge in zip(genus, species, geo)],
        color=colors,
        name=[f"<i style='color:{c}'>{g} **{s}**</i> ({ge})" for c, g, s, ge in zip(colors, genus, species, geo)],
    )
    p1 = ggtree(tree) % d2 + xlim(NA, 6) + geom_tiplab(aes(label="lab"), parse=True)
    p2 = ggtree(tree) % d2 + geom_richtext(aes(label="name"), data=td_filter("isTip"), label_color=NA) + hexpand(0.35)
    return plot_list(p1, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_A_4",
    num="A.4",
    chapter=14,
    part=APPENDIX,
    section="A.4.4 Avoid Overlapping Text Labels",
    title="Repel labels.",
    caption="Repel labels. Repel labels to avoid overlapping.",
    apis=["read_raxml", "geom_label_repel", "geom_text_repel", "scale_fill_viridis_c"],
    size=(840, 580),
)
def _fig_A_4():
    from ggtree import read_raxml, system_file, ggtree, geom_label_repel, aes, theme, scale_fill_viridis_c

    raxml_file = system_file("extdata", "RAxML", "RAxML_bipartitionsBranchLabels.H3")
    raxml = read_raxml(raxml_file)
    p = (
        ggtree(raxml)
        + geom_label_repel(aes(label="bootstrap", fill="bootstrap"))
        + theme(legend_position=[0.1, 0.8])
        + scale_fill_viridis_c()
    )
    return p


@register_figure(
    fig_id="fig_A_5",
    num="A.5",
    chapter=14,
    part=APPENDIX,
    section="A.4.5 Bootstrap Values from Newick Format",
    title="Bootstrap value stored in node label.",
    caption="Bootstrap value stored in node label.",
    apis=["read_tree", "geom_label2", "as_numeric", "is_na"],
    size=(840, 580),
)
def _fig_A_5():
    from ggtree import read_tree, system_file, ggtree, geom_label2, aes

    nwk = system_file("extdata", "RAxML", "RAxML_bipartitions.H3")
    tr = read_tree(nwk)
    p = ggtree(tr) + geom_label2(
        aes(label="label", subset="~is_na(as_numeric(label)) & (as_numeric(label) > 80)")
    )
    return p


@register_figure(
    fig_id="fig_A_6",
    num="A.6",
    chapter=14,
    part=APPENDIX,
    section="A.5.1 Plot the Same Tree as plot.phylo()",
    title="Ladderized and non-ladderized tree.",
    caption="Ladderized and non-ladderized tree. plot.phylo() displays non-ladderized tree (A), use ladderize = FALSE to display non-ladderized tree in ggtree() (B), ggtree() displays ladderized tree by default (C).",
    apis=["plot_phylo", "ggtree", "ladderize", "geom_tiplab", "plot_list"],
    size=(880, 360),
)
def _fig_A_6():
    from ggtree import set_seed, rtree, plot_phylo, ggtree, geom_tiplab, plot_list

    set_seed(42)
    x = rtree(5)
    pa = plot_phylo(x)
    pb = ggtree(x, ladderize=False) + geom_tiplab()
    pc = ggtree(x) + geom_tiplab()
    return plot_list(pa, pb, pc, ncol=3, tag_levels="A")


@register_figure(
    fig_id="fig_A_7",
    num="A.7",
    chapter=14,
    part=APPENDIX,
    section="A.5.2 Specifying the Order of Tips",
    title="Specifying tree order.",
    caption="Specifying tree order. The order of the input tree will be maintained in ggtree() when ladderize = FALSE.",
    apis=["rotateConstr", "ggtree", "geom_tiplab", "hexpand"],
    size=(680, 380),
)
def _fig_A_7():
    from ggtree import set_seed, rtree, rotateConstr, ggtree, geom_tiplab, hexpand

    set_seed(42)
    x = rtree(5)
    y = rotateConstr(x, ["t4", "t2", "t5", "t1", "t3"])
    return ggtree(y, ladderize=False) + geom_tiplab() + hexpand(0.15)


@register_figure(
    fig_id="fig_A_8",
    num="A.8",
    chapter=14,
    part=APPENDIX,
    section="A.5.3 Shrink Outlier Long Branch",
    title="Shrink outlier long branch.",
    caption="Shrink outlier long branch. Original tree (A); reduced outgroup branch length (B); truncated tree plot (C).",
    apis=["scale_x_break", "MRCA", "groupClade", "hexpand", "plot_list"],
    size=(940, 560),
)
def _fig_A_8():
    from ggtree import (
        read_tree, system_file, MRCA, groupClade, ggtree, aes,
        geom_tiplab, theme, scale_x_break, hexpand, plot_list,
    )

    x = read_tree(system_file("extdata", "TDbook", "tree_long_branch_example.nwk"))
    m = MRCA(x, 75, 76)
    y = groupClade(x, m)
    p1 = ggtree(y, aes(linetype="group")) + geom_tiplab(size=2) + theme(legend_position="none")
    p = p1.copy()
    mean_x = sum(float(v) for v in p.data["x"]) / len(p.data)
    p.data["x"] = [mean_x if int(nd) in (75, 76) else xv for nd, xv in zip(p.data["node"], p.data["x"])]
    p2 = p1 + scale_x_break([0.03, 0.09]) + hexpand(0.05)
    return plot_list(p1, p, p2, ncol=3, tag_levels="A")


@register_figure(
    fig_id="fig_A_9",
    num="A.9",
    chapter=14,
    part=APPENDIX,
    section="A.5.4 Attach a New Tip to a Tree",
    title="Attaching a new tip to a tree.",
    caption="Attaching a new tip to a tree. Different line types were employed to distinguish the newly introduced tip and an error bar was added to indicate the uncertainty of the added branch position.",
    apis=["bind_tip", "as_tibble", "parent", "as_treedata", "geom_errorbarh", "scale_linetype_manual"],
    size=(760, 440),
)
def _fig_A_9():
    from ggtree import (
        set_seed, rtree, bind_tip, as_tibble, parent, as_treedata,
        ggtree, aes, geom_tiplab, geom_errorbarh, scale_linetype_manual,
        theme, NA, hexpand,
    )

    set_seed(1993)
    tr = rtree(5)
    tr2 = bind_tip(tr, "U", edge_length=0.1, where=7, position=0.15)
    d = as_tibble(tr2)
    u_par = int(parent(d, "U")["node"][0])
    d["type"] = ["newly introduced" if lbl == "U" else "original" for lbl in d["label"]]
    d["sd"] = [0.05 if int(nd) == u_par else NA for nd in d["node"]]
    tr3 = as_treedata(d)
    p = (
        ggtree(tr3, aes(linetype="type"))
        + geom_tiplab()
        + geom_errorbarh(aes(xmin="x - sd", xmax="x + sd", y="y - 0.3"), linetype="dashed", height=0.1)
        + scale_linetype_manual(values={"newly introduced": "dashed", "original": "solid"})
        + hexpand(0.15)
        + theme(legend_position=[0.8, 0.2])
    )
    return p


@register_figure(
    fig_id="fig_A_10",
    num="A.10",
    chapter=14,
    part=APPENDIX,
    section="A.5.5 Arbitrarily Colored & Styled Branches",
    title="Change colors and line types of specific branches.",
    caption="Change colors and line types of specific branches.",
    apis=["I", "Nnode2", "geom_label", "aes"],
    size=(760, 460),
)
def _fig_A_10():
    from ggtree import set_seed, rtree, Nnode2, data_frame, ggtree, geom_label, aes

    set_seed(123)
    x = rtree(10)
    n_tot = Nnode2(x)
    d = data_frame(
        node=list(range(1, n_tot + 1)),
        colour=["red" if i in (2, 3, 14, 15) else "black" for i in range(1, n_tot + 1)],
    )
    lty_map = {2: 2, 5: 3, 13: 2, 14: 4}
    d2 = data_frame(
        node=list(range(1, n_tot + 1)),
        lty=[lty_map.get(i, 1) for i in range(1, n_tot + 1)],
    )
    p = ggtree(x) + geom_label(aes(label="node"))
    return p % d % d2 + aes(colour="I(colour)", linetype="I(lty)")


@register_figure(
    fig_id="fig_A_11",
    num="A.11",
    chapter=14,
    part=APPENDIX,
    section="A.5.6 Add an Arbitrary Point on a Branch",
    title="Add an arbitrary point on a branch.",
    caption="Add an arbitrary point on a branch. The position of the symbolic point can be adjusted by an absolute value (A) or in proportion to the branch length (B).",
    apis=["geom_nodepoint", "aes", "plot_list"],
    size=(840, 420),
)
def _fig_A_11():
    from ggtree import set_seed, rtree, ggtree, geom_nodepoint, aes, plot_list

    set_seed(2020 - 5 - 20)
    x = rtree(10)
    p = ggtree(x)
    p1 = p + geom_nodepoint(aes(subset="node == 13", x="x - 0.1"), size=5, colour="firebrick", shape=21)
    p2 = (
        p
        + geom_nodepoint(aes(subset="node == 13", x="x - branch_length * 0.2"), size=3, colour="firebrick")
        + geom_nodepoint(aes(subset="node == 13", x="x - branch_length * 0.8"), size=5, colour="steelblue")
    )
    return plot_list(p1, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_A_12",
    num="A.12",
    chapter=14,
    part=APPENDIX,
    section="A.6 Different X-Axis Labels for Facet Panels",
    title="X-axis titles for different facet panels.",
    caption="X-axis titles for different facet panels.",
    apis=["geom_facet", "theme_bw", "xlim_tree", "xlim_expand", "scale_y_continuous", "coord_cartesian"],
    size=(820, 540),
)
def _fig_A_12():
    from ggtree import (
        set_seed, rtree, rnorm, data_frame, ggtree, geom_tiplab,
        geom_facet, geom_point, aes, theme_bw, xlim_tree, xlim_expand,
        scale_y_continuous, geom_text, coord_cartesian, theme, margin,
    )

    set_seed(2019 - 5 - 2)
    x = rtree(30)
    p = ggtree(x) + geom_tiplab()
    d_val = data_frame(label=x.tip_label, value=rnorm(30))
    p2 = (
        p
        + geom_facet(panel="Dot", data=d_val, geom=geom_point, mapping=aes(x="value"))
        + theme_bw()
        + xlim_tree(5)
        + xlim_expand([-5, 5], "Dot")
    )
    d_lbl = data_frame(**{".panel": ["Tree", "Dot"], "lab": ["Distance", "Dot Units"], "x": [2.5, 0.0], "y": [-2.0, -2.0]})
    res = (
        p2
        + scale_y_continuous(limits=[0, 31], expand=[0, 0])
        + geom_text(aes(label="lab"), data=d_lbl)
        + coord_cartesian(clip="off")
        + theme(plot_margin=margin(6, 6, 40, 6))
    )
    return res


@register_figure(
    fig_id="fig_A_13",
    num="A.13",
    chapter=14,
    part=APPENDIX,
    section="A.7 Plot Layers Behind the Phylogeny",
    title="Add layers behind the tree structure.",
    caption="Add layers behind the tree structure. A layer on top of the tree structure (A). Reverse layer order of A (B). Add layer behind the tree layer (C).",
    apis=["geom_hilight", "ggplot", "geom_tree", "theme_tree", "plot_list"],
    size=(880, 360),
)
def _fig_A_13():
    from ggtree import set_seed, rtree, ggtree, ggplot, geom_hilight, geom_tree, theme_tree, plot_list

    set_seed(1982)
    x = rtree(5)
    p1 = ggtree(x) + geom_hilight(node=7, alpha=1)
    p2 = p1.copy()
    p2.layers = list(reversed(p2.layers))
    p3 = ggplot(x) + geom_hilight(node=7, alpha=1) + geom_tree() + theme_tree()
    return plot_list(p1, p2, p3, ncol=3, tag_levels="A")


@register_figure(
    fig_id="fig_A_14",
    num="A.14",
    chapter=14,
    part=APPENDIX,
    section="A.8 Enlarge Center Space in Circular/Fan Layout",
    title="Enlarge center space in circular tree.",
    caption="Enlarge center space in circular tree. Allocate more space by xlim (A) or long root branch (B).",
    apis=["layout_circular", "xlim", "geom_rootedge", "plot_list"],
    size=(820, 420),
)
def _fig_A_14():
    from ggtree import set_seed, rtree, ggtree, xlim, NA, geom_rootedge, plot_list

    set_seed(1982)
    tree = rtree(30)
    pa = ggtree(tree, layout="circular") + xlim(-10, NA)
    pb = ggtree(tree, layout="circular") + geom_rootedge(5)
    return plot_list(pa, pb, tag_levels="A", ncol=2)


@register_figure(
    fig_id="fig_A_15",
    num="A.15",
    chapter=14,
    part=APPENDIX,
    section="A.9 Backward Timescale from Most Distant Tip",
    title="Origin of the time scale.",
    caption="Origin of the time scale. Forward: from the root to the tips (A). Backward: from the most distant tip to the root (B).",
    apis=["revts", "scale_x_continuous", "theme_tree2", "plot_list"],
    size=(840, 420),
)
def _fig_A_15():
    from ggtree import set_seed, rtree, ggtree, theme_tree2, revts, scale_x_continuous, plot_list

    set_seed(123)
    tr = rtree(10)
    p = ggtree(tr) + theme_tree2()
    p2 = revts(p) + scale_x_continuous(labels=abs)
    return plot_list(p, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_A_16",
    num="A.16",
    chapter=14,
    part=APPENDIX,
    section="A.10 Trim Blank Margins for Circular Layout",
    title="Trim extra white space for polar coordinates.",
    caption="Trim extra white space for polar coordinates. Original plot (A). Trimmed version (B).",
    apis=["ggsave", "image_read", "image_trim", "image_ggplot", "element_rect", "plot_list"],
    size=(820, 420),
)
def _fig_A_16():
    import tempfile
    from ggtree import (
        set_seed, rtree, ggtree, ggsave, image_read, image_trim,
        image_ggplot, theme, element_rect, NA, plot_list,
    )

    set_seed(2021)
    tr = rtree(30)
    p = ggtree(tr, size=1, colour="purple", layout="circular")
    with tempfile.NamedTemporaryFile(suffix=".png") as tf:
        ggsave(filename=tf.name, plot=p, width=7, height=7)
        x_img = image_read(tf.name, density=300)
        y_img = image_trim(x_img)
    panel_border = theme(panel_border=element_rect(colour="black", fill=NA, size=2))
    xx = image_ggplot(x_img) + panel_border
    yy = image_ggplot(y_img) + panel_border
    return plot_list(xx, yy, tag_levels="A", ncol=2)

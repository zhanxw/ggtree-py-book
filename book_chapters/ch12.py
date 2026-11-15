"""Figure generators for ch12."""

from __future__ import annotations

from ggtree import *
from .registry import PART_I, PART_II, PART_III, PART_IV, APPENDIX, register_figure


@register_figure(
    fig_id="fig_12_1",
    num="12.1",
    chapter=12,
    part=PART_III,
    section="12.1 Facet Utilities (facet_widths)",
    title="Adjust relative widths of ggplot facets.",
    caption="Adjust relative widths of ggplot facets. The facet_widths() function works with ggtree (A) as well as ggplot (B).",
    apis=["facet_widths", "geom_facet", "geom_bar", "facet_grid", "plot_list"],
    size=(880, 480),
)
def _fig_12_1():
    from ggtree import (
        set_seed, rtree, runif, data_frame, melt, ggtree, geom_tiplab,
        geom_facet, geom_bar, aes, xlim_tree, facet_widths, ggplot,
        geom_point, facet_grid, read_table, system_file, theme, plot_list,
    )

    set_seed(123)
    tree = rtree(30)
    p = ggtree(tree, branch_length="none") + geom_tiplab() + theme(legend_position="none")
    a = runif(30, 0, 1)
    b = [1.0 - v for v in a]
    df = melt(data_frame(label=tree.tip_label, a=a, b=b), id_vars=["label"])
    p2 = (
        p
        + geom_facet(
            panel="bar",
            data=df,
            geom=geom_bar,
            mapping=aes(x="value", fill="factor(variable)"),
            orientation="y",
            width=0.8,
            stat="identity",
        )
        + xlim_tree(9)
    )
    pa = facet_widths(p2, {"Tree": 0.5})

    iris = read_table(system_file("extdata", "TDbook", "iris.tsv"), header=True, sep="\t")
    pb = facet_widths(
        ggplot(iris, aes("Sepal.Width", "Petal.Length")) + geom_point() + facet_grid(".~Species"),
        {"setosa": 0.5},
    )
    return plot_list(pa, pb, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_12_2",
    num="12.2",
    chapter=12,
    part=PART_III,
    section="12.1.2 Rename Facet Labels (facet_labeller)",
    title="Rename facet labels.",
    caption="Rename facet labels. Rename multiple labels simultaneously (A) or only for a specific one (B) are all supported. facet_labeller() can combine with facet_widths() to rename facet label and then adjust relative widths (B).",
    apis=["facet_labeller", "facet_widths", "geom_facet", "geom_bar", "plot_list"],
    size=(880, 480),
)
def _fig_12_2():
    from ggtree import (
        set_seed, rtree, runif, data_frame, melt, ggtree, geom_tiplab,
        geom_facet, geom_bar, aes, xlim_tree, facet_labeller, facet_widths,
        theme, plot_list,
    )

    set_seed(123)
    tree = rtree(30)
    p = ggtree(tree, branch_length="none") + geom_tiplab() + theme(legend_position="none")
    a = runif(30, 0, 1)
    b = [1.0 - v for v in a]
    df = melt(data_frame(label=tree.tip_label, a=a, b=b), id_vars=["label"])
    p2 = (
        p
        + geom_facet(
            panel="bar",
            data=df,
            geom=geom_bar,
            mapping=aes(x="value", fill="factor(variable)"),
            orientation="y",
            width=0.8,
            stat="identity",
        )
        + xlim_tree(9)
    )
    pa = facet_labeller(p2, {"Tree": "phylogeny", "bar": "HELLO"})
    pb = facet_widths(facet_labeller(p2, {"Tree": "phylogeny"}), {"Tree": 0.4})
    return plot_list(pa, pb, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_12_3",
    num="12.3",
    chapter=12,
    part=PART_III,
    section="12.2 Geometric Layers Supporting Subsetting",
    title="Geometric layers that support subsetting.",
    caption="Geometric layers that support subsetting. These layers work with ggplot2 (A) and ggtree (B).",
    apis=["geom_text2", "geom_label2", "coord_cartesian", "theme_light", "plot_list"],
    size=(880, 440),
)
def _fig_12_3():
    from ggtree import (
        read_table, system_file, ggplot, ggtree, rtree, aes,
        geom_point, geom_text2, geom_label2, coord_cartesian,
        theme_light, theme, plot_list,
    )

    mpg = read_table(system_file("extdata", "TDbook", "mpg.tsv"), header=True, sep="\t")
    p = (
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_point(aes(color="class"))
        + geom_text2(aes(label="manufacturer", subset="(hwy > 40) | (displ > 6.5)"), nudge_y=1)
        + coord_cartesian(clip="off")
        + theme_light()
        + theme(legend_position=[0.85, 0.75])
    )
    p2 = ggtree(rtree(10)) + geom_label2(aes(subset="node < 5", label="label"))
    return plot_list(p, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_12_4",
    num="12.4",
    chapter=12,
    part=PART_III,
    section="12.3 Layout Utilities",
    title="Layout functions for transforming among different layouts.",
    caption="Layout functions for transforming among different layouts. Default rectangular layout (A); transform rectangular to dendrogram layout (B); transform circular to rectangular layout (C); transform rectangular to circular layout (D); transform rectangular to fan layout (E); transform rectangular to inward circular layout (F).",
    apis=[
        "layout_dendrogram", "layout_rectangular", "layout_circular",
        "layout_fan", "layout_inward_circular", "plot_list",
    ],
    size=(920, 620),
)
def _fig_12_4():
    from ggtree import (
        set_seed, rtree, ggtree, layout_dendrogram, layout_rectangular,
        layout_circular, layout_fan, layout_inward_circular,
        geom_tiplab, plot_list,
    )

    set_seed(2019)
    x = rtree(20)
    p = ggtree(x)
    pa = p
    pb = p + layout_dendrogram()
    pc = ggtree(x, layout="circular") + layout_rectangular()
    pd = p + layout_circular()
    pe = p + layout_fan(angle=90)
    pf = p + layout_inward_circular(xlim=4) + geom_tiplab(hjust=1)
    return plot_list(pa, pb, pc, pd, pe, pf, ncol=3, tag_levels="A")


@register_figure(
    fig_id="fig_12_5",
    num="12.5",
    chapter=12,
    part=PART_III,
    section="12.4 Scale Utilities (xlim_expand)",
    title="Setting xlim for user-specific facet panels.",
    caption="Setting xlim for user-specific facet panels. Using xlim_tree() to set the Tree panel of the ggtree output (A) and xlim_expand() to set the Dot panel of the ggtree output (A) and the Virginica panel of the ggplot output (B).",
    apis=["xlim_tree", "xlim_expand", "geom_facet", "facet_grid", "plot_list"],
    size=(880, 480),
)
def _fig_12_5():
    from ggtree import (
        set_seed, rtree, rnorm, data_frame, ggtree, geom_tiplab,
        geom_facet, geom_point, aes, xlim_tree, xlim_expand,
        ggplot, facet_grid, read_table, system_file, plot_list,
    )

    set_seed(2019 - 5 - 2)
    x = rtree(30)
    p = ggtree(x) + geom_tiplab()
    d = data_frame(label=x.tip_label, value=rnorm(30))
    p2 = p + geom_facet(panel="Dot", data=d, geom=geom_point, mapping=aes(x="value"))
    pa = p2 + xlim_tree(6) + xlim_expand([-10, 10], "Dot")

    iris = read_table(system_file("extdata", "TDbook", "iris.tsv"), header=True, sep="\t")
    g = ggplot(iris, aes("Sepal.Length", "Sepal.Width")) + geom_point() + facet_grid(".~Species", scales="free_x")
    pb = g + xlim_expand([0, 15], "virginica")
    return plot_list(pa, pb, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_12_6",
    num="12.6",
    chapter=12,
    part=PART_III,
    section="12.4.2 Expanding Plot Range (hexpand & vexpand)",
    title="Expanding plot limits by a fraction of the x or y range.",
    caption="Expanding plot limits by a fraction of the x or y range. Expand x limit at right-hand side by default (A), and expand x limit for left-hand side when direction = -1 and expand y limit at the upper side (B).",
    apis=["hexpand", "vexpand", "geom_tiplab", "ggplot", "plot_list"],
    size=(880, 460),
)
def _fig_12_6():
    from ggtree import (
        set_seed, rtree, ggtree, geom_tiplab, hexpand, vexpand,
        ggplot, aes, geom_point, read_table, system_file, plot_list,
    )

    set_seed(2019 - 5 - 2)
    x = rtree(30)
    x.tip_label = [f"to make the label longer_{lbl}" for lbl in x.tip_label]
    p1 = ggtree(x) + geom_tiplab() + hexpand(0.4)

    iris = read_table(system_file("extdata", "TDbook", "iris.tsv"), header=True, sep="\t")
    p2 = (
        ggplot(iris, aes("Sepal.Width", "Petal.Width"))
        + geom_point()
        + hexpand(0.2, direction=-1)
        + vexpand(0.2)
    )
    return plot_list(p1, p2, tag_levels="A", widths=[0.6, 0.4])


@register_figure(
    fig_id="fig_12_7",
    num="12.7",
    chapter=12,
    part=PART_III,
    section="12.5 Tree Data Utilities (td_filter)",
    title="Filtering ggtree plot data in geom layers.",
    caption="Filtering ggtree plot data in geom layers. Only selected tips (offspring of the node indicated by the blue circle point) were labeled.",
    apis=["td_filter", "offspring", "geom_text", "geom_nodepoint"],
    size=(760, 540),
)
def _fig_12_7():
    from ggtree import (
        set_seed, rtree, ggtree, offspring, aes, geom_text,
        geom_nodepoint, td_filter, hexpand,
    )

    set_seed(2020)
    tree = rtree(50)
    p = ggtree(tree)
    selected_nodes = offspring(p, 67)["node"]
    res = (
        p
        + geom_text(aes(label="label"), data=td_filter("isTip & node in selected_nodes"), hjust=0)
        + geom_nodepoint(aes(subset="node == 67"), size=5, color="blue")
        + hexpand(0.12)
    )
    return res


@register_figure(
    fig_id="fig_12_8",
    num="12.8",
    chapter=12,
    part=PART_III,
    section="12.5.2 Flattening List-Column Tree Data (td_unnest)",
    title="Flattening ggtree plot data.",
    caption="Flattening ggtree plot data. List-columns can be flattened by td_unnest() and two circle points were displayed on each tip simultaneously (A). Different tree data utilities can be combined to work together, e.g., filter data by td_filter(), and then flatten it by td_unnest()) (B).",
    apis=["nest", "td_unnest", "td_filter", "scale_size", "plot_list"],
    size=(860, 420),
)
def _fig_12_8():
    from ggtree import (
        set_seed, rtree, rnorm, data_frame, rep, c, nest, ggtree,
        geom_point, aes, td_unnest, td_filter, scale_size, plot_list,
    )

    set_seed(1997)
    tr = rtree(5)
    d = data_frame(
        id=rep(tr.tip_label, 2),
        value=[abs(v) for v in rnorm(10, 6, 2)],
        group=c(rep("A", 5), rep("B", 5)),
    )
    d2 = nest(d, value="value", group="group")
    p = ggtree(tr) % d2
    p2 = (
        p
        + geom_point(aes("x", "y", size="value", colour="group"), data=td_unnest(["value", "group"]), alpha=0.4)
        + scale_size(range=[3, 10], limits=[3, 10])
    )
    p3 = (
        p
        + geom_point(
            aes("x", "y", size="value", colour="group"),
            data=td_unnest(["value", "group"], _f=td_filter("isTip & node == 4")),
            alpha=0.4,
        )
        + scale_size(range=[3, 10], limits=[3, 10])
    )
    return plot_list(p2, p3, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_12_9",
    num="12.9",
    chapter=12,
    part=PART_III,
    section="12.6 Tree Utilities (get_taxa_name)",
    title="An example tree for demonstrating get_taxa_name() function.",
    caption="An example tree for demonstrating get_taxa_name() function.",
    apis=["get_taxa_name", "geom_hilight", "geom_tiplab", "labs"],
    size=(760, 440),
)
def _fig_12_9():
    from ggtree import set_seed, rtree, ggtree, geom_tiplab, geom_hilight, get_taxa_name, labs

    set_seed(123)
    tree = rtree(10)
    p = ggtree(tree) + geom_tiplab() + geom_hilight(node=12, extendto=2.5)
    x = "Taxa order: " + ", ".join(get_taxa_name(p))
    return p + labs(title=x)


@register_figure(
    fig_id="fig_12_10",
    num="12.10",
    chapter=12,
    part=PART_III,
    section="12.6.2 Padding Taxa Labels (label_pad)",
    title="Align tip label to the end.",
    caption="Align tip label to the end. With a dotted line (A) and without a dotted line (B).",
    apis=["label_pad", "geom_tiplab", "xlim", "plot_list"],
    size=(840, 400),
)
def _fig_12_10():
    from ggtree import set_seed, rtree, data_frame, label_pad, ggtree, geom_tiplab, aes, xlim, NA, plot_list

    set_seed(2015 - 12 - 21)
    tree = rtree(5)
    tree.tip_label[1] = "long string for test"
    d = data_frame(
        label=tree.tip_label,
        newlabel=label_pad(tree.tip_label),
        newlabel2=label_pad(tree.tip_label, pad=" "),
    )
    p = ggtree(tree) % d + xlim(NA, 5)
    p1 = p + geom_tiplab(aes(label="newlabel"), align=True, family="mono", linetype="dotted", linesize=0.7)
    p2 = p + geom_tiplab(aes(label="newlabel2"), align=True, family="mono", linetype=None, offset=-0.5) + xlim(NA, 5)
    return plot_list(p1, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_12_11",
    num="12.11",
    chapter=12,
    part=PART_III,
    section="12.7 Interactive ggtree Annotation",
    title="Interactive phylogenetic tree using identify() method.",
    caption="Interactive phylogenetic tree using identify() method. Highlighting, labelling and rotating clades are all supported.",
    apis=[
        "identify", "geom_hilight_interactive", "geom_cladelab_interactive",
        "geom_point_interactive", "geom_tiplab_interactive",
    ],
    size=(820, 560),
    interactive=True,
)
def _fig_12_11():
    from ggtree import (
        set_seed, rtree, ggtree, aes, geom_hilight_interactive,
        geom_cladelab_interactive, geom_point_interactive,
        geom_tiplab_interactive, hexpand, theme_tree2,
    )

    set_seed(2021)
    tr = rtree(30)
    p = (
        ggtree(tr)
        + geom_hilight_interactive(node=34, fill="#38BDF8", alpha=0.25, tooltip="Clade 34 highlighted")
        + geom_hilight_interactive(node=45, fill="#F59E0B", alpha=0.25, tooltip="Clade 45 highlighted")
        + geom_cladelab_interactive(node=34, label="Clade A", offset=0.18, barcolor="#0284C7", textcolor="#0284C7", tooltip="Interactive Clade A")
        + geom_cladelab_interactive(node=45, label="Clade B", offset=0.18, barcolor="#D97706", textcolor="#D97706", tooltip="Interactive Clade B")
        + geom_point_interactive(aes(tooltip="label"), size=2.4, color="#1D4ED8")
        + geom_tiplab_interactive(aes(tooltip="label"), size=2.4)
        + hexpand(0.32)
        + theme_tree2()
    )
    return p

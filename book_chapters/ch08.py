"""Figure generators for ch08."""

from __future__ import annotations

from ggtree import *
from .registry import PART_I, PART_II, PART_III, PART_IV, APPENDIX, register_figure


@register_figure(
    fig_id="fig_8_1",
    num="8.1",
    chapter=8,
    part=PART_II,
    section="8.1 Annotating Tree with Images",
    title="Labelling frog family tips and canvas corner with JPEG photographs",
    caption="Using geom_tiplab(geom='image') to align frog family photographs alongside boxed family labels and placing an illustrative icon in canvas space via geom_image().",
    apis=["read_tree", "geom_tiplab", "geom_image", "DataFrame", "xlim", "ylim"],
    size=(860, 580),
)
def _fig_8_1():
    from ggtree import read_tree, DataFrame, system_file, ggtree, aes, geom_tiplab, geom_image, xlim, ylim

    nwk = "((((bufonidae, dendrobatidae), ceratophryidae), (centrolenidae, leptodactylidae)), hylidae);"
    imgdir = system_file("extdata", "frogs")
    x = read_tree(text=nwk)
    df = DataFrame({"label": x.tip_label, "img": [f"{imgdir}/{t}.jpg" for t in x.tip_label]})
    p = (
        ggtree(x) % df
        + xlim(None, 7)
        + ylim(None, 6.2)
        + geom_tiplab(aes(image="img"), geom="image", offset=2, align=2, size=0.2)
        + geom_tiplab(geom="label", offset=1, hjust=0.5)
        + geom_image(x=0.8, y=5.5, image=f"{imgdir}/frog.jpg", size=0.2)
    )
    return p


@register_figure(
    fig_id="fig_8_2",
    num="8.2",
    chapter=8,
    part=PART_II,
    section="8.2 Annotating Tree with Phylopic",
    title="Annotating a hominoid phylogeny with colored PhyloPic silhouettes",
    caption="Querying PhyloPic silhouette IDs via phylopic_uid(), joining body mass measurements, and coloring tip silhouettes along a continuous viridis scale.",
    apis=["read_tree", "phylopic_uid", "geom_tiplab", "scale_color_viridis_c", "%<+%"],
    size=(820, 500),
)
def _fig_8_2():
    from ggtree import read_tree, phylopic_uid, ggtree, aes, geom_tiplab, xlim, scale_color_viridis_c

    newick = (
        "((Pongo_abelii,(Gorilla_gorilla_gorilla,(Pan_paniscus,"
        "Pan_troglodytes)Pan,Homo_sapiens)Homininae)Hominidae,"
        "Nomascus_leucogenys)Hominoidea;"
    )
    tree = read_tree(text=newick)
    d = phylopic_uid(tree.tip_label)
    d["body_mass"] = [52, 114, 47, 45, 58, 6]
    p = (
        ggtree(tree) % d
        + geom_tiplab(aes(image="uid", colour="body_mass"), geom="phylopic", offset=2.5, size=6.5)
        + geom_tiplab(aes(label="label"), offset=0.2)
        + xlim(None, 7)
        + scale_color_viridis_c()
    )
    return p


@register_figure(
    fig_id="fig_8_3",
    num="8.3",
    chapter=8,
    part=PART_II,
    section="8.3 Annotating Tree with Sub-plots",
    title="Annotating internal nodes with marginal likelihood bar (A) and pie (B) insets",
    caption="Estimating ancestral Anolis ecomorph probabilities with ace(..., model='ER', type='discrete') and overlaying stacked bar charts (A) or pie charts (B) on internal branches and nodes via geom_inset().",
    apis=["getStates", "ace", "nodebar", "nodepie", "geom_inset", "plot_list"],
    size=(1060, 680),
)
def _fig_8_3():
    from ggtree import (
        read_tree, DataFrame, system_file, getStates, ace, nodebar, nodepie,
        ggtree, aes, geom_tiplab, geom_tippoint, geom_inset, scale_color_manual,
        xlim, theme, plot_list,
    )

    anoletree = read_tree(system_file("extdata", "TDbook", "anoletree.nwk"))
    x = getStates(anoletree, "tips")
    cols = {"CG": "black", "GB": "#DF536B", "TC": "#61D04F", "TG": "#2297E6", "Tr": "#28E2E5", "Tw": "#CD0BBC"}
    fitER = ace(x, anoletree, model="ER", type="discrete")
    ancstats = fitER.lik_anc.copy()
    ancstats["node"] = [int(r) for r in fitER.lik_anc.rownames]

    bars = nodebar(ancstats, cols=fitER.states, color=cols, position="stack")
    pies = nodepie(ancstats, cols=fitER.states, color=cols)
    stat_df = DataFrame({"label": list(x.keys()), "stat": list(x.values())})

    p_left = (
        ggtree(anoletree) % stat_df
        + geom_tiplab(size=2.0)
        + geom_tippoint(aes(color="stat"), show_legend=False)
        + scale_color_manual(values=cols)
        + theme(legend_position="none")
        + xlim(None, 8)
    )
    p1 = p_left + geom_inset(bars, width=0.05, height=0.03, x="branch", show_legend=False)

    p_right = (
        ggtree(anoletree) % stat_df
        + geom_tiplab(size=2.0)
        + geom_tippoint(aes(color="stat"))
        + scale_color_manual(values=cols)
        + theme(legend_position="right")
        + xlim(None, 8)
    )
    p2 = p_right + geom_inset(pies, width=0.055, height=0.055)
    return plot_list(p1, p2, ncol=2, tag_levels="A")


@register_figure(
    fig_id="fig_8_4",
    num="8.4",
    chapter=8,
    part=PART_II,
    section="8.3 Annotating Tree with Sub-plots",
    title="Combining mixed pie and stacked bar subplots on internal nodes",
    caption="Mixing nodepie() and nodebar() micro-charts inside a single geom_inset() dictionary on the Anolis ecomorph phylogeny.",
    apis=["getStates", "ace", "nodebar", "nodepie", "geom_inset"],
    size=(820, 720),
)
def _fig_8_4():
    from ggtree import (
        set_seed, sample, read_tree, DataFrame, system_file, getStates, ace,
        nodebar, nodepie, ggtree, aes, geom_tiplab, geom_tippoint, geom_inset,
        scale_color_manual, xlim, theme,
    )

    set_seed(84)
    anoletree = read_tree(system_file("extdata", "TDbook", "anoletree.nwk"))
    x = getStates(anoletree, "tips")
    cols = {"CG": "black", "GB": "#DF536B", "TC": "#61D04F", "TG": "#2297E6", "Tr": "#28E2E5", "Tw": "#CD0BBC"}
    fitER = ace(x, anoletree, model="ER", type="discrete")
    ancstats = fitER.lik_anc.copy()
    ancstats["node"] = [int(r) for r in fitER.lik_anc.rownames]

    bars = nodebar(ancstats, cols=fitER.states, color=cols, position="stack")
    pies = nodepie(ancstats, cols=fitER.states, color=cols)
    pies_and_bars = dict(pies)
    for k in sample(list(pies.keys()), 20):
        pies_and_bars[k] = bars[k]

    stat_df = DataFrame({"label": list(x.keys()), "stat": list(x.values())})
    p = (
        ggtree(anoletree) % stat_df
        + geom_tiplab(size=2.0)
        + geom_tippoint(aes(color="stat"))
        + scale_color_manual(values=cols)
        + theme(legend_position="right")
        + xlim(None, 8)
    )
    return p + geom_inset(pies_and_bars, width=0.055, height=0.04)


@register_figure(
    fig_id="fig_8_5",
    num="8.5",
    chapter=8,
    part=PART_II,
    section="8.4 Have Fun with Phylomoji",
    title="Parsing tip labels as phylomoji alongside taxonomic pill labels",
    caption="Tip identifiers mapped to emoji graphics with geom_tiplab(parse='emoji') paired with boxed taxonomic clade descriptions on a dashed tree.",
    apis=["read_tree", "ggtree", "geom_tiplab", "DataFrame", "xlim", "ylim"],
    size=(780, 540),
)
def _fig_8_5():
    from ggtree import read_tree, DataFrame, ggtree, aes, geom_tiplab, xlim, ylim

    tt = "((snail,mushroom),(((sunflower,evergreen_tree),leaves),green_salad));"
    tree = read_tree(text=tt)
    d = DataFrame({
        "label": ["snail", "mushroom", "sunflower", "evergreen_tree", "leaves", "green_salad"],
        "group": ["animal", "fungi", "flowering plant", "conifers", "ferns", "mosses"],
    })
    p = (
        ggtree(tree, linetype="dashed", size=1.1, color="firebrick") % d
        + xlim(0, 4.5)
        + ylim(0.5, 6.5)
        + geom_tiplab(parse="emoji", size=15, vjust=0.25)
        + geom_tiplab(aes(label="group"), geom="label", x=3.35, hjust=1)
    )
    return p


@register_figure(
    fig_id="fig_8_6",
    num="8.6",
    chapter=8,
    part=PART_II,
    section="8.4 Have Fun with Phylomoji",
    title="Rendering phylomoji radially across circular and rotated fan trees",
    caption="(A) Closed circular layout, (B) open_tree(..., angle=200) rotated -90 degrees to form an upward fan, and (C) unrotated 200-degree fan layout.",
    apis=["ggtree", "geom_tiplab", "open_tree", "rotate_tree", "plot_list"],
    size=(860, 640),
)
def _fig_8_6():
    from ggtree import read_tree, ggtree, geom_tiplab, open_tree, rotate_tree, plot_list

    tt = "((snail,mushroom),(((sunflower,evergreen_tree),leaves),green_salad));"
    tree = read_tree(text=tt)
    pA = ggtree(tree, layout="circular", size=1) + geom_tiplab(parse="emoji", size=10, vjust=0.25)
    pC = open_tree(pA, angle=200)
    pB = rotate_tree(pC, -90)
    return plot_list(pA, pB, pC, design="AC\nBC", tag_levels="A")


@register_figure(
    fig_id="fig_8_7",
    num="8.7",
    chapter=8,
    part=PART_II,
    section="8.4 Have Fun with Phylomoji",
    title="Annotating clades with vector emoji icons via geom_cladelab(parse='emoji')",
    caption="Using monochrome tinted vector emojis directly as aligned clade labels on a 30-taxon random phylogeny.",
    apis=["rtree", "geom_cladelab", "scale_color_manual", "DataFrame"],
    size=(760, 540),
)
def _fig_8_7():
    from ggtree import set_seed, rtree, DataFrame, ggtree, aes, geom_cladelab, scale_color_manual, xlim

    set_seed(123)
    tr = rtree(30)
    dat = DataFrame({
        "node": [39, 48, 55],
        "name": ["chicken", "duck", "family"],
    })
    p = (
        ggtree(tr)
        + xlim(None, 5.2)
        + geom_cladelab(
            data=dat,
            mapping=aes(node="node", label="name", color="name"),
            parse="emoji",
            fontsize=12,
            align=True,
            show_legend=False,
        )
        + scale_color_manual(values={"chicken": "firebrick", "duck": "steelblue", "family": "darkkhaki"})
    )
    return p


@register_figure(
    fig_id="fig_8_8",
    num="8.8",
    chapter=8,
    part=PART_II,
    section="8.4 Have Fun with Phylomoji",
    title="Rendering full-color Apple Color Emoji tip icons directly inside SVG",
    caption="Extracting native color glyphs from Apple Color Emoji and embedding them as crisp vector-aligned tip labels.",
    apis=["read_tree", "ggtree", "geom_tiplab", "xlim", "ylim"],
    size=(780, 560),
)
def _fig_8_8():
    from ggtree import read_tree, ggtree, geom_tiplab, xlim, ylim

    tree_text = "(((((cow, (whale, dolphin)), (pig2, boar)), camel), fish), seedling);"
    x = read_tree(text=tree_text)
    p = ggtree(x, size=2) + geom_tiplab(size=20, parse="emoji") + xlim(None, 7) + ylim(None, 8.5)
    return p

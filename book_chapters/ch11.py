"""Figure generators for ch11."""

from __future__ import annotations

from ggtree import *
from .registry import PART_I, PART_II, PART_III, PART_IV, APPENDIX, register_figure


@register_figure(
    fig_id="fig_11_1",
    num="11.1",
    chapter=11,
    part=PART_III,
    section="11.1 Visualizing Differential Taxonomy Clades (MicrobiotaProcess)",
    title="Visualize differential taxonomy clade.",
    caption="Visualize differential taxonomy clade.",
    apis=["ggdiffclade", "scale_fill_manual", "guides", "guide_legend", "theme"],
    size=(980, 920),
)
def _fig_11_1():
    from ggtree import (
        read_table, system_file, ggdiffclade, scale_fill_manual,
        guides, guide_legend, theme, element_rect, element_text,
        margin, unit, NA,
    )

    taxa = read_table(system_file("extdata", "TDbook", "df_alltax_info.tsv"), header=True, sep="\t")
    dt = read_table(system_file("extdata", "TDbook", "df_difftax.tsv"), header=True, sep="\t")
    p = (
        ggdiffclade(
            obj=taxa,
            nodedf=dt,
            factorName="DIAGNOSIS",
            layout="radial",
            skpointsize=0.6,
            cladetext=2,
            linewd=0.2,
            taxlevel=3,
            reduce=True,
        )
        + scale_fill_manual(values=["#00AED7", "#009E73"])
        + guides(color=guide_legend(keywidth=0.1, keyheight=0.6, order=3, ncol=1))
        + theme(
            panel_background=element_rect(fill=NA),
            legend_position="right",
            plot_margin=margin(0, 0, 0, 0),
            legend_spacing_y=unit(0.02, "cm"),
            legend_title=element_text(size=7.5),
            legend_text=element_text(size=5.5),
            legend_box_spacing=unit(0.02, "cm"),
        )
    )
    return p


@register_figure(
    fig_id="fig_11_2",
    num="11.2",
    chapter=11,
    part=PART_III,
    section="11.2 Visualizing Phylogenetic Network Using Tanggle",
    title="Phylogenetic network.",
    caption="Phylogenetic network.",
    apis=["read_nexus_networx", "ggsplitnet", "geom_splitnet", "geom_tiplab2", "rainbow"],
    size=(760, 600),
)
def _fig_11_2():
    from ggtree import (
        read_nexus_networx, system_file, ggsplitnet, aes,
        geom_tiplab2, geom_nodepoint, scale_color_manual,
        rainbow, theme, ggexpand,
    )

    nnet = read_nexus_networx(system_file("extdata", "trees", "woodmouse.nxs"))
    p = (
        ggsplitnet(nnet)
        + geom_tiplab2(aes(color="label"), hjust=-0.1)
        + geom_nodepoint(color="firebrick", alpha=0.4)
        + scale_color_manual(values=rainbow(15))
        + theme(legend_position="none")
        + ggexpand(0.1)
        + ggexpand(0.1, direction=-1)
    )
    return p

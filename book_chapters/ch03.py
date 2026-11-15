"""Figure generators for Chapter 3: Exporting Tree with Data."""

from __future__ import annotations

from ggtree import *
from .registry import PART_I, register_figure


@register_figure(
    fig_id="fig_3_1",
    num="3.1",
    chapter=3,
    part=PART_I,
    section="3.2 Exporting Tree Data to BEAST Nexus Format",
    title="Round-trip BEAST Nexus export preserving NHX and CodeML annotations",
    caption=(
        "Both NHX (phyldog.nhx, panel A) and PAML CodeML (panel B) TreeData objects serialized via write_beast() "
        "and re-imported via read_beast(), preserving continuous branch attributes (S and dN) for ggtree mapping."
    ),
    apis=["read_nhx", "read_codeml", "write_beast", "read_beast", "ggtree", "plot_list"],
    size=(820, 620),
)
def _fig_3_1():
    import os
    import tempfile

    nhx = read_nhx(system_file("extdata", "NHX", "phyldog.nhx"))
    mlc = read_codeml(
        system_file("extdata", "treeio", "PAML_Codeml", "rst"),
        system_file("extdata", "treeio", "PAML_Codeml", "mlc"),
    )
    with tempfile.TemporaryDirectory() as d:
        b1 = os.path.join(d, "nhx_beast.nexus")
        b2 = os.path.join(d, "mlc_beast.nexus")
        write_beast(nhx, file=b1)
        write_beast(mlc, file=b2)
        tr1 = read_beast(b1)
        tr2 = read_beast(b2)

    p1 = (
        ggtree(tr1, aes(color="S"))
        + scale_color_continuous(low="#132B43", high="#56B1F7")
        + geom_tiplab(size=2.8)
        + geom_treescale(x=0.05, y=2.0)
        + hexpand(0.32)
    )
    p2 = (
        ggtree(tr2, aes(color="dN"))
        + scale_color_continuous(low="darkgreen", high="red")
        + geom_tiplab(size=3.0)
        + geom_treescale(x=0.2, y=1.5)
        + hexpand(0.24)
    )
    return plot_list(p1, p2, ncol=1, nrow=2, tag_levels="A")

"""Figure generators for ch13."""

from __future__ import annotations

from ggtree import *
from .registry import PART_I, PART_II, PART_III, PART_IV, APPENDIX, register_figure


@register_figure(
    fig_id="fig_13_1",
    num="13.1",
    chapter=13,
    part=PART_IV,
    section="13.1 Visualizing Pairwise Nucleotide Sequence Distance with Phylogenetic Tree",
    title="HPV58 nucleotide sequence phylogeny with nested clade bars and pairwise Hamming distances",
    caption="Reproducing Figure 13.1 of treedata-book: HPV58 whole-genome ML phylogeny with nested monophyletic/paraphyletic clade annotations paired via geom_facet() with pairwise nucleotide sequence differences (%).",
    apis=["read_tree", "read_fasta", "groupClade", "geom_cladelab", "geom_strip", "geom_facet", "geom_point", "geom_path"],
    size=(960, 820),
)
def _fig_13_1():
    import numpy as np
    from ggtree import (
        read_tree, read_fasta, system_file, groupClade, rootnode, rotate,
        DataFrame, ggtree, aes, geom_tiplab, geom_treescale, scale_color_manual,
        scale_shape_manual, theme_tree2, geom_cladelab, geom_strip, geom_nodelab,
        geom_facet, geom_point, geom_path, facet_widths, hexpand,
    )

    tree = read_tree(system_file("extdata", "TDbook", "tree_HPV58.nwk"))
    aln = read_fasta(system_file("extdata", "TDbook", "dna_HPV58_aln.fas"))

    clade = {"A3": 92, "A1": 94, "A2": 108, "B1": 156, "B2": 159, "C": 163, "D1": 173, "D2": 176}
    tree = groupClade(tree, clade)
    cols = {
        "A1": "#EC762F", "A2": "#CA6629", "A3": "#894418", "B1": "#0923FA",
        "B2": "#020D87", "C": "#000000", "D1": "#9ACD32", "D2": "#08630A",
    }

    p = (
        rotate(ggtree(tree, aes(color="group"), ladderize=False), rootnode(tree))
        + geom_tiplab(aes(label="paste0(\"italic('\", label, \"')\")"), parse=True, size=1.6)
        + geom_treescale(x=0, y=1, width=0.002)
        + scale_color_manual(
            values=cols,
            na_value="black",
            name="Lineage",
            breaks=["A1", "A2", "A3", "B1", "B2", "C", "D1", "D2"],
        )
        + hexpand(0.42)
        + theme_tree2(legend_position=(0.05, 0.90))
    )

    dat1 = DataFrame({
        "node": [94, 108, 131, 156, 159, 173, 176],
        "name": ["A1", "A2", "A3", "B1", "B2", "D1", "D2"],
        "offset": [0.0038] * 7,
        "offset_text": [-0.0004] * 7,
        "extend": [(0, 0.5), 0.5, (0.5, 0), (0, 0.5), (0.5, 0), (0, 0.5), (0.5, 0)],
    })
    dat2 = DataFrame({
        "node": [92, 172],
        "name": ["A", "D"],
        "offset": [0.0052, 0.0052],
        "offset_text": [0.00025, 0.00025],
        "extend": [0, 0],
    })
    dat3 = DataFrame({
        "node": [163],
        "name": ["C"],
        "offset": [0.0051],
        "offset_text": [0.00025],
        "extend": [0],
    })

    p = (
        p
        + geom_cladelab(
            data=dat1,
            mapping=aes(node="node", label="name", color="group", offset="offset", offset_text="offset_text", extend="extend"),
            barsize=1.2, fontface=3, align=True, fontsize=2.6,
        )
        + geom_cladelab(
            data=dat2,
            mapping=aes(node="node", label="name", offset="offset", offset_text="offset_text", extend="extend"),
            barcolor="darkgrey", textcolor="darkgrey", barsize=2.0, fontsize=3.4, fontface=3, align=True,
        )
        + geom_cladelab(
            data=dat3,
            mapping=aes(node="node", label="name", offset="offset", offset_text="offset_text", extend="extend"),
            barcolor="darkgrey", textcolor="darkgrey", barsize=3.2, fontsize=3.4, fontface=3, align=True,
        )
        + geom_strip(65, 71, "italic(B)", color="darkgrey", offset=0.0052, align=True, offset_text=0.00025, barsize=2.0, fontsize=3.4, parse=True)
        + geom_nodelab(aes(subset="node == 92", label="'*'"), color="black", nudge_x=-0.001, nudge_y=1, size=2.8)
        + geom_nodelab(aes(subset="node == 155", label="'*'"), color="black", nudge_x=-0.0003, nudge_y=-1, size=2.8)
        + geom_nodelab(aes(subset="node == 158", label="'95/92/1.00'"), color="black", nudge_x=-0.0001, nudge_y=-1, hjust=1, size=2.1)
        + geom_nodelab(aes(subset="node == 162", label="'98/97/1.00'"), color="black", nudge_x=-0.0001, nudge_y=-1, hjust=1, size=2.1)
        + geom_nodelab(aes(subset="node == 172", label="'*'"), color="black", nudge_x=-0.0003, nudge_y=-1, size=2.8)
    )

    tips_df = p.data[p.data["isTip"]]
    tips_recs = sorted(tips_df.to_records(), key=lambda r: float(r["y"]))
    tips_ordered = [str(r["label"]) for r in tips_recs]
    group_map = {str(r["label"]): r.get("group") for r in tips_recs}

    seq_bytes = [np.frombuffer(aln[lbl.split("|")[-1]].encode("ascii"), dtype=np.uint8) for lbl in tips_ordered]
    seq_mat = np.vstack(seq_bytes)
    seq_len = float(seq_mat.shape[1])

    seq1_col, seq2_col, dist_col, clade_col = [], [], [], []
    for j, s2 in enumerate(tips_ordered):
        pct = (seq_mat != seq_mat[j : j + 1]).sum(axis=1) / seq_len * 100.0
        g2 = group_map.get(s2)
        for s1, dv in zip(tips_ordered, pct):
            seq1_col.append(s1)
            seq2_col.append(s2)
            dist_col.append(float(dv))
            clade_col.append(g2)

    td = DataFrame({"seq1": seq1_col, "seq2": seq2_col, "dist": dist_col, "clade": clade_col})
    p2 = (
        p
        + geom_facet(panel="Sequence Distance", data=td, geom=geom_point, alpha=0.6, size=0.9, mapping=aes(x="dist", color="clade", shape="clade"))
        + geom_facet(panel="Sequence Distance", data=td, geom=geom_path, alpha=0.55, size=0.6, mapping=aes(x="dist", group="seq2", color="clade"))
        + scale_shape_manual(values=[1, 2, 3, 4, 5, 6, 7, 8], guide=False)
    )
    return facet_widths(p2, widths=[1.15, 1.0])


@register_figure(
    fig_id="fig_13_2",
    num="13.2",
    chapter=13,
    part=PART_IV,
    section="13.2 Displaying Different Symbolic Points for Bootstrap Values",
    title="Categorical bootstrap intervals encoded as white/grey/black circular node symbols",
    caption="Reproducing Figure 13.2 of treedata-book: right-ladderized Newick tree parsed with read_newick(node_label='support') and internal bootstrap intervals mapped to shape=21 filled points.",
    apis=["read_newick", "cut", "geom_point2", "scale_fill_manual", "rootnode"],
    size=(860, 720),
)
def _fig_13_2():
    from ggtree import (
        read_newick, system_file, rootnode, ggtree, aes, geom_tiplab,
        geom_point2, xlim, theme_tree, scale_fill_manual,
    )

    tree = read_newick(system_file("extdata", "TDbook", "text_RMI_tree.nwk"), node_label="support")
    root = rootnode(tree)
    p = (
        ggtree(tree, color="black", size=1.1, linetype=1, right=True)
        + geom_tiplab(size=2.6, hjust=-0.06, fontface="bold")
        + xlim(0, 0.09)
        + geom_point2(
            aes(subset="!isTip & node != root", fill="cut(support, c(0, 700, 900, 1000))"),
            shape=21,
            size=3.0,
        )
        + theme_tree(legend_position=(0.18, 0.20))
        + scale_fill_manual(
            values={"(900,1e+03]": "black", "(700,900]": "grey", "(0,700]": "white"},
            guide="legend",
            name="Bootstrap Percentage(BP)",
            breaks=["(900,1e+03]", "(700,900]", "(0,700]"],
            labels=["BP >= 90", "70 <= BP < 90", "BP < 70"],
        )
    )
    return p


@register_figure(
    fig_id="fig_13_3",
    num="13.3",
    chapter=13,
    part=PART_IV,
    section="13.3 Highlighting Different Groups",
    title="Circular phylogeny with groupOTU styling, radial clade highlights, and curved clade labels",
    caption="Reproducing Figure 13.3 of treedata-book: chicken (^ch) vs non-chicken lineages styled with groupOTU() color and linetype, node swaps via flip()/rotate(), radial geom_hilight() sectors, bootstrap > 50 labels, and curved clade annotations.",
    apis=["groupOTU", "flip", "rotate", "geom_hilight", "geom_cladelab", "geom_nodelab"],
    size=(920, 860),
)
def _fig_13_3():
    from ggtree import (
        read_tree, system_file, groupOTU, DataFrame, ggtree, aes,
        scale_color_manual, geom_nodepoint, geom_tiplab, flip, rotate,
        geom_hilight, geom_cladelab, geom_nodelab, theme,
    )

    mytree = read_tree(system_file("extdata", "TDbook", "tree_treenwk_30.4.19.nwk"))
    cls = [t for t in mytree.tip_label if t.startswith("ch")]
    labeltree = groupOTU(mytree, cls)

    p = (
        ggtree(labeltree, aes(color="group", linetype="group"), layout="circular")
        + scale_color_manual(values=["#efad29", "#63bbd4"])
        + geom_nodepoint(color="black", size=0.1)
        + geom_tiplab(size=2.0, color="black")
    )

    p2 = (
        p
        + flip(136, 110)
        + flip(141, 145)
        + rotate(141)
        + rotate(142)
        + rotate(160)
        + rotate(164)
        + rotate(131)
    )

    dat = DataFrame({
        "node": [110, 88, 156, 136],
        "fill": ["#229f8a", "#229f8a", "#229f8a", "#f9311f"],
    })
    p3 = p2 + geom_hilight(data=dat, mapping=aes(node="node", fill="I(fill)"), alpha=0.2, extendto=1.4)

    p4 = p3 + geom_cladelab(
        node=113,
        label="Avian-specific expansion",
        align=True,
        angle=-35,
        offset_text=0.05,
        hjust="center",
        fontsize=2.2,
        offset=0.2,
        barsize=0.2,
    )

    p5 = p4 + geom_nodelab(
        mapping=aes(x="branch", label="label", subset="!is.na(as.numeric(label)) & as.numeric(label) > 50"),
        size=2.0,
        color="black",
        nudge_y=0.6,
    )

    sub_df = DataFrame({"node": [114, 121], "name": ["Subgroup A", "Subgroup B"]})
    p6 = (
        p5
        + geom_cladelab(
            data=sub_df,
            mapping=aes(node="node", label="name"),
            align=True,
            offset=0.05,
            offset_text=0.03,
            hjust="center",
            barsize=0.2,
            fontsize=2.2,
            angle="auto",
            horizontal=False,
        )
        + theme(legend_position="none")
    )
    return p6


@register_figure(
    fig_id="fig_13_4",
    num="13.4",
    chapter=13,
    part=PART_IV,
    section="13.4 Phylogenetic Tree with Genome Locus Structure",
    title="BioNJ gene-content tree paired with aligned bacterial operon locus arrows",
    caption="Reproducing Figure 13.4 of treedata-book: BioNJ tree reconstructed from pairwise Jaccard gene-content distances across example_genes and paired via geom_facet(..., geom=geom_motif, on='genE', label='gene', align='left').",
    apis=["bionj", "read_table", "geom_facet", "geom_motif", "facet_widths", "scale_fill_brewer"],
    size=(920, 480),
)
def _fig_13_4():
    from ggtree import (
        read_table, system_file, bionj, ggtree, aes, geom_tiplab, xlim_tree,
        geom_facet, geom_motif, scale_fill_brewer, theme, element_blank, facet_widths,
    )

    example_genes = read_table(system_file("extdata", "TDbook", "example_genes.tsv"), header=True, sep="\t")
    genomes = []
    for g_name in example_genes["molecule"].tolist():
        if g_name not in genomes:
            genomes.append(g_name)
    gene_sets = {
        g_name: set(example_genes[example_genes["molecule"] == g_name]["gene"].tolist())
        for g_name in genomes
    }
    n = len(genomes)
    d = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i):
            gi, gj = gene_sets[genomes[i]], gene_sets[genomes[j]]
            jacc = len(gi & gj) / max(len(gi | gj), 1)
            d[i][j] = d[j][i] = 1.0 - jacc

    tree = bionj(d, labels=genomes)
    p = (
        ggtree(tree, branch_length="none")
        + geom_tiplab(size=3.0)
        + xlim_tree(5.5)
        + geom_facet(
            mapping=aes(xmin="start", xmax="end", fill="gene"),
            data=example_genes,
            geom=geom_motif,
            panel="Alignment",
            on="genE",
            label="gene",
            align="left",
        )
        + scale_fill_brewer(palette="Set3", name="gene")
        + theme(strip_text=element_blank())
    )
    return facet_widths(p, widths=[1, 2])

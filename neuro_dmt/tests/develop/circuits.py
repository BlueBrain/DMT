"""Available circuits for testing."""
import os
from neuro_dmt.library.bluebrain.circuit.models.sscx\
   import get_sscx_atlas_circuit_model
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model

circuits_path=\
        os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj68",
            "circuits")
sscx_circuit_model_2018=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj66",
            "circuits", "O1",
            "20180305",
            "CircuitConfig"),
        animal="mouse",
        region_label="region")
sscx_circuit_model=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            circuits_path, "O1",
            "20190307",
            "connectome/functional/All",
            "CircuitConfig"),
        animal="mouse",
        region_label="region",
        representative_subregion="mc2_Column")
sscx_circuit_model_nrn=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            circuits_path, "O1",
            "20190307",
            "connectome",
            "functional-nrn", "All",
            "CircuitConfig"),
        animal="mouse",
        region_label="region",
        representative_subregion="mc2_Column")
sscx_circuit_model_aff=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            circuits_path, "O1",
            "20190307",
            "connectome",
            "functional", "All",
            "CircuitConfig-aff"),
        animal="mouse",
        region_label="region",
        representative_subregion="mc2_Column")
sscx_circuit_model_eff=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            circuits_path, "O1",
            "20190307",
            "connectome",
            "functional", "All",
            "CircuitConfig-eff"),
        animal="mouse",
        region_label="region",
        representative_subregion="mc2_Column")


def IsocortexCircuitModel(
        region,
        hemisphere="left",
        direction="eff",
        use_backup_circuit=False):
    "..."
    assert\
        direction in {"eff", "aff"}
    assert\
        hemisphere in {"left", "right"}
    circuit_config_path=\
        os.path.join(
            circuits_path, "Isocortex",
            "20190307",
            "connectome/functional",
            "{}@{}".format(region, hemisphere),
            "CircuitConfig-{}".format(direction))\
            if not use_backup_circuit else\
               os.path.join(
                   circuits_path, "Isocortex",
                   "20190307",
                   "connectome/functional_backup",
                   "{}@{}".format(region, hemisphere),
                   "CircuitConfig-{}".format(direction))\

    return get_iso_cortex_circuit_model(
        circuit_config_path,
        animal="mouse",
        region_label="region",
        hemisphere=hemisphere,
        representative_subregion="SSp-ll@left")

all_mtypes=\
    sorted(list(
        sscx_circuit_model_nrn.cells.mtypes))
def top_(number, pandas_series):
    """..."""
    return\
        list(
            pandas_series\
              .value_counts()\
              .iloc[:number]\
              .index\
              .values\
              .astype(str))
            
interesting_mtypes=[
    mtype for layer in range(1, 7)
    for mtype in top_(
            2,
            sscx_circuit_model_nrn.cells.get(
                {"layer": layer},
                "mtype"))]
l5_tpcs=[
    mtype for mtype in all_mtypes if "L5_TPC" in mtype]
interesting_pathways={
    (pre_mtype, post_mtype)
    for pre_mtype in l5_tpcs
    for post_mtype in l5_tpcs}

def get_pathways(
        pre_mtypes,
        post_mtypes):
    """..."""
    return{
        (pre_mtype, post_mtype)
        for pre_mtype in pre_mtypes
        for post_mtype in post_mtypes}

L23_PCs=\
    [mtype for mtype in all_mtypes
     if ("L2" in mtype or "L3" in mtype or "L23" in mtype) and "PC" in mtype]
L4_PCs=\
    [mtype for mtype in all_mtypes
     if "L4" in mtype and "PC" in mtype]
L5_PCs=\
    [mtype for mtype in all_mtypes
     if "L5" in mtype and "PC" in mtype]
L6_PCs=\
    [mtype for mtype in all_mtypes
     if "L6" in mtype and "PC" in mtype]
pc_mtypes=\
    L23_PCs + L4_PCs + L5_PCs
eff_pathways={
    (X, Y)
    for X in ["L2_TPC:A", "L2_TPC:B"]
    for Y in L23_PCs + L4_PCs + L5_PCs}
aff_pathways={
    (Y,X) for X,Y in eff_pathways}
pc_pathways=\
    eff_pathways.union(
        aff_pathways)
connectome_algo_paper_pathways=\
    get_pathways(
        pre_mtypes=["L23_BTC", "L23_LBC", "L23_MC", "L23_NBC", "L23_SBC"],
        post_mtypes=L23_PCs)\
    .union(
        get_pathways(
            pre_mtypes=L23_PCs,
            post_mtypes=L23_PCs))\
    .union(
        get_pathways(
            pre_mtypes=L23_PCs,
            post_mtypes=["L23_LBC", "L23_NBC"]))\
    .union(
        get_pathways(
            pre_mtypes=["L23_LBC", "L23_SBC"],
            post_mtypes=["L23_LBC", "L23_SBC"]))\
    .union(
        get_pathways(
            pre_mtypes=["L4_BTC", "L4_LBC", "L4_MC", "L4_NBC", "L4_SBC"],
            post_mtypes=L4_PCs))\
    .union(
        get_pathways(
            pre_mtypes=L4_PCs,
            post_mtypes=["L4_LBC", "L4_NBC"]))\
    .union(
        get_pathways(
            pre_mtypes=["L4_LBC", "L4_SBC"],
            post_mtypes=["L4_LBC", "L4_SBC"]))\
    .union(
        get_pathways(
            pre_mtypes=["L4_SSC"],
            post_mtypes=L23_PCs))\
    .union(
        get_pathways(
            pre_mtypes=["L5_BTC", "L5_MC"],
            post_mtypes=L5_PCs))\
    .union(
        get_pathways(
            pre_mtypes=L5_PCs,
            post_mtypes=["L5_BTC", "L5_MC"]))\
    .union(
        get_pathways(
            pre_mtypes=L5_PCs,
            post_mtypes=L5_PCs))\
    .union(
        get_pathways(
            pre_mtypes=["L6_BTC"],
            post_mtypes=L6_PCs))\
    .union(
        get_pathways(
            pre_mtypes=L6_PCs,
            post_mtypes=L6_PCs))

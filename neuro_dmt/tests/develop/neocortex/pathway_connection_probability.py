"""Test develop pathway connection probability"""

from neuro_dmt.tests.develop.neocortex\
    import *
from neuro_dmt.measurement.parameter.spatial\
    import SomaDistance

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
pc_pathways={
    (X, Y)
    for X in ["L2_TPC:A", "L2_TPC:B"]
    for Y in L23_PCs + L4_PCs + L5_PCs}
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
def get_pathway_connection_probability_analysis(
        circuit_model,
        region,
        mtypes=all_mtypes,
        soma_distances=None,
        output_dir_path=os.getcwd(),
        sample_size=200,
        pathways=set(),
        upper_bound_soma_distance=300.,
        *args, **kwargs):
    """..."""
    regions=\
        AtlasRegion(values=[region])
    pre_mtypes=\
        Mtype(label="pre_mtype", values=mtypes)
    post_mtypes=\
        Mtype(label="post_mtype", values=mtypes)
    measurement_parameters=\
        [regions, pre_mtypes, post_mtypes, soma_distances]\
        if soma_distances else\
           [regions, pre_mtypes, post_mtypes]
    plotter_parameters=\
        ["pre_mtype", "post_mtype", "soma_distance"]\
        if soma_distances else\
           ["pre_mtype", "post_mtype"]
    return\
        PathwayConnectionProbabilityAnalysis(
            animal="mouse",
            brain_region=circuit_model.brain_region,
            measurement_parameters=measurement_parameters,
            plotted_parameters=plotter_parameters,
            cell_group_parameter=Mtype(values=mtypes),
            pathway_parameters=[
                pre_mtypes, post_mtypes],
            output_dir_path=output_dir_path,
            adapter=BlueBrainModelAdapter(
                brain_region=circuit_model.brain_region,
                sample_size=sample_size,
                sampled_box_shape=50. * np.ones(3),
                spatial_random_variate=RandomRegionOfInterest,
                model_label="in-silico"),
            pathways_to_analyze=pathways,
            *args, **kwargs)









from neuro_dmt.tests.develop.neocortex.pathway_connection_probability\
    import *
from neuro_dmt.analysis.circuit.connectome.by_mtype.efferent_connection_count\
    import EfferentConnectionCount

def get_efferent_connection_count_analysis(
        circuit_model,
        region,
        mtypes=all_mtypes,
        soma_distance=SomaDistance(0., 2000., 10),
        output_dir_path=os.getcwd(),
        sample_size=200,
        pathways=set(),
        *args, **kwargs):
    """..."""
    regions=\
        AtlasRegion(values=[region])
    pre_mtypes=\
        Mtype(label="pre_mtype", values=mtypes)
    post_mtypes=\
        Mtype(label="post_mtype", values=mtypes)
    measurement_parameters=\
        [regions, pre_mtypes, post_mtypes, soma_distance]
    plotted_parameters=\
        ["pre_mtype", "post_mtype", "soma_distance"]
    return\
        EfferentConnectionCount(
            animal="mouse",
            brain_region=circuit_model.brain_region,
            measurement_parameters=measurement_parameters,
            plotted_parameters=plotted_parameters,
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









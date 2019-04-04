"""Test develop pathway connection probability"""

from neuro_dmt.tests.develop.neocortex\
    import *
from neuro_dmt.measurement.parameter.spatial\
    import SomaDistance

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









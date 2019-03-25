"""Test develop pathway connection probability"""

from neuro_dmt.tests.develop.neocortex\
    import *
from neuro_dmt.measurement.parameter.spatial\
    import SomaDistance

all_mtypes=\
    sorted(list(
        sscx_circuit_model_nrn.cells.mtypes))
def get_pathway_connection_probability_analysis(
        circuit_model,
        region,
        mtypes=all_mtypes,
        by_distance=True,
        output_dir_path=os.getcwd(),
        sample_size=200,
        *args, **kwargs):
    """..."""
    regions=\
        AtlasRegion(values=[region])
    pre_mtypes=\
        Mtype(label="pre_mtype", values=mtypes)
    post_mtypes=\
        Mtype(label="post_mtype", values=mtypes)
    soma_distances=\
        SomaDistance(0., 500., 10)\
        if by_distance else\
           SomaDistance(0., 300., 1)
    return\
        PathwayConnectionProbabilityAnalysis(
            animal="mouse",
            brain_region=circuit_model.brain_region,
            measurement_parameters=[
                regions, pre_mtypes, post_mtypes, soma_distances],
            plotted_parameters=[
                "pre_mtype", "post_mtype", "soma_distance"],
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
            *args, **kwargs)



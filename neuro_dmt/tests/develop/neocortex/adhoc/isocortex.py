"""Adhoc tests for the iso-cortex"""
import itertools
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.tests.develop.neocortex.adhoc\
    import *

logger=\
    Logger(
        """Adhoc isocortex tests""",
        level=Logger.level.DEBUG)

def run_isocortex(
        region,
        direction,
        sample_size=1000,
        as_distribution=False,
        filename_suffix=""):
    """Get number of connections in region."""

    output_directory=\
        os.path.join(
            output_path,
            region,
            direction)
    if not os.path.exists(output_directory):
        os.makedirs(
            output_directory)
    circuit=\
        Circuit(
            iso_circuit_config(
                region,
                direction=direction))

    def __random_sample(gids):
        """..."""
        if len(gids) == 0:
            return np.array([])
        return\
            np.random.choice(
                gids,
                sample_size)

    def __random_post_gids(gid):
        return\
            __random_sample(
                circuit.connectome\
                       .efferent_gids(gid))

    def get_pathway_strength(
            pre_mtype):
        """..."""
        logger.info(
            "Get strengths for pathways coming out of {}"\
            .format(pre_mtype))
        empty_dataframe=\
            pd.DataFrame([], columns=["strength"])
        pre_gids=\
            circuit.cells.ids(
                {Cell.MTYPE: pre_mtype,
                 Cell.REGION: region})
        if len(pre_gids) == 0:
            return empty_dataframe
        post_mtypes=\
            circuit.cells.get(
                np.hstack(
                    circuit.connectome.efferent_gids(pre_gid)
                    for pre_gid in pre_gids),
                Cell.MTYPE)
        number_connections=\
            len(post_mtypes)
        if number_connections == 0:
            return empty_dataframe
        logger.info(
            "Number of efferent connections for {}: {}"\
            .format(
                pre_mtype,
                len(post_mtypes)))
        post_mtype_counts=[
            (mtype, count)
            for mtype, count in post_mtypes.value_counts().items()]
        dataframe=\
            pd.DataFrame(
                {"strength": np.array([
                    count for _,count in post_mtype_counts])},
                index=pd.MultiIndex.from_tuples(
                    tuples=[(pre_mtype, post_mtype)
                            for post_mtype,_ in post_mtype_counts],
                    names=["pre_mtype", "post_mtype"]))
        return\
            dataframe if not as_distribution\
            else dataframe / number_connections
                
    result=\
        pd.concat(
            get_pathway_strength(pre_mtype)
            for pre_mtype in mtypes)
    result.to_csv(
        os.path.join(
            output_directory,
            "pathway_strength_region_{}{}.csv"\
            .format(
                region,
                filename_suffix)))
    return result


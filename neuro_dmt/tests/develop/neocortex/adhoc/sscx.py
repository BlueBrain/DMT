"""Adhoc tests for the sscx O1 circuit."""

import itertools
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.tests.develop.neocortex.adhoc\
    import *

logger=\
    Logger(
        """Adhoc sscx O1 tests""",
        level=Logger.level.DEBUG)

def run_sscx(
        connectome_type,
        direction,
        filename_suffix="",
        column=None,
        as_distribution=False):
    """Get number of connections in O1 (SSCx)."""
    output_directory=\
        os.path.join(
            output_path,
            "sscx")
    if not os.path.exists(output_directory):
        os.makedirs(
            output_directory)
    circuit=\
        Circuit(
            sscx_circuit_config(
                connectome_type=connectome_type,
                direction=direction))

    def get_cell_type(mtype):
        """..."""
        if column:
            return {Cell.MTYPE: mtype,
                    Cell.REGION: column}
        return {Cell.MTYPE: mtype}

    def get_pathway_strength(
            pre_mtype):
        """pathway strength distribution of a given pre mtype"""
        logger.info(
            logger.get_source_info(),
            "Get pathway strengths for pre_mtype {}".format(pre_mtype))
        pre_gids=\
            circuit.cells.ids(
                get_cell_type(pre_mtype))
        if len(pre_gids) == 0:
            return pd.DataFrame([], columns=["strength"])
        post_mtypes=\
            circuit.cells.get(
                np.hstack(
                    circuit.connectome.efferent_gids(pre_gid)
                    for pre_gid in pre_gids),
                Cell.MTYPE)
        logger.info(
            "Number of efferent connections for {}: {}"\
            .format(
                pre_mtype,
                len(post_mtypes)))
        post_mtype_counts=[
            (post_mtype, count)
            for post_mtype, count in post_mtypes.value_counts().items()]
        pathway_strength=\
            pd.DataFrame(
                {"strength": np.array([
                    count for _,count in post_mtype_counts])},
                index=pd.MultiIndex.from_tuples(
                    tuples=[(pre_mtype, post_mtype)
                            for post_mtype, _ in post_mtype_counts],
                    names=["pre_mtype", "post_mtype"]))
        return\
            pathway_strength if not as_distribution\
            else pathway_strength / len(post_mtypes)

    result=\
        pd.concat([
            get_pathway_strength(pre_mtype)
            for pre_mtype in mtypes])

    result.to_csv(
        os.path.join(
            output_directory,
            "O1_pathway_strength_region{}.csv".format(filename_suffix)))

    return result

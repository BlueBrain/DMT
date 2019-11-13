import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.field import lazyfield
from .import PathwayProperty

logger = Logger(client=__file__)

class ConnectionProbability(PathwayProperty):
    phenomenon = "connection_probability"
    aggregators_inner = ["size", "sum"]
    aggregators_outer = "sum"
    measurement_label = "connection_probability"
    columns = {"size": "pairs_total", "sum": "pairs_connected"}
    measured_variables = ["pairs"]
    other_grouping_variables = []

    @lazyfield
    def empty(self):
        """
        The value to return when there is no data.
        """
        return pd.Series({
            "pairs_total": 0,
            "pairs_connected": 0,
            self.phenomenon: 0})

    @lazyfield
    def definition(self):
        def _connection_probability(summary):
            return summary.pairs_connected/summary.pairs_total
        return {
            self.phenomenon: _connection_probability}

    def soma_distance(self, xcell, ycell):
        """
        Soma distance between cells.

        Arguments
        -------------------------
        xcell / ycell : A single cell (i.e. a pandas.Series),
        ~               or a collection of cells (i.e. a pandas.DataFrame)
        """
        XYZ = ["x", "y", "z"]
        return np.linalg.norm(xcell[XYZ] - ycell[XYZ], axis=1)

    def get_pairs(self,
            pre_synaptic_cells,
            post_synaptic_cells,
            upper_bound_soma_distance=None,
            *args, **kwargs):
        """

        Arguments
        --------------
        pre_synaptic_cells : pandas.DataFrame
        post_synaptic_cells : pandas.DataFrame
        *args, **kwargs : Accommodate super's call to `get`.

        Returns
        --------------
        A generator of data-frames that provides values for individual
        pairs `(pre_synaptic_cell, post_synaptic_cell)`.
        """
        logger.study(
            logger.get_source_info(),
            """
            Get connection probability for
            {} pre synaptic cells
            {} post synaptic cells
            """.format(
                pre_synaptic_cells.shape[0],
                post_synaptic_cells.shape[0]))
        for count, (_, post_cell) in enumerate(post_synaptic_cells.iterrows()):
            logger.info(
                logger.get_source_info(),
                """
                Get all pairs for post cell {} / {} ({})
                """.format(
                    post_cell,
                    post_synaptic_cells.shape[0],
                  count / post_synaptic_cells.shape[0]))
            pairs = pre_synaptic_cells\
                .drop(
                    columns="gid"
                ).reset_index(
                    drop=True
                ).assign(
                    pairs=np.in1d(
                        pre_synaptic_cells.gid.values,
                        self.circuit_model.connectome.afferent_gids(
                            post_cell.gid)))
            if upper_bound_soma_distance is not None:
                soma_distance = self\
                    .soma_distance(
                        pre_synaptic_cells,
                        post_cell)
                pairs = pairs[
                    soma_distance < upper_bound_soma_distance
                ].reset_index(
                    drop=True)
            post_cell_info = pd.DataFrame(
                pairs.shape[0] * [post_cell.drop("gid")]
            ).reset_index(
                drop=True)
            yield pd.concat(
                [pairs, post_cell_info],
                axis=1
            ).reset_index(
                drop=True)


class ConnectionProbabilityBySomaDistance(ConnectionProbability):
    """
    Get connection probability between cells in a pathway by soma-distance.
    """
    measured_variables = ["pairs", "soma_distance"]
    other_grouping_variables = ["soma_distance"]
    soma_distance_bin_size = 100.

    @lazyfield
    def empty(self):
        """
        The value to return when there is no data.
        """
        return pd.DataFrame(
            [],
            columns=["pairs_total", "pairs_connected", self.phenomenon],
            index=pd.Index([], name="soma_distance"))


    def soma_distance(self, xcell, ycell):
        """
        Soma distance between cells.

        Arguments
        -------------------------
        xcell / ycell : A single cell (i.e. a pandas.Series),
        ~               or a collection of cells (i.e. a pandas.DataFrame)
        """
        XYZ = ["x", "y", "z"]
        distance = np.linalg.norm(xcell[XYZ] - ycell[XYZ], axis=1)
        bin_size = self.soma_distance_bin_size
        bin_starts = bin_size * np.floor(distance / bin_size)
        #bin_ends = bin_size + bin_starts
        #return np.vstack([bin_start, bin_start + bin_size]).transpose()
        return [(bin_start, bin_start + bin_size) for bin_start in bin_starts]

    def get_pairs(self,
            pre_synaptic_cells,
            post_synaptic_cells,
            *args, **kwargs):
        """..."""

        logger.study(
            logger.get_source_info(),
            """
            Get connection probability among
            {} pre-synaptic cells
            {} post-synaptic cells
            """.format(
                pre_synaptic_cells.shape[0],
                post_synaptic_cells.shape[0]))
        for count, (_, post_cell) in enumerate(post_synaptic_cells.iterrows()):
            logger.ignore(
                logger.get_source_info(),
                """
                Get all pairs for post cell {} / {} ({})
                """.format(
                    post_cell,
                    post_synaptic_cells.shape[0],
                    count / post_synaptic_cells.shape[0]))
            pairs = pre_synaptic_cells\
                .drop(
                    columns="gid"
                ).reset_index(
                    drop=True
                ).assign(
                    pairs=np.in1d(
                        pre_synaptic_cells.gid.values,
                        self.circuit_model.connectome.afferent_gids(
                            post_cell.gid)),
                    soma_distance=self.soma_distance(
                        pre_synaptic_cells,
                        post_cell))
            post_cell_info = pd.DataFrame(
                pre_synaptic_cells.shape[0] * [post_cell.drop("gid")]
            ).reset_index(
                drop=True)
            yield pd.concat(
                [pairs, post_cell_info],
                axis=1)




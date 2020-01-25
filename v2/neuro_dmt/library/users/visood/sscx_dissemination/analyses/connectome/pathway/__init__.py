"""
Abstraction of a pathway and its properties.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from collections import OrderedDict, namedtuple
import functools
from enum import Enum
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields
from neuro_dmt import terminology


LOGGER = Logger(client=__file__)

XYZ = ["x", "y", "z"]

class PathwaySummary(WithFields):
    """
    Compute and store a circuit's pathway properties.
    This class will be used by a circuit analysis.

    Data types for circuit artefacts
    ---------------------------------
    Circuit analyses implemented here work extensively with `pandas`.
    Thus `pandas.Series` is used to represent a cell-type,
    and a `pandas.DataFrame` for a collection of cell-types.
    """
    circuit_model = Field(
        """
        The circuit model for which this `PathwaySummary` has been defined.
        """)
    adapter = Field(
        """
        Adapter of the model analyzed.
        """)

    @lazyfield
    def circuit_cells(self):
        """
        Cells of the circuit model being analyzed.
        """
        return self.circuit_model.cells

    @lazyfield
    def circuit_connectome(self):
        """
        Connectome of the circuit model being analyzed.
        """
        return self.circuit_model.connectome

    def get_pairs(self,
            pre_synaptic_cells,
            post_synaptic_cells,
            upper_bound_soma_distance=None,
            with_soma_distance=False,
            *args, **kwargs):
        """
        Arguments
        -----------
        pre_synaptic_cells ::  pandas.DataFrame with cell properties as columns
        post_synaptic_cells :: pandas.DataFrame with cell properties as columns
        """
        LOGGER.study(
            LOGGER.get_source_info(),
            """
            Get connection probability for
            {} pre-synaptic cells
            {} post-synaptic cells
            """.format(
                pre_synaptic_cells.shape[0],
                post_synaptic_cells.shape[0]))
        for count, (_, post_cell) in enumerate(post_synaptic_cells.iterrows()):
            LOGGER.info(
                LOGGER.get_source_info(),
                """
                Get all pairs for cell {} / {} ({})
                """.format(
                    post_cell,
                    post_synaptic_cells.shape[0],
                    count / post_synaptic_cells.shape[0]))
            pairs =\
                pre_synaptic_cells\
                .reset_index(drop=True)\
                .assign(
                    number_pairs_connected=self.adapter.are_afferently_connected(
                        self.circuit_model, pre_synaptic_cells, post_cell),
                    number_pairs_total=1.)
            if upper_bound_soma_distance is not None:
                soma_distance =\
                    self.adapter.get_soma_distance(
                        self.circuit_model,
                        pre_synaptic_cells,
                        post_cell)
                pairs =\
                    pairs[
                        soma_distance < upper_bound_soma_distance
                    ].reset_index(drop=True)
            if with_soma_distance:
                pairs =\
                    pairs.assign(
                        soma_distance=self.adapter.get_soma_distance(
                            self.circuit_model,
                            pre_synaptic_cells,
                            post_cell))
            post_cell_info =\
                pd.DataFrame(pairs.shape[0] * [post_cell.drop("gid")])\
                  .reset_index(drop=True)
            yield\
                pd.concat([pairs, post_cell_info], axis=1)\
                  .reset_index(drop=True)




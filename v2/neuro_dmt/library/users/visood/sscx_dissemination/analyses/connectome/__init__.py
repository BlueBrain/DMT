"""
Analyses of the circuit's connectome.
"""

import os
from copy import deepcopy
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.model.interface import Interface
from dmt.tk.field import WithFields, Field, lazyfield
from dmt.tk.author import Author
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.plotting import Bars, LinePlot
from dmt.tk.plotting.multi import MultiPlot
from dmt.tk.parameters import Parameters
from dmt.data.observation import measurement
from neuro_dmt import terminology
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.reporting import\
    CircuitAnalysisReport,\
    CheetahReporter
from neuro_dmt.data import rat
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid
from neuro_dmt.models.bluebrain.circuit.adapter.adapter import measurement_method
from .pathway import PathwaySummary


LOGGER = Logger(client=__file__, level="DEBUG")

class ConnectomeAnalysisSuite(WithFields):
    """
    Analyze the connectome of a brain circuit model.
    """
    sample_size = Field(
        """
        Number of individual sample measurements for each set of parameter
        values.
        """,
        __default_value__=100)
    path_reports = Field(
        """
        Location where the reports will be posted.
        """,
        __default_value__=os.path.join(os.getcwd(), "reports"))
    pre_synaptic_cell_type = Field(
        """
        An object describing the group of pre-synaptic cells to be investigated
        in these analyses.  Interpretation of the data in this object will be 
        delegated to the adapter used for the model analyzed.
        Here are some guidelines when this object may is a dictionary. 
        Such a dictionary will have cell properties such as region, layer,
        mtype,  and etype as keys. Each key may be given either a single value 
        or an iterable of values. Phenomena must be evaluated for each of these
        values and collected as a pandas.DataFrame.
        """)
    post_synaptic_cell_type = Field(
        """
        An object describing the group of post-synaptic cells to be investigated
        in these analyses.  Interpretation of the data in this object will be 
        delegated to the adapter used for the model analyzed.
        Here are some guidelines when this object may is a dictionary. 
        Such a dictionary will have cell properties such as region, layer,
        mtype,  and etype as keys. Each key may be given either a single value 
        or an iterable of values. Phenomena must be evaluated for each of these
        values and collected as a pandas.DataFrame.
        """)

    class AdapterInterface(Interface):
        """
        Document the methods that will be used by this analysis to measure a
        circuit model. Users must adapt the functionality of their circuit model
        to provide the methods defined in this `Interface`. They may implement
        their adapter as a class or a module.
        """
        def get_provenance(self, circuit_model):
            """
            Provide a dictionary with following keys:
            
            1. label: that names the circuit model
            2. authors: group that built the circuit model
            3. release_date: when the circuit model was released in its final form
            4. location: a URI from where the circuit model can be loaded
            5. animal: whose brain was modeled
            6  age: of the animal at which the brain was modeled
            7. brain_region: name of the region in the brain modeled 
            """
            raise NotImplementedError
        
        def get_brain_regions(self, circuit_model):
            """
            A list of named regions in the `circuit_model`.
            """
            raise NotImplementedError
        
        def get_layers(self, circuit_model):
            """
            A list of layers in the `circuit_model`
            """
            raise NotImplementedError

        def get_mtypes(self, circuit_model):
            """
            Get a 1D numpy array that provides the mtypes in the circuit model.

            Arugments
            ---------------
            circuit_model :: The circuit model to analyze.
            """
            raise NotImplementedError

        def get_pathways(self,
                circuit_model=None,
                pre_synaptic_cell_type=None,
                post_synaptic_cell_type=None):
            """
            Arguments
            ------------
            pre_synaptic_cell_type ::  An object describing the group of
            ~  pre-synaptic cells to be investigated in these analyses.
            ~  Interpretation of the data in this object 
            ~  will be  delegated to the adapter used for the model analyzed.
            ~  Here are some guidelines when this object may is a dictionary. 
            ~  Such a dictionary will have cell properties such as region, ,
            ~  layer mtype,  and etype as keys. Each key may be given either a 
            ~  single value or an iterable of values. Phenomena must be 
            ~  evaluated for each of these values and collected as a 
            ~  pandas.DataFrame.
            post_synaptic_cell_type :: An object describing the group of
            ~  post-synaptic cells to be investigated in these analyses.
            ~  Interpretation of the data in this object 
            ~  will be  delegated to the adapter used for the model analyzed.
            ~  Here are some guidelines when this object may is a dictionary. 
            ~  Such a dictionary will have cell properties such as region, ,
            ~  layer mtype,  and etype as keys. Each key may be given either a 
            ~  single value or an iterable of values. Phenomena must be 
            ~  evaluated for each of these values and collected as a 
            ~  pandas.DataFrame.

            Returns
            ------------
            pandas.DataFrame with nested columns, with two columns
            `pre_synaptic` and `post_synaptic` at the 0-th level.
            Under each of these two columns should be one column each for the
            cell properties specified in the `cell_group` when it is a set,
            or its keys if a mapping.
            ~   1. When `cell_group` is a set of cell properties, pathways
            ~      between all possible values of these cell properties.
            ~   2. When `cell_group` is a mapping, pathways between cell groups
            ~      that satisfy the mapping's values.
            """
            raise NotImplementedError

        def are_afferently_connected(self,
                circuit_model,
                pre_synaptic_cells,
                post_synaptic_cell):
            """
            Which of the pre-synaptic cells are afferent connections of a
            post_synaptic_cell?
            
            Arguments
            ------------
            pre_synaptic_cells :: pandas.DataFrame with columns that contain
            ~                     cell properties, with `gid` each cells unique id.
            post_synaptic_cell :: pandas.Series containing cell property,
            ~                     with `gid` the cell's unique id.
            """
            raise NotImplementedError


    def measurement_number_afferent_connections(self,
            circuit_model,
            adapter,
            pre_synaptic_cell_type,
            post_synaptic_cell_type)

    @lazyfield
    def analysis_number_afferent_connections(self):
        """
        Analyze number of incoming connections.
        """
        return BrainCircuitAnalysis(
            introduction="""
            A circuit model should reproduce experimentally measured number
            of incoming connections of a cell. Here we analyze number of
            afferent connections to cells of a given (post-synaptic) cell-type,
            grouped by the cell-types of the post-synaptic cells. For example,
            if cell-type is defined by a cell's mtype, then given a
            pre-synaptic-mtype-->post-synaptic-mtype pathway, we analyze number 
            of afferent connections incident upon the group of cells with the
            given post-synaptic mtype that originate from the group of all cells 
            with the given pre-synaptic mtype.
            """,
            methods="""
            For each of pre-synaptic and post-synaptic cell type in the given
            pathway {}, cells were sampled. Connection probability was computed
            as the number of cell pairs that were connected to the total number
            of pairs.""".format(self.sample_size),
            phenomenon=Phenomenon(
                "Connection Probability",
                """
                Probability that two neurons in a pathway are connected.
                While most of the interest will be in `mtype-->mtype` pathways,
                we can define a pathway as a any two group of cells, one on 
                the afferent side, the other on the efferent side of a (possible)
                synapse. Given the pre-synaptic and post-synaptic cell types (groups),
                connection probability counts the fraction of connected pre-synaptic,
                post-synaptic pairs. Connection probability may be calculated as a 
                function of the soma-distance between the cells in a pair, in which
                case the measured quantity will be vector-valued data such as a 
                `pandas.Series`.
                """),
            AdapterInterface=self.AdapterInterface,
            measurement_parameters=Parameters())



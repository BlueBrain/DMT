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

def add_counter(log_after=100):
    """decorate..."""
    def _decorator(method):
        method.n_calls = 0

        def _decorated(*args, **kwargs):
            result = method(*args, **kwargs)
            method.n_calls += 1
            if method.n_calls % log_after == 0:
                LOGGER.info(
                    """{} call count : {}""".format(
                        method.__name__,
                        method.n_calls))
            return result

        return _decorated

    return _decorator

class ConnectomeAnalysesSuite(WithFields):
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
    cell_mtypes = Field(
        """
        Cell type for which pathways will be analyzed.
        """,
        __default_value__=[])
    pre_synaptic_mtypes = Field(
        """
        Cell type for which pathways will be analyzed.
        """,
        __default_value__=[])
    post_synaptic_mtypes = Field(
        """
        Cell type for which pathways will be analyzed.
        """,
        __default_value__=[])

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

        def get_adjacency_list(self,
                pre_synaptic_cells,
                post_synaptic_cells,
                upper_bound_soma_distance=None,
                with_soma_distance=False):
            """
            arguments
            --------------
            pre_synaptic_cells : pandas.dataframe
            post_synaptic_cells : pandas.dataframe
            
            returns
            --------------
            a generator of data-frames that provides values for individual
            pairs `(pre_synaptic_cell, post_synaptic_cell)`.
            """
            raise NotImplementedError

        def get_soma_distance(self,
                circuit_model,
                cell,
                cell_group):
            """
            Soma distance of a cell from a group of cells.
            """
            raise NotImplementedError

        def get_afferent_gids(self,
                circuit_model,
                post_synaptic_cell):
            """
            Get ids of the cells afferently connected to a post-synaptic cell.

            """
            raise NotImplementedError


    def pre_synaptic_cell_type(self,
            circuit_model,
            adapter):
        """..."""
        return self.pre_synaptic_mtypes\
            if len(self.pre_synaptic_mtypes) > 0 else\
               adapter.get_mtypes(circuit_model)

    def post_synaptic_cell_type(self,
            circuit_model,
            adapter):
        """..."""
        return self.post_synaptic_mtypes\
            if len(self.post_synaptic_mtypes) > 0 else\
               adapter.get_mtypes(circuit_model)

    @lazyfield
    def parameters_pre_synaptic_cell_mtypes(self):
        """..."""
        def _mtypes(adapter, circuit_model):
            mtypes =\
                self.cell_mtypes\
                if len(self.cell_mtypes) > 0 else\
                   adapter.get_mtypes(circuit_model)
            return pd.DataFrame({
                ("pre_synaptic_cell", "mtype"): mtypes})
        return\
            Parameters(_mtypes)

    @lazyfield
    def parameters_post_synaptic_cell_mtypes(self):
        """..."""
        def _mtypes(adapter, circuit_model):
            """..."""
            mtypes =\
                self.cell_mtypes\
                if len(self.cell_mtypes) > 0 else\
                   adapter.get_mtypes(circuit_model)
            return pd.DataFrame({
                ("post_synaptic_cell", "mtype"): mtypes})
        return\
            Parameters(_mtypes)

    @staticmethod
    def _at(role_synaptic):
        """..."""
        def _rename_column(variable):
            return "{}_{}".format(role_synaptic, variable)
        return _rename_column

    @measurement_method("""
    Number of afferent connections are computed as a function of the
    post-synaptic cell type. Cell-type can be any defined by the values of
    a neuron's properties, for example layer, mtype, and etype. A group of
    cells are sampled with the given (post-synaptic) cell-type. For each of
    these post-synaptic cells, incoming connections from all other neurons are
    grouped by cell type of the neuron where they start (i.e. their pre-synaptic
    cell-type) and their soma-dstiance from the post-synaptic cell under .
    consideration Afferent connection count or in-degree of a post-synaptic 
    cell is defined as the number of pre-synaptic cells in each of these groups.
    """)
    @add_counter(1)
    def number_afferent_connections(self,
            circuit_model,
            adapter,
            post_synaptic_cell,
            pre_synaptic_cell_type_specifier=None,
            by_soma_distance=True,
            bin_size=100,
            sampling_methodology=terminology.sampling_methodology.random):
        """
        Number of afferent connections incident on the post-synaptic cells,
        originating from the pre-synaptic cells.

        Arugments
        --------------
        post_synaptic_cell :: An object describing the group of
        ~   post-synaptic cells to be investigated in these analyses.
        ~   Interpretation of the data in this object will be 
        ~   delegated to the adapter used for the model analyzed.
        ~   Here are some guidelines when this object may is a dictionary. 
        ~    Such a dictionary will have cell properties such as region, layer,
        ~    mtype,  and etype as keys. Each key may be given either a single 
        ~    value or an iterable of values. Phenomena must be evaluated for 
        ~    each of these values and collected as a pandas.DataFrame.
        """
        if pre_synaptic_cell_type_specifier is None:
            pre_synaptic_cell_type_specifier =\
                frozenset(post_synaptic_cell.keys())

        def _prefix_pre_synaptic(variable):
            return\
                ("pre_synaptic_cell", variable)\
                if variable in pre_synaptic_cell_type_specifier\
                   else variable

        variables_groupby =[
            _prefix_pre_synaptic(variable)
            for variable in pre_synaptic_cell_type_specifier]
        if by_soma_distance:
            variables_groupby.append("soma_distance")

        circuit_cells =\
            adapter.get_cells(circuit_model)

        def _summary_afferent(post_synaptic_cell):
            """..."""
            def _soma_distance(pre_cells):
                distance =\
                    adapter.get_soma_distance(
                        circuit_model,
                        pre_cells,
                        post_synaptic_cell)
                bin_starts =\
                    bin_size * np.floor(distance / bin_size)
                return [
                    bin_start + bin_size / 2. for bin_start in bin_starts]

            gids_afferent =\
                adapter.get_afferent_gids(
                    circuit_model,
                    post_synaptic_cell)
            variables_measurement =\
                dict(number_connections_afferent=1.,
                     soma_distance=_soma_distance)\
                     if by_soma_distance else\
                        dict(number_connections_afferent=1.)
            return \
                circuit_cells.loc[gids_afferent]\
                             .assign(**variables_measurement)\
                             .rename(columns=_prefix_pre_synaptic)\
                             [variables_groupby + ["number_connections_afferent"]]\
                             .groupby(variables_groupby)\
                             .agg("sum")
        post_synaptic_cells =\
            adapter.get_cells(
                circuit_model,
                **post_synaptic_cell)
        sample_post_synaptic_cells =\
            post_synaptic_cells.sample(n=self.sample_size)\
            if sampling_methodology == terminology.sampling_methodology.random\
               else post_synaptic_cells
        dataframe =\
            pd.concat([
                _summary_afferent(cell)
                for _, cell in sample_post_synaptic_cells.iterrows()])
        return\
            dataframe.number_connections_afferent

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
                "Number Afferent Connections",
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
            measurement_parameters=self.parameters_post_synaptic_cell_mtypes,
            sample_measurement=self.number_afferent_connections,
            measurement_collection=measurement.collection.series_type,
            plotter=LinePlot(
                xvar="soma_distance",
                xlabel="Soma Distance",
                yvar="number_afferent_connections",
                ylabel="Mean number of afferent connections",
                gvar=("pre_synaptic_cell", "mtype"),
                fvar=("post_synaptic_cell", "mtype"),
                drawstyle="steps-mid"),
            report=CircuitAnalysisReport)


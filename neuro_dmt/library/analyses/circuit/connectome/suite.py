"""
Analyses of the circuit's connectome.
"""

import os
from copy import deepcopy
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.journal.utils import count_number_calls
from dmt.model.interface import Interface
from dmt.tk.field import WithFields, Field, LambdaField, lazyfield
from dmt.tk.author import Author
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.plotting import LinePlot, HeatMap
from dmt.tk.plotting.multi import MultiPlot
from dmt.tk.parameters import Parameters
from dmt.data.observation import measurement
from neuro_dmt import terminology
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.reporting import\
    CircuitAnalysisReport,\
    CheetahReporter
from neuro_dmt.utils import measurement_method
from neuro_dmt.utils.geometry import Cuboid
from neuro_dmt.analysis.circuit.tools import PathwayMeasurement

LOGGER = Logger(client=__file__, level="DEBUG")


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
        Arguments
        --------------
        pre_synaptic_cells : pandas.dataframe
        post_synaptic_cells : pandas.dataframe
        
        Returns
        --------------
        A generator of data-frames that provides values for individual
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


class ConnectomeAnalysesSuite(WithFields):
    """
    Analyze the connectome of a brain circuit model.
    """

    AdapterInterface = AdapterInterface

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
    pre_synaptic_mtypes = LambdaField(
        """
        Pre synaptic cell type for which pathways will be analyzed.
        """,
        lambda self: self.cell_mtypes)
    post_synaptic_mtypes = LambdaField(
        """
        Post synaptic cell type for which pathways will be analyzed.
        """,
        lambda self: self.cell_mtypes)

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
                self.pre_synaptic_mtypes\
                if len(self.pre_synaptic_mtypes) > 0 else\
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
                self.post_synaptic_mtypes\
                if len(self.post_synaptic_mtypes) > 0 else\
                   adapter.get_mtypes(circuit_model)
            return pd.DataFrame({
                ("post_synaptic_cell", "mtype"): mtypes})
        return\
            Parameters(_mtypes)

    @staticmethod
    def _at(role_synaptic, as_tuple=True):
        """..."""
        def _rename(variable):
            return\
                "{}_{}".format(role_synaptic, variable)\
                if not as_tuple else\
                   (role_synaptic, variable)

        return _rename

    @staticmethod
    def get_soma_distance_bins(
            circuit_model,
            adapter,
            cell,
            cell_group,
            bin_size=100.,
            bin_mids=True):
        """
        Get binned distance of `cell`'s soma from soma of all the cells in
        `cell_group`.
        """
        distance =\
            adapter.get_soma_distance(
                circuit_model,
                cell, cell_group)
        bin_starts =\
            bin_size * np.floor(distance / bin_size)
        return\
            [bin_start + bin_size / 2. for bin_start in bin_starts]\
            if bin_mids else\
               [[bin_start, bin_size] for bin_start in bin_starts]

    @staticmethod
    def get_random_cells(
            circuit_model,
            adapter,
            cell_type,
            number=1):
        """
        Get a random cell with the given `cell_type`.

        Arguments
        ------------
        cell_type :: pandas.Series<CellProperty>
        """
        group_cells =\
            adapter.get_cells(circuit_model, **cell_type)
        return\
            group_cells if group_cells.shape[0] < number\
            else group_cells.sample(n=number)

    @staticmethod
    def random_cell(
            circuit_model,
            adapter,
            cell_type):
        """Only one random cell"""
        return\
            ConnectomeAnalysesSuite.get_random_cells(
                circuit_model, adapter,
                cell_type,
                number=1
            ).iloc[0]

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
    @count_number_calls(LOGGER)
    def number_connections_afferent_verbose(self,
            circuit_model,
            adapter,
            cell,
            cell_properties_groupby,
            by_soma_distance=True,
            bin_size_soma_distance=100.,
            with_cell_propreties_as_index=True):
        """
        Just an example, for now.
        """


        variable = "number_connections_afferent"
        value = lambda cnxns: np.ones(cnxns.shape[0])

        def _soma_distance(other_cells):
            return\
                self.get_soma_distance_bins(
                    circuit_model, adapter,
                    cell, other_cells,
                    bin_size=bin_size_soma_distance)
        
        variables_groupby =\
            cell_properties_groupby + (
                ["soma_distance"] if by_soma_distance else [])

        connections =\
            adapter.get_afferent_connections(
                circuit_model,
                cell)

        columns_relevant =\
            cell_properties_groupby + (
                [variable, "soma_distance"]\
                if by_soma_distance else [variable])

        cells_afferent =\
            adapter.get_cells(circuit_model)\
                   .loc[connections.pre_gid.values]\
                   .assign(**{variable: value(connections)})
        if by_soma_distance:
            cells_afferent =\
                cells_afferent.assign(soma_distance=_soma_distance)
        value_measurement =\
            cells_afferent[columns_relevant].groupby(variables_groupby)\
                                            .agg("sum")
        return\
            value_measurement[variable]\
            if with_cell_propreties_as_index else\
               value_measurement.reindex()
                          
    def number_connections_afferent(self, by_soma_distance):
        """..."""
        return\
            PathwayMeasurement(
                value=lambda connection: np.ones(connection.shape[0]),
                variable="number_connections_afferent",
                by_soma_distance=by_soma_distance,
                direction="AFF",
                specifiers_cell_type=["mtype"],
                sampling_methodology=terminology.sampling_methodology.random
            ).sample_one

    def number_connections_pathway(self, by_soma_distance):
        return\
            PathwayMeasurement(
                value=lambda connection: np.ones(connection.shape[0]),
                variable="number_connections_afferent",
                by_soma_distance=by_soma_distance,
                direction="AFF",
                specifiers_cell_type=["mtype"],
                sampling_methodology=terminology.sampling_methodology.exhaustive,
                summaries="sum"
            ).summary

    def strength_connections_afferent(self, by_soma_distance):
        """..."""
        return\
            PathwayMeasurement(
                value=lambda cnxn: cnxn.strength.to_numpy(np.float64),
                by_soma_distance=by_soma_distance,
                direction="AFF",
                specifiers_cell_type=["mtype"],
                sampling_methodology=terminology.sampling_methodology.random,
                summaries="sum"
            ).sample_one

    def strength_pathways(self, by_soma_distance):
        """..."""
        return\
            PathwayMeasurement(
                value=lambda cnxn: cnxn.strength.to_numpy(np.float64),
                variable="pathway_strength",
                by_soma_distance=by_soma_distance,
                direction="AFF",
                specifiers_cell_type=["mtype"],
                sampling_methodology=terminology.sampling_methodology.exhaustive,
                summaries="sum"
            ).summary

        # variables_measurement =\
        #     dict(number=1., soma_distance=_soma_distance)\
        #     if by_soma_distance else\
        #        dict(number=1.)

        # return\
        #     cells_afferent.assign(**variables_measurement)[columns_relevant]\
        #                   .groupby(variables_groupby)\
        #                   .agg("sum")\
        #                   .number
        # return\
        #     adapter.get_cells(circuit_model)\
        #            .loc[adapter.get_afferent_gids(circuit_model, cell)]\
        #            .assign(**variables_measurement)\
        #            [variables_groupby +
        #             additional_variables_groupby +
        #             ["number_connections_afferent"]]\
        #            .groupby(variables_groupby + additional_variables_groupby)\
        #            .agg("sum")\
        #            .number_connections_afferent
    
    @lazyfield
    def analysis_number_connections_afferent(self):
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
            sample_measurement=self.number_connections_afferent(
                terminology.sampling_methodology.random,
                by_soma_distance=True).sample_one,
            measurement_collection=measurement.collection.series_type,
            plotter=MultiPlot(
                mvar=("post_synaptic_cell", "mtype"),
                plotter=LinePlot(
                    xvar="soma_distance",
                    xlabel="Soma Distance",
                    yvar="number_afferent_connections",
                    ylabel="Mean number of afferent connections",
                    gvar=("pre_synaptic_cell", "mtype"),
                    drawstyle="steps-mid")),
            report=CircuitAnalysisReport)


    @count_number_calls(LOGGER)
    def strength_connections_afferent(self,
            circuit_model,
            adapter,
            cell,
            cell_properties_groupby,
            by_soma_distance=True,
            bin_size_soma_distance=100.):
        """
        ...
        """
        def _soma_distance(other_cells):
            return\
                self.get_soma_distance_bins(
                    circuit_model, adapter,
                    cell, other_cells,
                    bin_size=bin_size_soma_distance)

        connections =\
            adapter.get_afferent_connections(
                circuit_model,
                cell)
        variables_measurement =\
            dict(strength=connections.strength.to_numpy(np.float64),
                 soma_distance=_soma_distance)\
            if by_soma_distance else\
               dict(strength=connections.strength.to_numpy(np.float64))
        columns_relevant =\
            variables_groupby + list(variables_measurement.keys())
        variables_groupby =\
            cell_properties_groupby + (
                ["soma_distance"] if by_soma_distance else [])
        cells_afferent =\
            adapter.get_cells(circuit_model)\
                   .loc[connections.pre_gid.values]
        return\
            cells_afferent.assign(**variables_measurement)[columns_relevant]\
                          .groupby(variables_groupby)\
                          .agg("sum")\
                          .strength



    @count_number_calls(LOGGER)
    def strength_afferent_connections(self,
            circuit_model,
            adapter,
            post_synaptic_cell_type,
            pre_synaptic_cell_type_specifier=None,
            by_soma_distance=True,
            bin_size=100,
            sampling_methodology=terminology.sampling_methodology.random):
        """
        Strength of afferent connections incident on the post-synaptic cells,
        originating from the pre-synaptic cells. Strength of connection is the
        number of synapses mediating that connection.

        Arugments
        --------------
        post_synaptic_cell_type :: An object describing the group of
        ~   post-synaptic cells to be investigated in these analyses.
        ~   Interpretation of the data in this object will be
        ~   delegated to the adapter used for the model analyzed.
        ~   Here are some guidelines when this object may is a dictionary.
        ~    Such a dictionary will have cell properties such as region, layer,
        ~    mtype,  and etype as keys. Each key may be given either a single
        ~    value or an iterable of values. Phenomena must be evaluated for
        ~    each of these values and collected as a pandas.DataFrame.
        """
        LOGGER.debug(
            """
            Strength afferent connections for post-synaptic cell type: {}
            """.format(post_synaptic_cell_type))
        if pre_synaptic_cell_type_specifier is None:
            pre_synaptic_cell_type_specifier =\
                list(post_synaptic_cell_type.keys())

        def _prefix_pre_synaptic(variable):
            return\
                self._at("pre_synaptic_cell_type", as_tuple=True)(variable)\
                if variable in pre_synaptic_cell_type_specifier\
                   else variable

        variables_groupby =[
            _prefix_pre_synaptic(variable)
            for variable in pre_synaptic_cell_type_specifier]
        if by_soma_distance:
            variables_groupby.append("soma_distance")

        post_synaptic_cell =\
            self.random_cell(
                circuit_model,
                adapter,
                post_synaptic_cell_type)

        def _soma_distance(pre_cells):
            return\
                self.get_soma_distance_bins(
                    circuit_model, adapter,
                    post_synaptic_cell, pre_cells,
                    bin_size=bin_size)

        connections =\
            adapter.get_afferent_connections(
                circuit_model,
                post_synaptic_cell)
        variables_measurement =\
            dict(strength=connections.strength.to_numpy(dtype=np.float64),
                 soma_distance=_soma_distance)\
            if by_soma_distance else\
               dict(number_connections_afferent=1.)
        return\
            adapter.get_cells(circuit_model)\
                   .loc[connections.pre_gid.values]\
                   .assign(**variables_measurement)\
                   .rename(columns=_prefix_pre_synaptic)\
                   [variables_groupby + ["strength"]]\
                   .groupby(variables_groupby)\
                   .agg("sum")\
                   .strength
                     
        # def _strength_connection(pre_synaptic_cells):
        #     return\
        #         adapter.get_strength_connections(
        #             pre_synaptic_cells,
        #             post_synaptic_cell)
        # gids_afferent =\
        #     adapter.get_afferent_gids(
        #         circuit_model,
        #         post_synaptic_cell)
        # variables_measurement =\
        #     dict(strength_afferent_connections=_strength_connection,
        #          soma_distance=_soma_distance)\
        #          if by_soma_distance else\
        #             dict(strength_afferent_connections=_strength_connection)
        # return\
        #     adapter.get_cells(circuit_model)\
        #            .loc[gids_afferent]\
        #            .assign(**variables_measurement)\
        #            .rename(columns=_prefix_pre_synaptic)\
        #            [variables_groupby + ["strength_afferent_connections"]]\
        #            .groupby(variables_groupby)\
        #            .agg("sum")\
        #            .strength_afferent_connections

    def synapse_count(self,
            adapter,
            circuit_model,
            pathway):
        """
        Get synapse count ...
        """
        raise NotImplementedError

    def analysis_synapse_count(self,
            pre_synaptic_cell_type_specifiers,
            post_synaptic_cell_type_specifiers):
        """
        Analysis of number of synapses in pathways specified by
        values of pre and post synaptic cell properties.

        Arguments
        ----------------
        pre_synaptic_cell_type_specifiers :: cell properties
        post_synaptic_cell_type_specifiers :: cell properties
        """
        return BrainCircuitAnalysis(
            introduction="""
            Not provided.
            """,
            methods="""
            Not provided.
            """,
            phenomenon=Phenomenon(
                "Sysapse count",
                """
                Number of synapses in a pathway.
                """),
            AdapterInterface=self.AdapterInterface,
            measurement_parameters=self.pathways(
                pre_synaptic_cell_type_specifiers,
                post_synaptic_cell_type_specifiers),
            sample_measurement=self.synapse_count,
            measurement_collection=measurement.collection.primitive_type,
            plotter=HeatMap())



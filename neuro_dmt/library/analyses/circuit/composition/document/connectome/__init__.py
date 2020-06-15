# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published
#  by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A  PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License 
# along with DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Document connectome of a circuit.
"""
import numpy as np
import pandas as pd
from matplotlib import  pyplot as plt
from dmt.model.interface import interfacemethod
from dmt.data.observation import measurement, SampleMeasurement, Summary
from pathlib import Path
from dmt.tk.journal import Logger
from dmt.tk.author import Author
from dmt.tk.parameters import Parameters
from dmt.tk.plotting import Bars, MultiPlot, LinePlot, HeatMap
from dmt.tk.utils import datasets
from dmt.analysis.document.measurement import CompositeData, Measurement
from dmt.analysis.document.builder import LabReportBuilder
from neuro_dmt import terminology
from neuro_dmt.utils.geometry import Cuboid
from neuro_dmt.library.data.sscx_mouse.composition.cell_density import\
    cell_density_defelipe
from neuro_dmt.library.data.sscx_mouse.composition.cell_ratio import\
    inhibitory_fraction_defelipe
from neuro_dmt.analysis.circuit.tools import PathwayMeasurement

X = terminology.bluebrain.cell.x
Y = terminology.bluebrain.cell.y
Z = terminology.bluebrain.cell.z
XYZ = [X, Y, Z]

LOGGER = Logger(client=__file__)

def get(sample_size=100, target={}, **kwargs):
    """
    Build a document that analyzes connectome of a circuit.

    Arguments
    ------------
    target :: Target cells to compute the connectome for.
    sample_size :: Population size to sample for a measurement.
    """

    document = LabReportBuilder("Circuit Connectome", author=Author.zero)

    @document.abstract
    def _():
        """
        This report analyzes a circuit's connectome, {\\it i.e.} the network
        like structure of neuron-to-neuron connectivity.
        """
        pass

    @document.introduction
    def _():
        """
        Connectome of a brain circuit is the complete description of its
        neuron-to-neuron connectivity. While at the local level a neuron's 
        connections determine its activity, at the circuit level the connectome 
        determines the circuit' computational capability.


        Here we analyze if a circuit's connectome follows the general principles
        of connectivity developed in
        \\href{https://www.frontiersin.org/articles/10.3389/fncom.2015.00120/full}{Reimann {\\it et. al.}},
        and has biologically realistic connectivity between neurons.


        A synapse between two neurons develops from an apposition between their
        axonal and dendritic arbors. The shapes of these trees are determined by
        the morphological types (mtypes) of the pre/post synaptic neurons. Thus
        we will analyze the connectivity of neurons of a specified pre-synaptic 
        mtype to neurons of a specified post-synaptic mtype. We will talk of
        these two pre and post synaptic populations as forming a mtype-to-mtype
        pathway.
        """
        pass

    @interfacemethod
    def get_mtypes(adapter, circuit_model):
        """
        Get a list of the  mtypes used in the circuit.
        """
        raise NotImplementedError

    def post_synaptic_cell_groups(adapter, circuit_model):
        return Parameters(
            pd.DataFrame(
                adapter.get_mtypes(circuit_model),
                columns=pd.MultiIndex.from_tuples([
                    ("post_synaptic_cell_group", "mtype")])
            )
        ).for_sampling(size=1)
    @document.methods.measurements
    def connection_probability(adapter, circuit_model, *args, **kwargs):
        """
        What is the probability that a cell from a pre-synaptic population is
        connected to a cell from a post-synaptic population?
        The pre and post synaptic populations are specified by their mtypes.
        """
        LOGGER.info(
            LOGGER.get_source_info(),
            """
            Compute connection probability.
            """)
        pathway_measurement = PathwayMeasurement(
            direction="AFF",
            value={"number": lambda c: 1.},
            specifiers_cell_type=["mtype"],
            sampling_methodology=terminology.sampling_methodology.exhaustive,
            processing_methodology=terminology.processing_methodology.batch,
            batch_size=10000,
            return_primary_info=True,
            target=lambda model, adapter: adapter.get_cells(circuit_model, **target)
        )
        def get_one(post_synaptic_cell_group):
            target = pathway_measurement.sample_target(
                circuit_model, adapter,
                post_synaptic_cell_group=post_synaptic_cell_group
            )
            connections = pathway_measurement.collector("sum")(
                circuit_model, adapter,
                post_synaptic_cell_group=post_synaptic_cell_group,
                target=target,
                prefixed=True
            )

            if connections is None:
                return None

            number_pairs = pathway_measurement.number_pairs(
                circuit_model, adapter,
                post_synaptic_cell_group=post_synaptic_cell_group,
                target=target,
                prefixed=True
            )
            return (connections.number / number_pairs).dropna()

        return measurement.collection.series_type(
            (p, get_one(**p))
            for p in post_synaptic_cell_groups(adapter, circuit_model)
        ).rename(
            columns={"value": "connection_probability"}
        )
    @document.methods.measurements
    def synapse_count(adapter, circuit_model, *args, **kwargs):
        """
        Number of synapses mediating connections.
        The pre and post synaptic populations are specified by their mtypes.
        """
        LOGGER.info(
            LOGGER.get_source_info(),
            """
            Compute synapse count.
            """)
        strength = lambda connections: connections.strength.to_numpy(np.float)
        pathway_measurement = PathwayMeasurement(
            direction="AFF",
            value=PathwayMeasurement.moments("strength", strength, n=1),
            variable="synapse_count",
            specifiers_cell_type=["mtype"],
            sampling_methodology=terminology.sampling_methodology.exhaustive,
            processing_methodology=terminology.processing_methodology.batch,
            batch_size=10000,
            return_primary_info=True,
            target=lambda model, adapter: adapter.get_cells(circuit_model, **target)
        )
        def get_one(post_synaptic_cell_group):
            target = pathway_measurement.sample_target(
                circuit_model, adapter,
                post_synaptic_cell_group=post_synaptic_cell_group
            )
            strengths = pathway_measurement.collector("sum")(
                circuit_model, adapter,
                post_synaptic_cell_group=post_synaptic_cell_group,
                target=target,
                prefixed=True
            )

            if strengths is None:
                return None

            return (strengths.strength_1 / strengths.strength_0).dropna()

        return measurement.collection.series_type(
            (p, get_one(**p))
            for p in post_synaptic_cell_groups(adapter, circuit_model)
        ).rename(
            columns={"value": "synapse_count"}
        )

    @document.methods.measurements
    def indegree(adapter, circuit_model, *args, **kwargs):
        """
        Number of afferent / in-coming connections at a neuron of a given mtype.
        """
        LOGGER.info(
            LOGGER.get_source_info(),
            """
            Compute in-degree.
            """)
        pathway_measurement = PathwayMeasurement(
            direction="AFF",
            value={"indegree": lambda c: 1.},
            sampling_methodology=terminology.sampling_methodology.exhaustive,
            processing_methodology=terminology.processing_methodology.batch,
            batch_size=10000,
            return_primary_info=True,
            target=lambda model, adapter: adapter.get_cells(circuit_model, **target)
        ).collector()

        def get_one(post_synaptic_cell_group):
            connections = pathway_measurement(
                circuit_model, adapter,
                post_synaptic_cell_group=post_synaptic_cell_group,
                prefixed=True
            )

            if connections is None:
                return None

            return connections.indegree

        return measurement.collection.series_type(
            (p, get_one(**p))
            for p in post_synaptic_cell_groups(adapter, circuit_model)
        ).rename(
            columns={"value": "indegree"}
        )

    @document.methods.measurements
    def outdegree(adapter, circuit_model, *args, **kwargs):
        """
        Number of efferent / out-going connections from a neuron of a given mtype.
        """
        LOGGER.info(
            LOGGER.get_source_info(),
            """
            Compute out-degree.
            """)
        pathway_measurement = PathwayMeasurement(
            direction="EFF",
            value={"outdegree": lambda c: 1.},
            sampling_methodology=terminology.sampling_methodology.exhaustive,
            processing_methodology=terminology.processing_methodology.batch,
            batch_size=10000,
            return_primary_info=True,
            target=lambda model, adapter: adapter.get_cells(circuit_model, **target)
        ).collector()

        def get_one(post_synaptic_cell_group):
            connections = pathway_measurement(
                circuit_model, adapter,
                post_synaptic_cell_group=post_synaptic_cell_group,
                prefixed=True
            )

            if connections is None:
                return None

            return connections.outdegree

        return measurement.collection.series_type(
            (p, get_one(**p))
            for p in post_synaptic_cell_groups(adapter, circuit_model)
        ).rename(
            columns={"value": "outdegree"}
        )

    @document.methods.measurements
    def number_afferent_connections(adapter, circuit_model, *args, **kwargs):
        """
        How many connections from neurons of a given pre-synaptic mtype
        to a neuron of a give post-synaptic mtype.
        """
        LOGGER.info(
            LOGGER.get_source_info(),
            """
            Compute number of afferent connections.
            """)
        pathway_measurement = PathwayMeasurement(
            direction="AFF",
            value={"number_afferent_connections": lambda c: 1.},
            specifiers_cell_type=["mtype"],
            sampling_methodology=terminology.sampling_methodology.exhaustive,
            processing_methodology=terminology.processing_methodology.batch,
            batch_size=10000,
            return_primary_info=True,
            target=lambda model, adapter: adapter.get_cells(circuit_model, **target)
        ).collector()
        def get_one(post_synaptic_cell_group):
            connections = pathway_measurement(
                circuit_model, adapter,
                post_synaptic_cell_group=post_synaptic_cell_group,
                prefixed=True
            )

            if connections is None:
                return pd.DataFrame()

            return connections

        return pd.concat([
            get_one(**p)
            for p in post_synaptic_cell_groups(adapter, circuit_model)
        ])

    # @document.methods.measurements
    # def number_efferent_connections(adapter, circuit_model, *args, **kwargs):
    #     """
    #     How many connections to neurons of a given post-synaptic mtype
    #     from a neuron of a give pre-synaptic mtype.
    #     """
    #     parameters = Parameters(
    #         pd.DataFrame(
    #             adapter.get_mtypes(circuit_model),
    #             columns=pd.MultiIndex.from_tuples([
    #                 ("pre_synaptic_cell_group", "mtype")])
    #         )
    #     )
    #     get = PathwayMeasurement(
    #         direction="EFF",
    #         value=lambda connections: 1,
    #         variable="number_efferent_connections",
    #         specifiers_cell_type=["mtype"],
    #         sampling_methodology=terminology.sampling_methodology.exhaustive,
    #         processing_methodology=terminology.processing_methodology.batch,
    #         batch_size=1000,
    #         return_primary_info=True,
    #         target=lambda model, adapter: adapter.get_cells(circuit_model, **target)
    #     ).collector("sum")
    #     return measurement.collection.series_type(
    #         (p, get(circuit_model, adapter, **p, **kwargs))
    #         for p in parameters.for_sampling(adapter, circuit_model, size=1)
    #     ).rename(
    #         columns={"value": "number_efferent_connections"}
    #     )

    @document.results.illustration
    def connection_probability():
        """
        Probability that a neuron from a pre-synaptic population is connected
        to a neuron from a post-synaptic population. The populations are specified
        by mtype.
        """
        LOGGER.info(
            LOGGER.get_source_info(),
            """
            Illustration connection probability.
            """)
        return HeatMap(
            vvar="connection_probability",
            xvar=("post_synaptic_cell_group", "mtype"),
            xlabel="post-synaptic mtype",
            yvar=("pre_synaptic_cell_group", "mtype"),
            ylabel="pre-synaptic mtype",
            font_size=8,
            font_scale=1.0,
            axes_titlesize=16,
            axes_labelsize="x-large",
            xtick_labelsize="xx-small",
            ytick_labelsize="xx-small",
            adjustments_plt=lambda : plt.gcf().subplots_adjust(bottom=0.15))

    @document.results.illustration
    def synapse_count():
        """
        Mean (expected) number of synapses mediating connections in
        a mtype-->mtype pathway.
        """
        return HeatMap(
            vvar="synapse_count",
            xvar=("post_synaptic_cell_group", "mtype"),
            xlabel="post-synaptic mtype",
            yvar=("pre_synaptic_cell_group", "mtype"),
            ylabel="pre-synaptic mtype",
            font_size=8,
            font_scale=1.0,
            axes_titlesize=16,
            axes_labelsize="x-large",
            xtick_labelsize="xx-small",
            ytick_labelsize="xx-small",
            adjustments_plt=lambda : plt.gcf().subplots_adjust(bottom=0.15))

    @document.results.illustration
    def indegree():
        """
        Total number of afferent connections arriving at a neuron.
        """
        return Bars(
            xvar=("post_synaptic_cell_group", "mtype"),
            xlabel="mtype",
            yvar="indegree",
            ylabel="in-degree",
            xtick_labelsize="x-small",
            ytick_labelsize="small")

    @document.results.illustration
    def outdegree():
        """
        Total number of efferent connections leaving from a neuron.
        """
        return Bars(
            xvar=("post_synaptic_cell_group", "mtype"),
            xlabel="mtype",
            yvar="outdegree",
            ylabel="out-degree",
            xtick_labelsize="x-small",
            ytick_labelsize="small")

    @document.results.illustration
    def number_afferent_connections():
        """
        Number of connections arriving at a neuron.
        """
        return MultiPlot(
            mvar=("post_synaptic_cell_group", "mtype"),
            plotter=Bars(
                xvar=("pre_synaptic_cell_group", "mtype"),
                xlabel="pre-synaptic mtype",
                yvar="number_afferent_connections",
                ylabel="Number Afferent Connections"))

    # @document.results.illustration
    # def number_efferent_connections():
    #     """
    #     Number of connections leaving a neuron.
    #     """
    #     return MultiPlot(
    #         mvar=("pre_synaptic_cell_group", "mtype"),
    #         plotter=Bars(
    #             xvar=("post_synaptic_cell_group", "mtype"),
    #             xlabel="post-synaptic mtype",
    #             yvar="number_efferent_connections",
    #             ylabel="number efferent connections"))

    return document.get()

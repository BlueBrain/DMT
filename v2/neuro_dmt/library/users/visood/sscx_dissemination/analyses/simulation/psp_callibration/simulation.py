"""
Data and code describing a PSP-simualtion.
"""
import os
import numpy as np
import pandas as pd
import h5py
import yaml
from dmt.tk.field import Field, LambdaField,  lazyfield, WithFields
from .trace import TraceCollection


class SimulationConfiguration(WithFields):
    """
    Configuration of a simulation to measure PSP traces for a pathway.
    """
    class Reference(WithFields):
        """..."""
        author = Field(
            """
            Author(s) of the reference data.
            """,
            __default_value__="NA")
        psp_amplitude = Field(
            """
            Statistical summary(mean and standard-deviation)
            as a `Mapping` or a `pandas.Series`.
            """,
            __as__=pd.Series)
        synapse_count = Field(
            """
            Statistical summary(mean and standard-deviation)
            as a `Mapping` or a `pandas.Series`.
            """,
            __as__=pd.Series)
        

    class Pathway(WithFields):
        """..."""
        class Constraints(WithFields):
            """
            Constraints to impose when simulating a pathway.
            """
            unique_gids = Field(
                """
                Boolean, true if unique gids should be used in sampling 
                cell pairs.
                """)
            max_dist_x = Field(
                """
                Maximum distance between pair cells along the x-axis.
                """,
                __default_value__=100.)
            max_dist_y = Field(
                """
                Maximum distance between pair cells along the y-axis.
                """,
                __default_value__=100.)
            max_dist_z = Field(
                """
                Maximum distance between pair cells along the z-axis.
                """,
                __default_value__=100.)

        pre = Field(
            """
            The pre-synaptic mtype in this `Pathway` instance.
            """)
        post = Field(
            """
            The post-synaptic mtype in this `Pathway` instance.
            """)
        constraints = Field(
            """
            Constraints associated with this `Pathway` instance.
            """,
            __as__=Constraints)

        label = LambdaField(
            """
            Label used for this `Pathway` instance.
            """,
            lambda self: "{}-{}".format(self.pre, self.post))


    class Protocol(WithFields):
        """..."""
        record_dt = Field(
            """
            Time step for recording the voltage.
            """)
        hold_V = Field(
            """
            Holding voltage.
            """)
        t_stim = Field(
            """
            Start time of stimulation.
            """)
        t_stop = Field(
            """
            Stop time of stimulation
            """)
        post_ttx = Field(
            """
            Boolean indicating if simulation should be run with a
            TTX treatment on the post-synaptic side.
            """)


class PathwaySimulation(WithFields):
    """
    Handle data associated with PSP simulation for a given pathway.
    """
    reference = Field(
        """
        Reference data against which this pathway will be calibrated.
        """,
        __as__=SimulationConfiguration.Reference)
    pathway = Field(
        """
        The mtype-->mtype pathway to run the simulation for.
        """,
        __as__=SimulationConfiguration.Pathway)
    protocol = Field(
        """
        Protocol for the PSP simulation.
        """,
        __as__=SimulationConfiguration.Protocol)
    path_output = Field(
        """
        String locating the output of this simulation.
        """)
    key_traces = Field(
        """
        Top level key in the output (HDF5) data that provides data for the
        recorded traces.
        """,
        __default_value__="traces")
    key_samples = Field(
        """
        Key in the output data that provides sample traces for each sampled
        connection in the simulated pathway.
        """,
        __default_value__="trials")
    key_average = Field(
        """
        Key in the output data that provides an average trace each sampled
        connection in the simulated pathway.
        """,
        __default_value__="average")
    index_time = Field(
        """
        Each trace will have a time and voltage / current. This field provides
        the index for the recorded time values.
        """,
        __default_value__=1)
    index_voltage = Field(
        """
        Each trace will have a time and voltage / current. This field provides
        the index for the recorded voltage values.
        """,
        __default_value__=0)
    h5_file_name = Field(
        """
        A call-back that provides the name of the HDF5 file containing data
        associated with the pathway simulated.
        """,
        __default_value__= "{}.traces.h5".format)
    parse_connection = Field(
        """
        A call-back to parse connection label into a pre and post synaptic cell.
        """,
        __default_value__=lambda c: tuple(c.split('-')))

    @lazyfield
    def raw_traces(self):
        """
        Raw output traces
        """
        return\
            h5py.File(
                os.path.join(
                    self.path_output,
                    self.h5_file_name(self.pathway.label))
            )[self.key_traces]

    @lazyfield
    def connections(self):
        """
        Pairs of cells simulated.
        """
        return list(self.raw_traces.keys())

    @lazyfield
    def traces(self):
        """..."""
        return\
            TraceCollection(
                self.raw_traces,
                key_samples=self.key_samples,
                index_time=self.index_time,
                index_voltage=self.index_voltage,
                parse_connection=lambda c: tuple(c.split('-')))


class ModelSimulationPSP(WithFields):
    """
    PSP Simulation output wrapped as a model.
    """
    path_simulation_data = Field(
        """
        Path where data associated with PSP simulations are located.
        It is assumed that traces obtained in these simulations are
        stored in HFD5 format, one such file for each pathway simulated.
        """)
    name_folder_traces = Field(
        """
        Name of the folder that contains traces as HDF5, assumed to be located
        under the simulation data directory
        """,
        __default_value__="output")
    name_folder_pathway_configurations = Field(
        """
        Name of the folder that contains configurations for simulated pathways.
        """,
        __default_value__="pathways")
    name_config_file_pathway = Field(
        """
        A callback to construct the name of the file containing configuration
        for simulation of a given pathway.
        """,
        __default_value__="{}.yaml".format)
    pathway_types = Field(
        """
        Names types of pathways.
        """,
        __default_value__=["primary", "secondary", "projection"])
    type_pathway = Field(
        """
        Mapping pathway-->type_pathway
        """,
        __default_value__={})

    @lazyfield
    def path_simulation_traces(self):
        return\
            os.path.join(
                self.path_simulation_data,
                self.name_folder_traces)

    def read_pathway_types(self):
        path_configs =\
            os.path.join(
                self.path_simulation_data,
                self.name_folder_pathway_configurations)
        def _pathways(type_pathway):
            for name_file in os.listdir(
                    os.path.join(path_configs, type_pathway)):
                split_name =\
                    name_file.split('.')
                if split_name[-1] == "yaml":
                    result = '.'.join(split_name[:-1])
                    yield result

        return {
            pathway: type_pathway
            for type_pathway in self.pathway_types
            for pathway in _pathways(type_pathway)}

    def path_simulation_config(self,
            pathway):
        """
        Path to the configuration used to simulated `pathway`.

        Arguments
        --------------
        type_pathway :: Either primary, secondary, or projection...
        """
        # try:
        #     pre = pathway[0]
        #     post = pathway[1]
        # except IndexError:
        #     pre = pathway.pre
        #     post = pathway.post
        if not self.type_pathway:
            self.type_pathway = self.read_pathway_types()
        path_configs =\
            os.path.join(
                self.path_simulation_data,
                self.name_folder_pathway_configurations)
        try:
            return\
                os.path.join(
                    path_configs,
                    self.type_pathway[pathway],
                    self.name_config_file_pathway(pathway))
        except KeyError:
            raise ValueError(
                """
                Unknown pathway {}.
                """.format(pathway))
        
    def __load_simulation_data(self, pathway):
        """..."""
        with open(
                self.path_simulation_config(pathway), 'r'
        ) as file_config:
            try:
                config = yaml.load(file_config, Loader=yaml.FullLoader)
            except:
                config = yaml.load(file_config)

        return PathwaySimulation(config, path_output=self.path_simulation_traces)
            
    __simulation_data = {} #to store simulation data for individual pathways.
    def simulation_data(self, pathway):
        """..."""
        if pathway not in self.__simulation_data:
            self.__simulation_data[pathway] =\
                self.__load_simulation_data(pathway)
        return self.__simulation_data[pathway]

    @lazyfield
    def pathways(self):
        """
        Pathways that were actually simulated and hence are a part of the
        "model".
        """
        return[
            name_file.split('.')[0]
            for name_file in os.listdir(self.path_simulation_traces)
            if "traces" in name_file and name_file.split('.')[-1] == "h5"]

    def connections(self, pathway, parsed=False):
        """..."""
        data_sim =\
            self.simulation_data(pathway)
        connections =\
            data_sim.connections
        return\
            [data_sim.parse_connection(cnxn) for cnxn in connections]\
            if parsed else connections


class Adapter:
    """
    Adapter of the model for simulation analysis.
    """
    @staticmethod
    def get_pathways(model):
        """..."""
        return model.pathways

    @staticmethod
    def get_connections(model, pathway):
        return model.connections(pathway)

    @staticmethod
    def get_trace(model, pathway, connection):
        """..."""
        return\
            model.simulation_data(pathway)\
                 .traces\
                 .loc[connection]

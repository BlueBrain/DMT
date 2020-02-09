"""
Data and code describing a PSP-simualtion.
"""
import os
import numpy as np
import pandas as pd
import h5py
from dmt.tk.field import Field, LambdaField,  lazyfield, WithFields
from .trace import TraceCollection

class SimulationPSP(WithFields):
    """
    Specify a simulation for PSP analysis.
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
            The post-synapticn mtype in this `Pathway` instance.
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
         
    reference = Field(
        """
        Reference data against which this pathway will be callibrated.
        """,
        __as__=Reference)
    pathway = Field(
        """
        The mtype-->mtype pathway to run the simulation for.
        """,
        __as__=Pathway)
    protocol = Field(
        """
        Protocol for the PSP simulation.
        """,
        __as__=Protocol)
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
        return list(
            self.parse_connection(c)
            for c in self.raw_traces.keys())

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

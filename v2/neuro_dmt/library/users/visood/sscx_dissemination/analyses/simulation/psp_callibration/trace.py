"""
Code to work with PSP traces recorded in a cell.
"""

import h5py
import numpy as np
import pandas as pd
from tqdm import tqdm
from collections import namedtuple
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields



class TimeWindow(WithFields):
    """Simple data class"""
    begin = Field(
        """
        Time at which the window begins.
        """)
    end = Field(
        """
        Time at which the window ends.
        """)

    def __init__(*args, **kwargs):
        """..."""
        if len(args) >= 2:
            kwargs.update({
                "begin": args[0],
                "end": args[1]})
            pass
        super().__init__(*args[2:], **kwargs)
        

def Trace(time, voltage):
    """..."""
    return pd.Series(voltage, index=pd.Index(time, name="time"))


class TraceCollection(pd.DataFrame):
    """
    Adapt `pandas.DataFrame` to hold a collection of traces produced by
    a simulation run.
    """
    def __init__(self,
            data_raw,
            key_samples,
            index_time,
            index_voltage,
            parse_connection):
        """
        Arguments
        -----------
        data_traces :: Data obtained from a 
        """
        def _extract(connection):
            traces =\
                data_raw[connection][key_samples]
            number_trials, number_quantities, number_records =\
                traces.shape
            #pre_synpatic_cell, post_synaptic_cell =\
            #    parse_connection(connection)
            assert number_quantities > index_time
            assert number_quantities > index_voltage
            return\
                pd.concat([
                    pd.DataFrame({
                        "trial": trial,
            #            "pre_synaptic_cell": pre_synpatic_cell,
            #            "post_synaptic_cell": post_synaptic_cell,
                        "connection": connection,
                        "record_step": range(number_records),
                        "time": np.array(
                            traces[trial, index_time, :]),
                        "voltage": np.array(
                            traces[trial, index_voltage, :])})
                    for trial in range(number_trials)])
            
        super().__init__(
            pd.concat([
                _extract(connection)
                for connection in tqdm(data_raw.keys())])\
            .set_index([
                "connection",
                "trial",
                "record_step"]))

    @classmethod
    def load(cls,
             path_hdf5,
             key_traces,
             key_samples,
             index_time,
             index_voltage,
             parse_connection):
        """
        Load a HDF5 file.
        """
        return cls(
            h5py.File(path_hdf5)[key_traces],
            key_trials=key_samples,
            index_time=index_time,
            index_voltage=index_voltage,
            parse_connection=parse_connection)
                

class RiseCurve(WithFields):
    """
    Mean rise curve for a bunch of traces.
    """
    Duration =\
        namedtuple("Duration", ["begin", "end"])
   
    traces = Field(
        """
        A `pandas.DataFrame` holding the traces.
        """,
        __as__=TraceCollection)

    time_window = Field(
        """
        A two-tuple specifying (begin, end) of the time window during which
        this `RiseCurve` instance is defined.
        """,
        __as__=Duration)

    @lazyfield
    def curve(self):
        """..."""
        return self.traces.mean[np.logical_and(
            self.time_window.begin <= self.traces.time,
            self.traces.time < self.time_window.end)]

    @lazyfield
    def amplitude(self):
        """Amplitude of rise."""
        raise NotImplementedError

    @lazyfield
    def tau(self):
        """Time constant of rise."""
        raise NotImplementedError

    @lazyfield
    def latency(self):
        """Latency of rise."""
        raise NotImplementedError

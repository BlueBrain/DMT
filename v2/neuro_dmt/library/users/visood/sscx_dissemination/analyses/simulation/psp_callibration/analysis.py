"""
Analyze PSP amplitudes, obtained from a library.
"""

import pandas as pd
from dmt.model.interface import Interface, interfacemethod
from dmt.data.observation import measurement
from neuro_dmt import terminology
from dmt.tk.parameters import Parameters
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.field import Field, lazyfield, LambdaField, ABCWithFields
from dmt.tk.plotting.crosses import Crosses
from dmt.tk.reporting.section import Section
from neuro_dmt.analysis.circuit import StructuredAnalysis

class PspTraceAnalysis(StructuredAnalysis):
    """
    Specialize StructuredAnalysis for an analysis of PSP traces.
    """
    
    @interfacemethod
    def get_pathways(adapter, model):
        """
        Implement this method on the adapter.
        The call `adapter.get_pathways(model)` should return the
        mtype-->mtype pathways for which traces can be obtained.
        """
        raise NotImplementedError

    @interfacemethod
    def get_connections(adapter, model, pathway):
        """
        Implement this method on the adapter.
        The call `adapter.get_connections(model, pathway)` should return the
        available connections for the given pathway.
        """
        raise NotImplementedError

    def measurement_parameters(self, adapter, model):
        """
        Parameters for which model will be asked to record traces.
        """
        return\
            pd.concat([
                pd.DataFrame({
                    "pathway": pathway,
                    "connection": adapter.get_connections(model, pathway)})
                for pathway in adapter.get_pathways(model)])

    @interfacemethod
    def get_trace(adapter, model, pathway, connection):
        """
        Implement this method on the adapter.
        The call `adapter.get_traces(model, pathway, connection)` should return
        a `pandas.DataFrame` with two columns: <time, voltage>, and
        'record_step' name of the index.
        """
        raise NotImplementedError

    def sample_measurement(self, adapter, model, pathway, connection):
        """..."""
        return adapter.get_trace(model, pathway, connection)

    def measurement_collection(self, traces):
        """
        Each model measurement returns a single trace (for given pathway and
        connection). These individual measurements must be collected into a
        dataframe.
        """
        return\
            pd.concat([
                pd.DataFrame({
                    "record_step": trace.shape[1],
                    "time": trace[0,:],
                    "voltage": trace[1,:]
                }).assign(**params).set_index(params.keys())
                for params, trace in traces])

    def _amplitude(self, trace):
        """
        PSP amplitude measurements for a given pathway, and connection.
        """
        return trace.voltage.max()

    def has_spiked(self, trace=None, amplitude=None):
        """
        Did the trace spike?
        """
        if trace is None and amplitude is None:
            raise TypeError(
                """
                has_spiked(...) called without any arguments.
                Provide either a trace or an amplitude...
                """)
        if amplitude is None:
            amplitude = self._amplitude(trace)
        return amplitude > - 0.61

    def amplitude(self, adapter, model, pathway, connection):
        """..."""
        return\
            self._amplitude(
                adapter.get_trace(
                    model, pathway, connection))

    def spike(self, adapter, model, pathway, connection):
        """..."""
        return\
            self.has_spiked(
                adapter.get_trace(
                    model, pathway, connection))

    def probability_spiking(self, measurement_traces):
        """
        ....
        """
        return\
            measurement_traces.groupby("pathway", "connection", "trial")\
                              .agg(self.has_spiked)\
                              .groupby(["pathway", "connection"])\
                              .agg(["size", "mean", "std"])

    def statistics_amplitudes(self, measurement_traces):
        """
        ....
        """
        return\
            measurement_traces.groupby("pathway", "connection", "trial")\
                              .filter(lambda trace: not self._has_spiked(trace))\
                              .agg(self._amplitude)\
                              .groupby(["pathway", "connection"])\
                              .agg(["size", "mean", "std"])

    def results(self, adapter, model, measurement_traces):
        """..."""
        return\
            """
            Statistics for Amplitudes
            -------------------------------------------------------------------
            {}
            -------------------------------------------------------------------

            Statistics for Spikes
            -------------------------------------------------------------------
            -------------------------------------------------------------------
            {}
            """.format(
                self.statistics_amplitudes(measurement_traces),
                self.probability_spiking(measurement_traces))


class PspAmplitudeAnalysis(StructuredAnalysis):
    """
    Analyze, and validate amplitudes measured in PSP simulations...
    """
    phenomenon = Phenomenon(
        "PSP Amplitude",
        description="Amplitude of post-synaptic potentials",
        group="Simulation")
    introduction = Section.introduction(
        """
        We analyze PSP amplitudes obtained for circuit {label}.
        """)
    methods = Section.methods(
        """
        Amplitudes for traces for pathway connections were analyzed.
        """)
    reference_data = Field(
        """
        Experimental data to validate model predictions.
        Reference data should be provided as a Mapping with only a single
        item --- its key will be used to label the reference data in plots
        and reports.
        """)

    @interfacemethod
    def get_pathways(adapter, model):
        """
        Implement this method on the adapter.
        The call `adapter.get_pathways(model)` should return the
        mtype-->mtype pathways for which traces can be obtained.
        """
        raise NotImplementedError

    @interfacemethod
    def get_amplitudes(adapter, model, pathway):
        """
        Implement this method on the adapter.
        The call `adapter.get_amplitudes(model, pathway)` should return the
        amplitudes obtained for connections in a pathway.
        """
        raise NotImplementedError

    sampling_methodology =\
        terminology.sampling_methodology.exhaustive
    @lazyfield
    def measurement_parameters(self):
        """..."""
        def _pathways(adapter, circuit_model):
            return\
                pd.DataFrame({
                    "pathway": adapter.get_pathways(circuit_model)})
        return\
            Parameters(
                _pathways,
                labels=("pathway"))

    def sample_measurement(self, model, adapter, pathway, **kwargs):
        """..."""
        return\
            adapter.get_amplitudes(model, pathway)

    @lazyfield
    def measurement_collection(self):
        """..."""
        return lambda\
            measurement_generator: measurement.collection\
                                              .summary_series_type(
                                                  measurement_generator,
                                                  "pathway")
        return measurement.collection.series_type

    def statistics_spiking(self, amplitudes):
        return\
            amplitudes.groupby("pathway")\
                      .agg(["size", "mean", "std"])

    def _with_reference_data(self,
            measurement_model,
            reference_data):
        """
        ...
        """
        model_datasets =\
            measurement_model.reset_index().dataset.unique()

        if len(model_datasets) != 1:
            raise ValueError(
                """
                Only a single model data can be handled.
                Datasets passed: {}
                """.format(list(model_datasets)))
        
        return\
            measurement.concat_as_summaries({
                "model": measurement_model.xs(model_datasets[0], level="dataset"),
                "reference": reference_data})

    @lazyfield
    def figures(self):
        """Plot the measurement."""
        return Crosses(
            xvar="model",
            yvar="reference",
            gvar="pathway",
            title="PSP Amplitude Validation.")


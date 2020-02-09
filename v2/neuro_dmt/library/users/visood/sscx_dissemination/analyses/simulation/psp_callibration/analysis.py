"""
Analyze PSP amplitudes, obtained from a library.
"""

from dmt.tk.parameters import Parameters
from dmt.model.interface import Interface, interfacemethod
from dmt.tk.field import Field, lazyfield, LambdaField, ABCWithFields
from neuro_dmt.analysis.circuit import StructuredAnalysis

class PostSynapticPotentialAnalysis(ABCWithFields):
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

    def trace(self, adapter, model, pathway, connection):
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

    def has_spiked(self, trace):
        """
        Did the trace spike?
        """
        return trace.voltage.max() > - 0.61

    def _amplitude(self, trace):
        """
        PSP amplitude measurements for a given pathway, and connection.
        """
        return trace.voltage.max()

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

    def statistics_spikes(self, measurement_traces):
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
                              agg(["size", "mean", "std"])


    @lazyfield
    def analysis_amplitudes(self):
        """..."""
        return StructuredAnalysis(
            introduction="""
            Analysis of PSP amplitudes.
            """,
            methods="""
            """)








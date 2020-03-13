"""
Analyses of the circuit's connectome.
"""

from  neuro_dmt.library.users.visood.sscx_dissemination.analyses import *
from .suite import AdapterInterface

def number_connections_afferent(circuit_model, adapter, target):
    """
    Arguments
    --------------
    target :: Mapping describing the subset of cells between which
    ~         the connections will be analyzed.
    """
    phenomenon =\
        Phenomenon(
            "Number Afferent Connections",
            description="Number of afferent connections",
            group="Connectome")
    pathway_measurement =\
            PathwayMeasurement(
                direction="AFF",
                value=lambda connections: 1,
                variable=phenomenon.label,
                specifiers_cell_type=["mtype"],
                sampling_methodology=terminology.sampling_methodology.exhaustive,
                processing_methodology=terminology.processing_methodology.batch,
                batch_size=1000,
                return_primary_info=True,
                target=lambda adapter, model: adapter.get_cells(model, **target))
    introduction =\
        """
        Number of afferent connections of a cell.
        """
    methods =\
        """
        Number of afferent connections were counted by mtype.
        """
    def mtypes(adapter, circuit_model):
        return pd.DataFrame(
            adapter.get_mtypes(circuit_model),
            columns=pd.MultiIndex.from_tuples([
                ("post_synaptic_cell_group", "mtype")]))
    analysis = \
        BrainCircuitAnalysis(
            phenomenon=phenomenon,
            introduction=introduction,
            methods=methods,
            AdapterInterface=AdapterInterface,
            measurement_parameters=Parameters(mtypes, labels=["mtype"]),
            sample_measurement=pathway_measurement.collector(),
            measurement_collection=measurement.collection.series_type,
            processing_methodology=terminology.processing_methodology.serial,
            sampling_methodology=terminology.sampling_methodology.exhaustive,
            plotter=MultiPlot(
                mvar=("post_synaptic_cell", "mtype"),
                plotter=Bars(
                    xvar=("pre_synaptic_cell", "mtype"),
                    xlabel="pre-synaptic-cell-mtype",
                    yvar=phenomenon.label,
                    ylabel=phenomenon.name)))
    return analysis(circuit_model, adapter)

def strength_connections_afferent(circuit_model, adapter, target):
    """
    Arguments
    --------------
    target :: Mapping describing the subset of cells between which
    ~         the connections will be analyzed.
    """
    phenomenon =\
        Phenomenon(
            "Strength Afferent Connections",
            description="Number of synapses mediating afferent connections",
            group="Connectome")
    pathway_measurement =\
            PathwayMeasurement(
                direction="AFF",
                value=lambda connections: connections.strength.to_numpy(np.float),
                variable=phenomenon.label,
                specifiers_cell_type=["mtype"],
                processing_methodology=terminology.processing_methodology.batch,
                sampling_methodology=terminology.sampling_methodology.exhaustive,
                batch_size=1000,
                return_primary_info=True,
                target=lambda adapter, model: adapter.get_cells(model, **target))
    introduction =\
        """
        Strength of afferent connections of a cell.
        """
    methods =\
        """
        Strength of afferent connections were counted by mtype.
        """
    def mtypes(adapter, circuit_model):
        return pd.DataFrame(
            adapter.get_mtypes(circuit_model),
            columns=pd.MultiIndex.from_tuples([
                ("post_synaptic_cell_group", "mtype")]))
    analysis = \
        BrainCircuitAnalysis(
            phenomenon=phenomenon,
            introduction=introduction,
            methods=methods,
            AdapterInterface=AdapterInterface,
            measurement_parameters=Parameters(mtypes, labels=["mtype"]),
            sample_measurement=pathway_measurement.collector(),
            measurement_collection=measurement.collection.series_type,
            processing_methodology=terminology.processing_methodology.serial,
            sampling_methodology=terminology.sampling_methodology.exhaustive,
            plotter=MultiPlot(
                mvar=("post_synaptic_cell", "mtype"),
                plotter=Bars(
                    xvar=("pre_synaptic_cell", "mtype"),
                    xlabel="pre-synaptic-cell-mtype",
                    yvar=phenomenon.label,
                    ylabel=phenomenon.name)))
    return analysis(circuit_model, adapter)

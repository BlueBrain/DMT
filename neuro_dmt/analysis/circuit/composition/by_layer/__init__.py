"""Analysis of a circuit's composition, by layer."""

from dmt.analysis\
    import OfSinglePhenomenon
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.utils.descriptor\
    import  Field, document_fields
from dmt.vtk.measurement.parameter.group\
    import ParameterGroup
from dmt.vtk.plotting\
    import Plot\
    ,      BarPlot
from neuro_dmt.analysis.circuit.composition\
    import SpatialCompositionAnalysis
from neuro_dmt.analysis.report.single_phenomenon\
    import AnalysisReport


@document_fields
class ByLayerCompositionAnalysis(
        OfSinglePhenomenon,
        SpatialCompositionAnalysis):
    """..."""
    Plotter=\
        Field(
            __name__ = "Plotter",
            __typecheck__ = Field.typecheck.subtype(Plot),
            __default__ = BarPlot,
            __doc__ = """A subclass of {} to comparison results.""".format(
                Plot))

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon,
            ReportType=AnalysisReport,
            *args, **kwargs)

    @property
    def spatial_parameter_group(self):
        """
        Unsed method. This method does not appear anywhere else,
        consider removing it.
        """
        return\
            ParameterGroup(
                tuple(self.spatial_parameters))


from neuro_dmt.analysis.circuit.composition.by_layer.cell_density\
    import CellDensityAnalysis
from neuro_dmt.analysis.circuit.composition.by_layer.cell_ratio\
    import CellRatioAnalysis
from neuro_dmt.analysis.circuit.composition.by_layer.inhibitory_synapse_density\
    import InhibitorySynapseDensityAnalysis
from neuro_dmt.analysis.circuit.composition.by_layer.synapse_density\
    import SynapseDensityAnalysis
from neuro_dmt.analysis.circuit.composition.by_layer.soma_volume_fraction\
    import SomaVolumeFractionAnalysis
from neuro_dmt.analysis.circuit.composition.by_layer.mtype_cell_density\
    import MtypeCellDensityAnalysis

"""Analyze a circuit by (cortical) depth.
These analyses will mostly be made for cortical circuits,
but they should work for any atlas-based circuit that provides a
'depth' dataset."""
from abc\
    import abstractmethod
from dmt.analysis\
    import OfSinglePhenomenon
from dmt.vtk.utils.descriptor\
    import Field, document_fields
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.measurement.parameter.group\
    import ParameterGroup
from neuro_dmt.analysis.circuit.composition\
    import SpatialCompositionAnalysis
from neuro_dmt.analysis.circuit.composition.by_depth.report\
    import AnalysisReport


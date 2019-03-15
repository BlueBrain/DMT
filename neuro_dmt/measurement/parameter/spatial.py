"""Parameters to measure phenomena as a function of space."""

from dmt.vtk.utils.descriptor\
    import Field
from neuro_dmt.measurement.parameter\
    import BrainCircuitSpatialParameter
from neuro_dmt.utils\
    import brain_regions
    
class CorticalDepth(
        BrainCircuitSpatialParameter):
    """Depth down a cortical column,
    as a fraction so that different cortical regions can be compared.
    """
    label = "depth"
        
    def __init__(self,
            number_points=20,
            *args, **kwargs):
        """..."""
        super().__init__(
            brain_region=brain_regions.isocortex,
            value_type=float,
            values=list(np.linspace(0., 1., number_points)),
            *args, **kwargs)


class SomaDistance(
        BrainCircuitSpatialParameter):
    """Distance between soma of two cells, in bins.
    """
    label = "soma_distance"

    value_type = Field(
        __name__="value_type",
        __type__=tuple,
        __typecheck__=Field.typecheck.__tuple__(float, float),
        __doc__="""Bins containing floats can be defined as an interval.""")

    def __init__(self,
            lower_bound = 0.,
            upper_bound = 500., #in micro-meters
            number_bins = 20,
            *args, **kwargs):
        """..."""
        bin_width=\
            (upper_bound - lower_bound)/number_bins
        super().__init__(
            brain_region=brain_regions.whole_brain,
            value_type=(float, float),
            values=[
                (lower_bound + i * bin_width,
                 lower_bound + (i + 1) * bin_width)
                for i in range(number_bins)],
            *args, **kwargs)

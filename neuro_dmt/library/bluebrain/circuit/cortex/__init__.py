"""..."""
from neuro_dmt.measurement.parameter import CorticalLayer, HippocampalLayer

class MeasureByCorticalLayer:
    """Mixin for validations of phenomena that are measured
    by cortical layer."""

    def __init__(self, *args, **kwargs):
        """..."""
        self.spatial_parameters = {CorticalLayer()}
        super().__init__(self, *args, **kwargs)

    @property
    def plotting_parameter(self):
        """This is a hack."""
        return CorticalLayer()

class MeasureByHippocampalLayer:
    """Mixin for validations of phenomena that are measured
    by hippocampal layer."""

    def __init__(self, *args, **kwargs):
        """..."""
        self.spatial_parameters = {HippocampalLayer()}
        super().__init__(self, *args, **kwargs)

    @property
    def plotting_parameter(self):
        """This is a hack."""
        return HippocampalLayer()

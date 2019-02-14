"""..."""
from dmt.vtk.utils.descriptor\
    import Field\
    ,      WithFCA
from neuro_dmt.measurement.parameter\
    import LayerIndex\
    ,      CorticalLayer\
    ,      HippocampalLayer
from neuro_dmt.models.bluebrain.circuit.parameters\
    import Mtype


class MeasureByCorticalLayer:
    """Mixin for validations of phenomena that are measured
    by cortical layer."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.spatial_parameters=\
            {CorticalLayer()}
        super().__init__(self,
                *args, **kwargs)

    @property
    def plotting_parameter(self):
        """This is a hack."""
        return CorticalLayer()

class MeasureByHippocampalLayer:
    """Mixin for validations of phenomena that are measured
    by hippocampa layer."""

    def __init__(self
            *args, **kwargs):
        """..."""
        self.spatial_parameters=\
            {HippocampalLayer()}
        super().__init__(self,
                *args, **kwargs)

    @property
    def plotting_parameter(self):
        """This is a hack."""
        return HippocampalLayer()


class MeasureByMtype:
    """Mixin for analyses of"""
    def __init__(self,
            *args, **kwargs):
        self.pathway_parameters=\
            [Mtype(label="pre_mtype"), Mtype(label="post_mtype")]
        self.cell_group_parameters=\
            Mtype()

        

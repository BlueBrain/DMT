"""..."""
from dmt.vtk.utils.descriptor\
    import Field\
    ,      WithFCA
from neuro_dmt.measurement.parameter\
    import LayerIndex\
    ,      CorticalLayer\
    ,      CorticalDepth\
    ,      HippocampalLayer
from neuro_dmt.models.bluebrain.circuit.parameters\
    import Mtype


class MeasureByCorticalLayer:
    """Mixin for validations of phenomena that are measured
    by cortical layer."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.spatial_parameters=[
            CorticalLayer()]
        self.measurement_parameters=[
            CorticalLayer()]
        self.plotted_parameters=[
            CorticalLayer().label]
        super().__init__(self,
                *args, **kwargs)

    @property
    def get_plotting_parameter(self):
        """This is a hack."""
        return CorticalLayer()


class MeasureByCorticalDepth:
    """Mixin for validations of phenomena that are measured
    by cortical depth."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        cortical_depth_parameter=\
            CorticalDepth(
                *args, **kwargs)
        self.spatial_parameters=[
            cortical_depth_parameter]
        self.measurement_parameters=[
            cortical_depth_parameter]
        self.plotted_parameters=[
            cortical_depth_parameter.label]
        super().__init__(self,
            *args, **kwargs)


class MeasureByHippocampalLayer:
    """Mixin for validations of phenomena that are measured
    by hippocampa layer."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        self.spatial_parameters=[
            HippocampalLayer()]
        self.measurement_parameters=[
            HippocampalLayer()]
        self.plotted_parameters=[
            HippocampalLayer().label]
        super().__init__(self,
                *args, **kwargs)

    @property
    def get_plotting_parameter(self):
        """This is a hack."""
        return HippocampalLayer()


class MeasureByMtype:
    """Mixin for analyses of"""
    def __init__(self,
            *args, **kwargs):
        self.pathway_parameters=[
            Mtype(label="pre_mtype"),
            Mtype(label="post_mtype")]
        self.cell_group_parameters=\
            Mtype()
        self.measurement_parameters=[
            Mtype(label="pre_mtype"),
            Mtype(label="post_mtype")]
        self.plotted_parameters=[
            Mtype(label="pre_mtype"),
            Mtype(label="post_mtype")]

        

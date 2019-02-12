"""SSCx circuit models."""
import numpy as np
from bluepy.v2.enums\
    import Cell
from dmt.vtk.utils\
    import collections
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.measurement.condition\
    import Condition
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import O1LayeredCircuitSpecialization\
    ,      O1CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import O1CircuitModel\
    ,      FakeAtlasBasedCircuitModel\
    ,      AtlasBasedCircuitModel
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import AtlasBasedLayeredCircuitSpecialization
from neuro_dmt.models.bluebrain.circuit.atlas.fake.build\
    import FakeAtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import AtlasCircuitGeometry


class SSCxO1Specialization(
        O1LayeredCircuitSpecialization):
    """..."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.brain_region = brain_regions.sscx
        super().__init__(
            *args, **kwargs)

    def get_spanning_column_parameter(self,
            column_values=range(7)):
        """A parameter whose values are meso-columns of the
        O1 circuit. While in most O1 circuits the values would be those
        of the default value above, at least on one Hippocampus CA1 circuit
        it's values do not contain the trailing '_Column'..."""
        return\
            Column(
                value_type=str,
                values=["mc{}_Column".format(n)
                        for n in column_values])


rat_sscx_o1_specialization=\
    SSCxO1Specialization(
        central_meso_column="mc2_Column",
        lattice_vector=Record(
            a1=np.array([0.0, 0.0, 230.92]),
            a2=np.array([199.98, 0.0, -115.46])),
        layer_thickness=np.array([
            164.94915873,
            148.87602025,
            352.92508322,
            189.57183895,
            525.05585701,
            700.37845971]),
        layer_bottom=10.)
mouse_sscx_o1_specialization=\
    SSCxO1Specialization(
        central_meso_colum="mc2_Column",
        lattice_vector=Record(
            a1=np.array([152.92, 0.0, 0.0]),
            a2=np.array([-76.46, 0.0, 132.43])),
        layer_thickness=np.array([
            122.71,
            96.49,
            175.84,
            185.25,
            362.26,
            436.22]),
        layer_bottom=0.0)


class RatO1CircuitGeometry(
        O1CircuitGeometry):
    """..."""
    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        self.circuit_specialization=\
            rat_sscx_o1_specialization
        super().__init__(
            circuit,
            *args, **kwargs)


class MouseO1CircuitGeometry(
        O1CircuitGeometry):
    """..."""
    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        self.circuit_specialization=\
            mouse_sscx_o1_specialization
        super().__init__(
            circuit,
            *args, **kwargs)


def get_rat_sscx_O1_circuit_model(
        circuit_config,
        *args, **kwargs):
    """..."""
    return\
        O1CircuitModel(
            animal="rat",
            brain_region=brain_regions.sscx,
            geometry_type=RatO1CircuitGeometry,
            circuit_config=circuit_config)

def get_mouse_sscx_O1_circuit_model(
        circuit_config,
        *args, **kwargs):
    """"..."""
    return\
        O1CircuitModel(
            animal="mouse",
            brain_region=brain_regions.sscx,
            geometry_type=MouseO1CircuitGeometry,
            circuit_config=circuit_config)



class SSCxAtlasSpecialization(
        AtlasBasedLayeredCircuitSpecialization):
    """Specialization for atlas based circuit of the rat from December 2018

    Applicable Circuits
    ----------------------------------------------------------------------------
    1. /gpfs/bbp.cscs.ch/project/proj64/circuits/S1.v6a/20171206/

    Development Notes
    ----------------------------------------------------------------------------
    A 'CircuitSpecialization' provides code peculiar to specific circuit builds.
    Provide the circuits that this specialization applies to.
    For now we do this in the doc-string. We can provide an attribute that
    is a list containing locations of circuit configurations."""

    def __init__(self,
            *args, **kwargs):
        """Initialize me"""
        self.representative_region=\
            "S1HL"
        self.atlas_acronym_separator=\
            ""
        if "brain_region" not in kwargs:
            kwargs["brain_region"]=\
                brain_regions.sscx
        super().__init__(
            *args, **kwargs)

    def get_atlas_ids(self,
            hierarchy,
            condition=Condition([])):
        """The code below applies to the rat SSCx circuit circa 201712DD.
        Future atlases will support the code in the base class
        AtlasBasedLayeredCircuitSpecialization."""
        region=\
            condition.get_value(
                Cell.REGION) #meso-columns termed as region
        if not region:
            region=\
                self.representative_region
        layers=\
            condition.get_value(
                "layer")
        if not layers:
            return\
                hierarchy.collect(
                    "acronym", region, "id")
        if not collections.check(layers):
            return hierarchy.collect(
                "acronym", region, "id"
            ).intersection(
                hierarchy.collect(
                    "acronym", "L{}".format(layers), "id"))
        return hierarchy.collect(
                "acronym", region, "id"
            ).intersection({
                id for layer in layers
                for id in hierarchy.collect(
                        "acronym", "L{}".format(layer), "id")})

    def get_spanning_column_parameter(self,
            column_values=range(7)):
        """..."""
        raise\
            NotImplementedError()


class SSCxAtlasCircuitGeometry(
        AtlasCircuitGeometry):
    """..."""
    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        self.circuit_specialization=\
            SSCxAtlasSpecialization()
        super().__init__(
            circuit,
            *args, **kwargs)
    

def get_sscx_atlas_circuit_model(
        circuit_config,
        animal,
        atlas_path=None,
        *args, **kwargs):
    """..."""
    return\
        AtlasBasedCircuitModel(
            animal=animal,
            brain_region=brain_regions.sscx,
            geometry_type=SSCxAtlasCircuitGeometry,
            circuit_config=circuit_config,
            atlas_path=atlas_path)

class SSCxFakeAtlasSpecialization(
        SSCxAtlasSpecialization):
    """Describe which circuits this specialization applies to.

    Applicable Circuits
    ----------------------------------------------------------------------------
    1. /gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/

    Development Notes
    ----------------------------------------------------------------------------
    A 'CircuitSpecialization' provides code peculiar to specific circuit builds.
    Provide the circuits that this specialization applies to.
    For now we do this in the doc-string. We can provide an attribute that
    is a list containing locations of circuit configurations."""
    
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)
        self.representative_region\
            = "mc2_Column"

    def get_spanning_column_parameter(self,
            column_values=range(7)):
        """..."""
        return\
            Column(
                value_type=str,
                values=["mc{}_Column".format(n)
                        for n in column_values])


class SSCxFakeAtlasCircuitGeometry(
        FakeAtlasCircuitGeometry):
    """..."""
    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        self.circuit_specialization=\
            SSCxFakeAtlasSpecialization()
        super().__init__(
            circuit,
            *args, **kwargs)


def get_sscx_fake_atlas_circuit_model(
        circuit_config,
        animal,
        atlas_path=None,
        *args, **kwargs):
    """..."""
    return\
        FakeAtlasBasedCircuitModel(
            animal=animal,
            brain_region=brain_regions.sscx,
            geometry_type=SSCxFakeAtlasCircuitGeometry,
            circuit_config=circuit_config,
            atlas_path=atlas_path)


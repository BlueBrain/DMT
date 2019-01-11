"""iso cortex models"""

from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import AtlasBasedCircuitSpecialization, AtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import AtlasBasedCircuitModel


class IsoCortexAtlasSpecialization(
        AtlasBasedLayeredCircuitSpecialization):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        if "brain_region" not in kwargs: #if there, it should be a cortex sub-region, eg SSCx
            kwargs["brain_region"]\
                = brain_regions.cortex
        self.atlas_acronym_separator\
            = '' #empty string, i.e. no separator
        self.representative_region\
            = "SSp-ll" #primary Somatosensory lower-limb (i.e. hind-limb)
        super().__init__(
            *args, **kwargs)

    def get_spanning_column_parameter(self,
            regions=["SSp-ll"]):
        """..."""
        raise NotImplementedError(
            """""")


class IsoCortexAtlasBasedCircuitGeometry(
        AtlasCircuitGeometry):
    """AtlasCircuitGeometry whose 'circuit_specialization' has already
    been set to 'CorticalAtlasSpecialization'"""
    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        self.circuit_specialization\
            = IsoCortexAtlasSpecialization(
                *args, **kwargs)
        super().__init__(
            circuit,
            *args, **kwargs)


class IsoCortexAtlasBasedCircuitModel(
        AtlasBasedCircuitModel):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        self.geometry_type\
            = IsoCortexAtlasBasedCircuitGeometry
        super().__init__(
            *args, **kwargs)


def get_iso_cortex_circuit_model(
        circuit_config,
        animal,
        atlas_path=None,
        *args, **kwargs):
    """Factory method that puts together default data
    to create a class...."""
    return\
        IsoCortexAtlasBasedCircuitModel(
            animal=animal,
            brain_region=brain_regions.cortex,
            geometry_type=IsoCortexAtlasBasedCircuitGeometry,
            circuit_config=circuit_config,
            atlas_path=atlas_path)

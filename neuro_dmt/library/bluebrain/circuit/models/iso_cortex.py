"""iso cortex models"""

from bluepy.v2.enums\
    import Cell
from dmt.vtk.utils\
    import collections
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import AtlasBasedLayeredCircuitSpecialization, AtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import AtlasBasedCircuitModel


class IsoCortexAtlasSpecialization(
        AtlasBasedLayeredCircuitSpecialization):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        if "brain_region" not in kwargs: 
            kwargs["brain_region"]=\
                brain_regions.isocortex
        self.atlas_acronym_separator=\
            "" #empty string, i.e. no separator
        self.representative_region=\
            "SSp-ll" #primary Somatosensory lower-limb (i.e. hind-limb)
        super().__init__(
            region_label=Cell.REGION,
            *args, **kwargs)

    def _get_atlas_region_acronyms(self,
            condition):
        """Isocortex circuit's atlas (circa 20190212)
        distinguishes layers 6a and 6b, but the circuit does not."""
        layers=\
            condition.get_value(
                Cell.LAYER)
        region=\
            condition.get_value(
                Cell.REGION)
        if not region:
            region=\
                self.representative_region
        if not layers:
            return [region]
        if not collections.check(layers):
            if layers == 6:
                return [
                    "{}{}{}".format(
                        region,
                        self.atlas_acronym_separator,
                        "6a"),
                    "{}{}{}".format(
                        region,
                        self.atlas_acronym_separator,
                        "6b")]
            else:
                return [
                    "{}{}{}".format(
                        region,
                        self.atlas_acronym_separator,
                        layers)]
        if 6 in layers:
            layers=\
                [str(layer) for layer in layers if layer != 6] + ["6a", "6b"]

        return [
            "{}{}{}".format(
                region,
                self.atlas_acronym_separator,
                layer)
            for layer in layers]
         
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
        AtlasBasedCircuitModel(
            animal=animal,
            brain_region=brain_regions.isocortex,
            geometry_type=IsoCortexAtlasBasedCircuitGeometry,
            circuit_config=circuit_config,
            atlas_path=atlas_path)

"""Test develop (generic) neuro_dmt Validations"""
from neuro_dmt.tests.develop.analysis import *
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSSCxCompositionData as ValidationReferenceData
from neuro_dmt.analysis.comparison.validation.circuit.composition.by_layer\
    import CellDensityValidation\
    ,      CellRatioValidation\
    ,      InhibitorySynapseDensityValidation\
    ,      SynapseDensityValidation
from neuro_dmt.models.bluebrain.circuit.circuit_model\
                                       .atlas_based_circuit_model\
    import AtlasBasedCircuitModel, AtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.specialization import\
    CircuitSpecialization
from neuro_dmt.utils.brain_regions import whole_brain
from neuro_dmt.data.bluebrain.circuit.atlas import get_atlas_data


logger=\
    Logger(
        "Test develop neuro_dmt Validations")

class TestCompositionValidation(
        TestCompositionAnalysis):
    """Test behavior of Composition Validation subclasses"""

    ValidationType=dict(
        cell_density=CellDensityValidation,
        cell_ratio=CellRatioValidation,
        inhibitory_synapse_density=InhibitorySynapseDensityValidation,
        synapse_density=SynapseDensityValidation)

    @classmethod
    def get_validation_type(cls,
            phenomenon):
        """..."""
        return cls.ValidationType[phenomenon]

    def get_instance(self,
            phenomenon,
            circuit_regions=None,
            reference_data=None,
            *args, **kwargs):
        """..."""
        if reference_data is None:
            reference_data = ValidationReferenceData# (phenomenon)
        circuit_regions=\
            circuit_regions if circuit_regions\
            else self._circuit_regions
        ValidationType=\
            self.get_validation_type(
                phenomenon)

        atlas_path = self._circuit_model.bluepy_circuit.atlas.dirpath
        atlas_data = get_atlas_data(phenomenon)(
            atlas_path,
            circuit_regions.values[0])
    
        v = ValidationType(
            phenomenon=phenomenon,
            adapter=self._adapter,
            animal=self._circuit_model.animal,
            measurement_parameters=[
                circuit_regions,
                CorticalLayer()],
            spatial_parameters=[
                circuit_regions,
                CorticalLayer()],
            plotting_parameter=CorticalLayer(),
            reference_data=reference_data.get(phenomenon),
            *args, **kwargs)
        # TODO: label passing should be automatic
        v.reference_data.add_dataset(atlas_data.data.label, atlas_data)
        return v
        


# class MySpecialization(CircuitSpecialization):
#     def target(self):
#         pass

# class MyGeometry(AtlasCircuitGeometry):
#     circuit_specialization=MySpecialization()
#     pass
    
# import bluepy.v2 as bp
# circuit_model = AtlasBasedCircuitModel(geometry_type=MyGeometry, animal='mouse', brain_region=whole_brain,  circuit_config="/gpfs/bbp.cscs.ch/project/proj68/circuits/Isocortex/20190212/CircuitConfig")
# # this is duplicate input
# (bp.Circuit("/gpfs/bbp.cscs.ch/project/proj68/circuits/Isocortex/20190212/CircuitConfig"), circuit_specialization=MySpecialization())

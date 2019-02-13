"""Test develop (generic) neuro_dmt Analysis."""

import os
import numpy as np
from dmt.vtk.measurement\
     import StatisticalMeasurement
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.utils.logging\
    import Logger
from dmt.vtk.utils.collections\
    import Record\
    ,      take
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.measurement.parameter\
    import AtlasRegion\
    ,      CorticalLayer\
    ,      CorticalLayer6abSplit
from neuro_dmt.library.bluebrain.circuit.models.sscx\
   import get_sscx_fake_atlas_circuit_model\
   ,      get_sscx_atlas_circuit_model
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest
from neuro_dmt.models.bluebrain.circuit.adapter\
     import BlueBrainModelAdapter
from neuro_dmt.analysis.circuit.composition.by_layer\
    import CellDensityAnalysis\
    ,      CellRatioAnalysis\
    ,      InhibitorySynapseDensityAnalysis\
    ,      SynapseDensityAnalysis
 

logger=\
    Logger(
        "Test develop neuro_dmt Analysis",
        level=Logger.level.DEVELOP)
bbadapter=\
    BlueBrainModelAdapter(
        brain_region=brain_regions.sscx,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=20)
sscx_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64", "circuits",
        "O1.v6a/20171212",
        "CircuitConfig")
sscx_circuit_model=\
    get_sscx_atlas_circuit_model(
        sscx_circuit_config,
        animal="rat",
        atlas_path=os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj64", "entities",
            "dev", "atlas",
            "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018"))
sscx_circuit_model.geometry.circuit_specialization.representative_region=\
    "mc2_Column"
sscx_circuit=\
    sscx_circuit_model.bluepy_circuit

sscx_atlas_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64", "circuits",
        "S1.v6a/20171206",
        "CircuitConfig")
sscx_atlas_circuit_model=\
    get_sscx_atlas_circuit_model(
        sscx_atlas_circuit_config,
        animal="rat",
        atlas_path=os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64", "circuits",
        "S1.v6a/20171206",
            ".atlas", "C63CB79F-392A-4873-9949-0D347682253A"))
sscx_atlas_circuit=\
    sscx_atlas_circuit_model.bluepy_circuit


iso_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj68/circuits",
        "Isocortex/20190212/",
        "CircuitConfig")
iso_circuit_model=\
    get_iso_cortex_circuit_model(
        iso_circuit_config,
        "mouse")
iso_circuit=\
     iso_circuit_model.bluepy_circuit

class TestCompositionAnalysis:

    """Test behavior of Composition Analysis subclasses"""
    def __init__(self,
            circuit_model=iso_circuit_model,
            sample_size=20,
            sampled_box_shape=50. * np.ones(3),
            *args, **kwargs):
        """"..."""
        self._circuit_model=\
            circuit_model
        self._adapter=\
            BlueBrainModelAdapter(
                brain_region=self._circuit_model.brain_region,
                sample_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                spatial_random_variate=RandomRegionOfInterest,
                model_label="in-silico")
        self._measurement_parameters=[
            AtlasRegion(values=["SSp-ll", "MOp"]),
            CorticalLayer()]
        
    AnalysisType=dict(
        cell_density=CellDensityAnalysis,
        cell_ratio=CellRatioAnalysis,
        inh_syn_density=InhibitorySynapseDensityAnalysis,
        syn_density=SynapseDensityAnalysis)

    def get_instance(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        return self.AnalysisType[phenomenon](
            adapter=self._adapter,
            animal=self._circuit_model.animal,
            measurement_parameters=self._measurement_parameters,
            spatial_parameters=self._measurement_parameters,
            plotting_parameter=CorticalLayer(),
            *args, **kwargs)
            
    def __call__(self,
            phenomenon,
            save=True,
            *args, **kwargs):
        """..."""
        return\
            self.get_instance(
                phenomenon)(
                    self._circuit_model,
                    save_report=True,
                    *args, **kwargs)



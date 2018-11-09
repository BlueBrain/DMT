"""Ready to run (after initialization) validations of BBP Circuit models.
These validations have been hooked up with a model adapter."""
import os
import pandas as pd
from neuro_dmt.utils import brain_regions
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import AtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.atlas.fake.build\
    import FakeAtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import O1CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.circuit_model import\
    CircuitModel,\
    O1CircuitModel,\
    FakeAtlasBasedCircuitModel,\
    AtlasBasedCircuitModel

available\
    = pd.DataFrame([
        {"brain_region": brain_regions.sscx,
         "animal": "Rat",
         "geometry": "O1.v6",
         "circuit_config": os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj64/circuits",
             "O1.v6a", "20171212", "CircuitConfig")},
        {"brain_region": brain_regions.sscx,
         "animal": "Mouse",
         "geometry": "O1.v6",
         "circuit_config": os.path.join(
             "/gpfs/bbp.cscs.ch/project/proj66/circuits",
             "O1", "20180305", "CircuitConfig")},
        {"brain_region": brain_regions.sscx,
         "animal": "rat",
         "geometry": "S1.v6",
         "circuit_config": os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj64/circuits",
             "S1.v6a", "20171206", "CircuitConfig")},
        {"brain_region": brain_regions.ca1,
         "animal": "mouse",
         "geometry": "O1.v6a",
         "circuit_config": os.path.join(
             "/gpfs/bbp.cscs.ch/project/proj42/circuits",
             "O1", "20180904", "CircuitConfig")},
        {"brain_region": brain_regions.ca1,
         "animal": "mouse",
         "geometry": "O1.v6a",
         "circuit_config": os.path.join(
             "/gpfs/bbp.cscs.ch/project/proj42/circuits",
             "O1", "20180219", "CircuitConfig")}])

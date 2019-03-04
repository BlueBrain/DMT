"""Validations for the neocortex (isocortex) circuit to be released
in 2019 March."""

import os
import numpy as np
import pandas as pd
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.library.bluebrain.circuit.models.sscx\
   import get_sscx_atlas_circuit_model
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model

circuits_path=\
        os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj68",
            "circuits")
sscx_circuit_model_20190228=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            circuits_path, "O1",
            "20190228",
            "connectome",
            "functional", "All",
            "CircuitConfig"),
        animal="mouse",
        region_label="region")
sscx_circuit_model_20190228_nrn=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            circuits_path, "O1",
            "20190228",
            "connectome",
            "functional-nrn", "All",
            "CircuitConfig"),
        animal="mouse",
        region_label="region")


from neuro_dmt.tests.develop.neocortex.analysis\
    import TestCompositionAnalysis
from neuro_dmt.tests.develop.neocortex.validation\
    import TestCompositionValidation

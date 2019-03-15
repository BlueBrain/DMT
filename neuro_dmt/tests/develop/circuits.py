"""Available circuits for testing."""
import os
from neuro_dmt.library.bluebrain.circuit.models.sscx\
   import get_sscx_atlas_circuit_model
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model

circuits_path=\
        os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj68",
            "circuits")
sscx_circuit_model_2018=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj66",
            "circuits", "O1",
            "20180305",
            "CircuitConfig"),
        animal="mouse",
        region_label="region")
sscx_circuit_model=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            circuits_path, "O1",
            "20190307",
            "connectome/functional/All",
            "CircuitConfig"),
        animal="mouse",
        region_label="region")
sscx_circuit_model_nrn=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            circuits_path, "O1",
            "20190307",
            "connectome",
            "functional-nrn", "All",
            "CircuitConfig"),
        animal="mouse",
        region_label="region")
sscx_circuit_model_aff=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            circuits_path, "O1",
            "20190307",
            "connectome",
            "functional", "All",
            "CircuitConfig-aff"),
        animal="mouse",
        region_label="region")
sscx_circuit_model_eff=\
    get_sscx_atlas_circuit_model(
        os.path.join(
            circuits_path, "O1",
            "20190307",
            "connectome",
            "functional", "All",
            "CircuitConfig-eff"),
        animal="mouse",
        region_label="region")


def IsocortexCircuitModel(
        region,
        hemisphere="left",
        direction="eff"):
    "..."
    assert\
        direction in {"eff", "aff"}
    assert\
        hemisphere in {"left", "right"}
    circuit_config_path=\
        os.path.join(
            circuits_path, "Isocortex",
            "20190307",
            "connectome/functional",
            "{}@{}".format(region, hemisphere),
            "CircuitConfig-{}".format(direction))
    return get_iso_cortex_circuit_model(
        circuit_config_path,
        animal="mouse",
        region_label="region",
        hemisphere=hemisphere)


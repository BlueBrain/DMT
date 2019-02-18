"""Test develop MultiReference Data"""

import traceback
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSSCxCompositionData
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSSCxCompositionData
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.connectome\
    import RatSSCxConnectomeData

log=\
    Logger(
        """Test develop multi reference data""",
        level=Logger.level.DEBUG)
exceptions= []
try:
    mouse_cell_density_data=\
        MouseSSCxCompositionData.get(
            "cell_density")
    assert\
        mouse_cell_density_data is not None
except Exception as exception:
    log.failure(
        log.get_source_info(),
        """could not load cell density data""",
        """Exception {}""".format(exception))
    exceptions.append(
        {"traceback": traceback.format_exc(),
         "exception": exception})
try:
    mouse_cell_ratio_data=\
        MouseSSCxCompositionData.get(
            "cell_ratio")
    assert\
        mouse_cell_ratio_data is not None
except Exception as exception:
    log.failure(
        log.get_source_info(),
        """could not load cell ratio data""",
        """Exception {}""".format(exception))
    exceptions.append(
        {"traceback": traceback.format_exc(),
         "exception": exception})
try:
    mouse_inhibitory_synapse_density_data=\
        MouseSSCxCompositionData.get(
            "inhibitory_synapse_density")
    assert\
        mouse_inhibitory_synapse_density_data is not None
except Exception as exception:
    log.failure(
        log.get_source_info(),
        """could not load inhibitory_synapse_density_data data""",
        """Exception {}""".format(exception))
    exceptions.append(
        {"traceback": traceback.format_exc(),
         "exception": exception})
try:
    mouse_synapse_density_data=\
        MouseSSCxCompositionData.get(
            "synapse_density")
    assert\
        mouse_synapse_density_data is not None
except Exception as exception:
    log.failure(
        log.get_source_info(),
        """could not load synapse density data""",
        """Exception {}""".format(exception))
    exceptions.append(
        {"traceback": traceback.format_exc(),
         "exception": exception})

try:
    rat_cell_density_data=\
        RatSSCxCompositionData.get(
            "cell_density")
    assert\
        rat_cell_density_data is not None
except Exception as exception:
    log.failure(
        log.get_source_info(),
        """could not load cell density data""",
        """Exception {}""".format(exception))
    exceptions.append(
        {"traceback": traceback.format_exc(),
         "exception": exception})
try:
    rat_cell_ratio_data=\
        RatSSCxCompositionData.get(
            "cell_ratio")
    assert\
        rat_cell_ratio_data is not None
except Exception as exception:
    log.failure(
        log.get_source_info(),
        """could not load cell ratio data""",
        """Exception {}""".format(exception))
    exceptions.append(
        {"traceback": traceback.format_exc(),
        "exception": exception})
try:
    rat_inhibitory_synapse_density_data=\
        RatSSCxCompositionData.get(
            "inhibitory_synapse_density")
    assert\
        rat_inhibitory_synapse_density_data is not None
except Exception as exception:
    log.failure(
        log.get_source_info(),
        """could not load inhibitory_synapse_density_data data""",
        """Exception {}""".format(exception))
    exceptions.append(
        {"traceback": traceback.format_exc(),
         "exception": exception})
try:
    rat_synapse_density_data=\
        RatSSCxCompositionData.get(
            "synapse_density")
    assert\
        rat_synapse_density_data is not None
except Exception as exception:
    log.failure(
        log.get_source_info(),
        """could not load synapse density data""",
        """Exception {}""".format(exception))
    exceptions.append(
        {"traceback": traceback.format_exc(),
         "exception": exception})
try:
    rat_pair_synapse_count_data=\
        RatSSCxConnectomeData.get(
            "pair_synapse_count")
    assert\
        rat_pair_synapse_count_data is not None
except Exception as exception:
    log.failure(
        log.get_source_info(),
        """could not load pair synapse count data""",
        """Exception {}""".format(exception))
    exceptions.append(
        {"traceback": traceback.format_exc(),
         "exception": exception})


if len(exceptions):
    log.failure(
        "Test failures: ")
    for exception in exceptions:
        log.failure(
            "Failure {}".format(exception["exception"]),
            "Traceback {}".format(exception["traceback"]))
else:
    log.success(
        """All Good, it seems""")

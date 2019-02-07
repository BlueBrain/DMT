"""Circuit connectome data for the Somatosensory cortex."""
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.utils import brain_regions
from neuro_dmt.models.bluebrain.circuit.parameters\
    import Mtype
from neuro_dmt.data.bluebrain.circuit.cortex\
    import CortexConnectomeData

class SSCxConnectomeData(
        CortexConnectomeData):
    """..."""
    _available_data = []

    def __init__(self,
            animal,
            phenomenon,
            *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon,
            animal=animal,
            pathway_parameters=[
                Mtype(label="pre_mtype"),
                Mtype(label="post_mtype")],
            cell_group_parameters=[Mtype()],
            brain_region=brain_regions.sscx,
            *args, **kwargs)

    @classmethod
    def get(cls,
        phenomenon,
        *args, **kwargs):
        """Get reference data by phenomenon.

        Parameters
        --------------------------------------------------------------------
        phenomenon :: Either[str, Phenomenon]"""

        plabel=\
            (phenomenon.label
             if isinstance(phenomenon, Phenomenon) else 
             phenomenon)
        if not cls._available_data:
            cls._available_data=\
                cls.get_available_data()
        try:
            return cls._available_data[plabel](*args, **kwargs)
        except KeyError as e:
            msg = "No data available for {}\n".format(phenomenon)
            msg += "Available data:\n"
            i = 0
            for k in available_data.keys():
                i += 1
                msg += "\t({}) {}\n".format(i, k)
            stderr.write(msg)
        return None

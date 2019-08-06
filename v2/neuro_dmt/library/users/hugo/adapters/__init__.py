import warnings
import numpy as np
import bluepy.v2 as bp
from abc import ABCMeta, abstractmethod
from neuro_dmt.library.users.hugo.adapters.atlas import AtlasAdapter


LAYER = 'layer'
MTYPE = 'mtype'
SYN_CLASS = 'sclass'
MORPH_CLASS = 'mclass'


# TODO: wrap data in adapter-like structure, get measurements
#       by matching measurement_parameters. This ensures that
#       the 'by' things will match up, and data not also requested
#       of a model will not (and does not need to be) displayed
#       also, data requested of model and not in data can
#       be displayed as NaN
#       lets us construct DataFrames between mismatched results
class CircuitAdapter(metaclass=ABCMeta):
    """
    adapter for bluepy circuits
    infers what functionality is needed based on the circuit provided
    (work in progress, presently only supports atlas based O1 circuits
    """
    def __init__(self, circuit_config):
        """initialize, for now assume atlas"""
        self._circuit = bp.Circuit(circuit_config)
        self._adaptedAtlas = AtlasAdapter(self._circuit.atlas)

    # TODO:: would it be better to have the adapter accept parameters as
    #        kwargs
    def cell_density(self, parameters):
        """
        get cell density from the circuit
        """
        cell_query = self._translate_query_cells(parameters)
        ncells = self._circuit.cells.get(cell_query).shape[0]
        mask = self._adaptedAtlas.mask_for_query(parameters)
        nvoxels = np.sum(mask)
        voxel_volume = self._adaptedAtlas.voxel_volume * 1e-9
        print(voxel_volume)
        print(ncells)
        return ncells / (nvoxels * voxel_volume)

    def mtypes(self):
        return [self._mtype_parameters(mtype_name) for mtype_name in
                                       self._circuit.cells.get().mtype.unique()]

    def _mtype_parameters(self, mtype_name):
        layer, mtype = mtype_name.split("_")
        if len(layer) > 2:
            layer = ["L{}".format(num) for num in layer[1:]]
        return dict(layer=layer, mtype=mtype)

    # TODO: support lists for each param
    def _translate_query_cells(self, parameters):
        cell_query = {}
        # TODO: clean way to abstract this from the adapters?
        for key, value in parameters.items():
            if key == LAYER:
                if isinstance(value, str):
                    value = int(value[1])
                cell_query[bp.Cell.LAYER] = value
            elif key == MTYPE:
                spl = value.split("_")
                if len(spl) > 1:
                    raise TypeError(
                        "Mtypes in queries to adapter should not be in form"
                        "<layer>_<name>, but simply <name>")
                ql = parameters.get(LAYER, False)
                if ql:
                    if isinstance(ql, tuple):
                        ql = "".join([l[1] for l in ql])

                    value = "_".join([ql, value])
                else:
                    value = [mt for mt in self._mtypes()
                             if mt.split("_")[-1] == value]
                cell_query[bp.Cell.MTYPE] = value
            elif key == SYN_CLASS:
                cell_query[bp.Cell.SYNAPSE_CLASS] = value
            elif key == MORPH_CLASS:
                cell_query[bp.Cell.MORPH_CLASS] = value
        return cell_query

    def _translate_query_atlas(self, parameters):
        atlas_region = parameters.get('layer', 'O1')
        return atlas_region

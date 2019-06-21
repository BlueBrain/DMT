import warnings
import numpy as np
import bluepy.v2 as bp
# TODO: what is the most elegant way to require subclasses to define
#       required methods

LAYER = 'layer'
MTYPE = 'mtype'
SYN_CLASS = 'sclass'
MORPH_CLASS = 'mclass'


class AtlasCircuitAdapter:

    def __init__(self, circuit_config):
        self._circuit = bp.Circuit(circuit_config)

    def cell_density(self, query):
        """get cell density from the circuit"""
        cell_query = self._translate_query_cells(query)
        atlas_region = self._translate_query_atlas(query)
        ncells = self._circuit.cells.get(cell_query).shape[0]
        mask = self._circuit.atlas.get_region_mask(atlas_region)
        nvoxels = np.sum(mask.raw)
        # TODO: number depends on units, how to organise that?
        #       does the .nrrd contain some info?
        voxel_volume = np.prod(mask.voxel_dimensions) * 1e-9
        return ncells / nvoxels * voxel_volume


class O1Adapter(AtlasCircuitAdapter):

    def _mtypes(self):
        return self._circuit.cells.mtypes

    def mtypes(self):
        return [mtype.split("_")[-1] for mtype in self._mtypes]

    def _translate_query_cells(self, query):
        cell_query = {}
        # TODO: clean way to abstract this from the adapters?
        for key, value in query.items():
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
                ql = query.get(LAYER, False)
                if ql:
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

    def _translate_query_atlas(self, query):
        atlas_region = query.get('layer', 'O1')
        return atlas_region

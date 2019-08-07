import warnings
import numpy as np
import bluepy.v2 as bp
from abc import ABCMeta, abstractmethod
from neuro_dmt.library.users.hugo.adapters.atlas import AtlasAdapter
from neuro_dmt.library.users.hugo.adapters.utils import _list_if_not_list

LAYER = 'layer'
MTYPE = 'mtype'
SYN_CLASS = 'sclass'
MORPH_CLASS = 'mclass'
COLUMN = 'column'
REGION = 'region'


# TODO: DOCSTRINGS DOCSTRINGS DOCSTRINGS
# TODO: what is the best way to deal with components that depend on other
#       components?
#       OPTION1: pass other components at initialization?
#         (will require changing of component interfaces)
#       OPTION2: pass each component an instance of the parent object
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
        # TODO: there has to be a better way to do this
        if is_O1(self._circuit):
            represented_region = None
        else:
            represented_region = {REGION: "Isocortex"}
        self._adaptedAtlas = AtlasAdapter(self._circuit.atlas,
                                          represented_region)
        self._layerTranslator = _LayerTranslator(self._circuit)
        self._mtypeTranslator = _MtypeTranslator(self, self._circuit)
        self._columnTranslator = _ColumnTranslator(self._circuit)
        self._regionTranslator = _RegionTranslator(self._circuit)

    # TODO:: would it be better to have the adapter accept parameters as
    #        kwargs
    def cell_density(self, parameters):
        """
        get cell density from the circuit
        """
        cell_parameters = self._translate_parameters_cells(parameters)
        print(cell_parameters)
        ncells = self._circuit.cells.get(cell_parameters).shape[0]
        mask = self._adaptedAtlas.mask_for_parameters(parameters)
        nvoxels = np.sum(mask)
        voxel_volume = self._adaptedAtlas.voxel_volume * 1e-9
        return ncells / (nvoxels * voxel_volume)

    def mtypes(self):
        return [self._mtype_parameters(mtype_name) for mtype_name in
                self._mtypes()]

    def _mtypes(self):
        return sorted(self._circuit.cells.mtypes)

    def _mtype_parameters(self, mtype_name):
        layer, mtype = mtype_name.split("_")
        if len(layer) > 2:
            layer = ["L{}".format(num) for num in layer[1:]]
        return dict(layer=layer, mtype=mtype)

    # TODO: support lists for each param
    def _translate_parameters_cells(self, parameters):
        cell_parameters = {}
        # TODO: clean way to abstract this from the adapters?
        for key, value in parameters.items():
            value = _list_if_not_list(value)
            if len(value) == 0:
                pass
            elif key == LAYER:
                self._layerTranslator.translate(cell_parameters, value)
            elif key == MTYPE:
                self._mtypeTranslator.translate(cell_parameters, value)
            elif key == SYN_CLASS:
                cell_parameters[bp.Cell.SYNAPSE_CLASS] = value
            elif key == MORPH_CLASS:
                cell_parameters[bp.Cell.MORPH_CLASS] = value
            elif key == COLUMN:
                self._columnTranslator.translate(cell_parameters, value)
            elif key == REGION:
                self._regionTranslator.translate(cell_parameters, value)
        return cell_parameters


class Translator:

    def __init__(self, circuit):
        self._circuit = circuit

    # Abstract class will not work, so NotImplementedError
    def translate(self, parameter_dict, value):
        raise NotImplementedError(
            "this method needs to be overwritten before use")


class _LayerTranslator(Translator):

    def __init__(self, circuit):
        if cells_have_int_layers(circuit):
            self.translate = self._int_layers
        super().__init__(circuit)

    def _int_layers(self, cell_parameters, value):
        cell_parameters[bp.Cell.LAYER] = [int(v[1]) for v in value]


class _MtypeTranslator(Translator):

    def __init__(self, adapted, circuit):
        self._adapted = adapted
        self.translate = self._from_circuit_mtypes
        super().__init__(circuit)

    def _from_circuit_mtypes(self, cell_parameters, value):
        v = []
        for mtype in value:
            if len(mtype.split("_")) > 1:
                raise TypeError(
                    "Mtypes in queries to adapter should not be in "
                    "form <layer>_<name>, but simply <name>")
            # TODO: is it bad practice to use parent object's private method?
            print(mtype, self._adapted._mtypes())
            v += [mt for mt in self._adapted._mtypes()
                  if mt.endswith(mtype)]
        cell_parameters[bp.Cell.MTYPE] = v


class _ColumnTranslator(Translator):

    def __init__(self, circuit):
        if is_O1(circuit):
            self.translate = self._region_column
        else:
            self.translate = self._no_column
        super().__init__(circuit)

    def _region_column(self, cell_parameters, value):
        cell_parameters[bp.Cell.REGION] =\
            [v + "_Column" for v in value]

    def _no_column(self, cell_parameters, value):
        Warning("column undefined for this model, ignorning parameter")
        return


class _RegionTranslator(Translator):

    def __init__(self, circuit):
        if is_O1(circuit):
            self.translate = self._no_region
        else:
            self.translate = self._separate_hemispheres
        super().__init__(circuit)

    def _no_region(self, cell_parameters, value):
        Warning("region is not defined for O1 models")
        return

    def _separate_hemispheres(self, cell_parameters, value):
        cell_parameters[bp.Cell.REGION] = []
        for region in value:
            cell_parameters[bp.Cell.REGION] += [region + "@left",
                                                region + "@right"]
        return


def is_O1(circuit):
    from neuro_dmt.library.users.hugo.adapters.atlas import is_O1_atlas
    return is_O1_atlas(circuit.atlas)


def cells_have_int_layers(circuit):
    alayer = circuit.cells.get(1)[bp.Cell.LAYER]
    return alayer in [1, 2, 3, 4, 5, 6]

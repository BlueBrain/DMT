import warnings
import numpy as np
import bluepy.v2 as bp
from os.path import dirname, join
from neuro_dmt.library.users.hugo.adapters.atlas import AtlasAdapter
from neuro_dmt.library.users.hugo.adapters.utils import _list_if_not_list,\
    LAYER, MTYPE, SYN_CLASS, MORPH_CLASS, COLUMN, REGION,\
    PRESYNAPTIC, POSTSYNAPTIC


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


def is_O1(circuit):
    """check if is O1 circuit"""
    from neuro_dmt.library.users.hugo.adapters.atlas import is_O1_atlas
    return circuit.atlas is None or is_O1_atlas(circuit.atlas)


def cells_have_int_layers(circuit):
    """check if layers are represented as
    integers in circuit's CellCollection"""
    alayer = circuit.cells.get(1)[bp.Cell.LAYER]
    return alayer in [1, 2, 3, 4, 5, 6]


def region_in_cells(circuit):
    try:
        circuit.cells.get(1).region
        return True
    except AttributeError:
        return False


def _mtypes(circuit):
    """retrieve raw mtypes from the circuit"""
    return sorted(circuit.cells.mtypes)


class Translator:
    """Base class for translators"""

    def __init__(self, circuit):
        self._circuit = circuit

    # Abstract class will not work, so NotImplementedError
    def translate(self, parameter_dict, value):
        raise NotImplementedError(
            "this method needs to be overwritten before use")


class _LayerTranslator(Translator):
    """translates layers from measurement parameter to cell property"""

    def __init__(self, circuit):
        if cells_have_int_layers(circuit):
            self.translate = self._int_layers
        super().__init__(circuit)

    def _int_layers(self, cell_properties, value):
        """
        layers in circuit are integers.
        sets 'layer' in cell_properties to integer representation of value
        """
        cell_properties[bp.Cell.LAYER] = [int(v[1]) for v in value]


class _MtypeTranslator(Translator):
    """translates mtype from measurement parameter to cell property"""
    def __init__(self, circuit):
        self.translate = self._from_circuit_mtypes
        super().__init__(circuit)

    def _from_circuit_mtypes(self, cell_properties, value):
        """infers the values for mtype property from raw mtypes in circuit"""
        v = []
        for mtype in value:
            if len(mtype.split("_")) > 1:
                # warning for now
                # once mtype-name translation is implemented, we can revert
                # to TypeError
                warnings.warn(Warning(
                    "Mtypes in queries to adapter should not be in "
                    "form <layer>_<name>, but simply <name>. "
                    "recieved mtype: {}".format(mtype)))
            # TODO: is it bad practice to use parent object's private method?
            thismt = [mt for mt in _mtypes(self._circuit)
                      if "_".join(mt.split("_")[1:]) == mtype]
            if len(thismt) == 0:
                warnings.warn(Warning("mtype: {} not present in circuit"
                                      .format(mtype)))
            v += thismt
        cell_properties[bp.Cell.MTYPE] = v


class _ColumnTranslator(Translator):
    """translates column from measurement parameter to cell property"""
    def __init__(self, circuit):
        # TODO: instead of testing O1, I should test properties more directly
        if is_O1(circuit):
            celldf = circuit.cells.get()
            if bp.Cell.HYPERCOLUMN in celldf.columns:
                self.translate = self._hypercolumn
            else:
                self.translate = self._region_column
        else:
            self.translate = self._no_column
        super().__init__(circuit)

    def _region_column(self, cell_properties, value):
        """column is represented as region in circuit's CellCollection"""
        cell_properties[bp.Cell.REGION] =\
            [v + "_Column" for v in value]

    def _hypercolumn(self, cell_properties, value):
        """column refers to hypercolumn in circuit"""
        cell_properties[bp.Cell.HYPERCOLUMN] = [int(v[-1]) for v in value]
        return

    def _no_column(self, cell_properties, value):
        """column not defined for this circuit"""
        warnings.warn(
            Warning("column undefined for this model, ignorning parameter"))
        return


class _RegionTranslator(Translator):
    """translates region from measurement parameter to cell property"""
    def __init__(self, circuit):
        if is_O1(circuit):
            self.translate = self._no_region
        elif region_in_cells(circuit):
            self.translate = self._separate_hemispheres
        else:
            self.translate = self._region_not_in_cells
        super().__init__(circuit)

    def _no_region(self, cell_properties, value):
        """region not defined for this circuit (O1)"""
        warnings.warn(
            Warning("region is not defined for O1 models"))
        return

    def _region_not_in_cells(self, cell_properties, value):
        """
        cells don't have a property corresponding to region,
        but regions are defined in the atlas, so we don't need to warn
        """
        return

    def _separate_hemispheres(self, cell_properties, value):
        """each region consists of two hemispheres"""
        cell_properties[bp.Cell.REGION] = []
        for region in value:
            cell_properties[bp.Cell.REGION] += [region + "@left",
                                                region + "@right"]
        return


def get_regions_represented(circuit):
    cells = circuit.cells.get(properties=[bp.Cell.X, bp.Cell.Y, bp.Cell.Z])
    br = circuit.atlas.load_data("brain_regions")
    cells_indices = br.positions_to_indices(cells.values)
    regionids = np.unique(
        br.raw[tuple(cells_indices[..., ax]
                     for ax in range(cells_indices.shape[-1]))])
    return np.isin(br.raw, regionids)


def _flatten(lst):
    """flatten a list which may contain lists"""
    out = []
    for item in lst:
        if isinstance(item, list):
            out += _flatten(item)
        else:
            out.append(item)
    return out


class CircuitAdapter:
    """
    adapter for bluepy circuits
    infers what functionality is needed based on the circuit provided
    currently fully supports atlas based O1(not all), S1,
    and Isocortex circuits
    and partially supports old (no atlas) O1 SSCX circuits.
    """
    def __init__(self, circuit_config):
        """compose an appropriate adapter from circuit_config"""
        self._circuit = bp.Circuit(circuit_config)
        # TODO: there has to be a better way to do this
        try:
            atlas = self._circuit.atlas
        except KeyError:
            # no atlas in config. look for .atlas dir
            from voxcell.nexus.voxelbrain import Atlas
            import glob
            apath = glob.glob(join(dirname(circuit_config),
                                   ".atlas/*"))
            if len(apath) == 1:
                atlas = Atlas.open(apath[0])
            elif len(apath) == 0:
                atlas = None
            self._circuit.atlas = atlas

        if atlas is not None:
            if is_O1(self._circuit):
                represented_region = None
            else:
                represented_region = get_regions_represented(self._circuit)

            self._adaptedAtlas = AtlasAdapter(atlas, represented_region)
        else:
            warnings.warn(
                Warning("old circuit with no atlas,"
                        " cell_density method is unavailable"))
            self.cell_density = self._cell_density_no_atlas

        self._layerTranslator = _LayerTranslator(self._circuit)
        self._mtypeTranslator = _MtypeTranslator(self._circuit)
        self._columnTranslator = _ColumnTranslator(self._circuit)
        self._regionTranslator = _RegionTranslator(self._circuit)

    def _cell_density_no_atlas(self, *args):
        raise NotImplementedError(
            "cell density is currently not supported"
            " for this circuit type")

    # TODO:: would it be better to have the adapter accept parameters as
    #        kwargs
    def cell_density(self, parameters):
        """
        get cell density from the circuit

        Arguments:
            parameters: a dict whose key-value pairs correspond to
                        measurement parameters
                        TODO: reference measurement parameter documentation

        Returns:
            density: the density in cells/mm^3 under the provided parameters
        """
        cell_properties = self._translate_parameters_cells(parameters)
        ncells = self._circuit.cells.get(cell_properties).shape[0]
        mask = self._adaptedAtlas.mask_for_parameters(parameters)
        nvoxels = np.sum(mask)
        voxel_volume = self._adaptedAtlas.voxel_volume * 1e-9
        return ncells / (nvoxels * voxel_volume)

    def mtypes(self):
        """
        get a list of all mtypes in the circuit

        Returns:
           list of parameter sets describing mtypes
           (e.g. {'layer': 'L2', 'mtype': 'MC'})
        """
        return [self._mtype_parameters(mtype_name) for mtype_name in
                _mtypes(self._circuit)]

    def connection_probability(self, measurement_parameters,
                               nsamples=100, sample_size=50):
        """
        get the connection probabilty for two groups of cells

        Arguments:
            measurement_parameters: a dict with keys {} and {},
                                    each with a dict value containing
                                    parameters identifying the two cell groups
            nsamples: how many samples to take. set to None to take whole group
            sample_size: how many cells to sample from each group
                         actual number of pairs sampled will be this squared

        Returns:
            float or list of floats: connection probabiltiy
        """.format(PRESYNAPTIC, POSTSYNAPTIC)
        return self._sample_connectome(self._connection_probability,
                                       nsamples, sample_size,
                                       measurement_parameters)

    def _connection_probability(self, connectome, pre_ids, post_ids):
        num_conn = len(tuple(connectome.iter_connections(
            pre=pre_ids, post=post_ids)))
        num_pairs = pre_ids.shape[0] * post_ids.shape[0]
        return num_conn / num_pairs

    # TODO: get all data from iter_connections, cache results?
    def _sample_connectome(self, method, nsamples, sample_size,
                           measurement_parameters, *args, **kwargs):
        """
        sample pre- and post- synaptic groups and apply method to them

        Arguments:
            method: method to use on the samples of cells to measure a property
                    of the connectome. Must take arguments:
                         connectome, pre_gids, post_gids
            nsamples: how many samples to take. set to None to take whole group
            sample_size: how many cells to sample from each group
                         actual number of pairs sampled will be this squared
            measurement_parameters: a dict with keys {} and {},
                                    each with a dict value containing
                                    parameters identifying the two cell groups
        """.format(PRESYNAPTIC, POSTSYNAPTIC)
        pre_cells = self.get_cells(measurement_parameters[PRESYNAPTIC])\
                        .index.values
        post_cells = self.get_cells(measurement_parameters[POSTSYNAPTIC])\
                         .index.values
        total_pairs = pre_cells.shape[0] * post_cells.shape[0]
        if total_pairs == 0:
            return np.nan
        connectome = self.get_connectome(measurement_parameters)
        if (nsamples is None) or ((nsamples * sample_size**2) >= total_pairs):
            return method(connectome, pre_cells, post_cells,
                          *args, **kwargs)
        else:
            return _flatten(
                [method(
                    connectome,
                    np.random.choice(pre_cells, sample_size),
                    np.random.choice(post_cells, sample_size),
                    *args, **kwargs)
                 for sample in range(nsamples)])

    # TOOD: should repeated docstrings always be copied? or referenced
    def synapses_per_connection(self, measurement_parameters,
                                nsamples=100, sample_size=50):
        """
        get the number of synapses per connection between two groups of cells

        Arguments:
            measurement_parameters: a dict with keys {} and {},
                                    each with a dict value containing
                                    parameters identifying the two cell groups
            nsamples: how many samples to take. set to None to take whole group
            sample_size: how many cells to sample from each group
                         actual number of pairs sampled will be this squared

        Returns:
            float or list of floats: number of synapses per connection
        """.format(PRESYNAPTIC, POSTSYNAPTIC)
        return self._sample_connectome(self._synapses_per_connection,
                                       nsamples, sample_size,
                                       measurement_parameters)

    def _synapses_per_connection(self, connectome, pre_ids, post_ids):
        """
        get the synapses per connection for each connection between
        the cells identified by pre_ids and post_ids
        """
        return [conn[2] for conn in connectome.iter_connections(
            pre=pre_ids, post=post_ids, return_synapse_count=True)]

    def get_cells(self, parameters, properties=None):
        """
        get cells satisfying parameters 'parameters'

        Arguments:

            parameters: dict of parameter name-value pairs
                        identifying the cell group

            # TODO: reference parameter documentation

        Returns:
            DataFrame of cell properties
        """
        return self._circuit.cells.get(
            self._translate_parameters_cells(parameters),
            properties=properties)

    def get_connectome(self, parameters):
        # TODO: make dummy connectome that selects chunks for hemispheres,
        #       and forwards operations seperately to the two before pooling
        #       the result.
        return self._circuit.connectome

    def _mtype_parameters(self, mtype_name):
        """
        translate a raw mtype name (generally <layer>_<mtype>) to a
        parameter dict (e.g. {LAYER: <layer>, MTYPE: <mtype>})

        Arguments:
            mtype_name: string, raw mtype name as in the circuit

        Returns:
            mtype_parameters: a dict of measurement parameters
                             representing this mtyoe
        """
        mttup = mtype_name.split("_")
        layer = mttup[0]
        mtype = "_".join(mttup[1:])
        if len(layer) > 2:
            layer = ["L{}".format(num) for num in layer[1:]]
        return dict(layer=layer, mtype=mtype)


    # TODO: support lists for each param
    def _translate_parameters_cells(self, parameters):
        """
        translate measurement parameters to a bluepy query

        Arguments:
            parameters: a dict of measurement parameters

        Returns:
            cell_properties: a dict of bluepy cell properties
        """
        cell_properties = {}
        # TODO: clean way to abstract this from the adapters?
        for key, value in parameters.items():
            value = _list_if_not_list(value)
            if len(value) == 0:
                pass
            elif key == LAYER:
                self._layerTranslator.translate(cell_properties, value)
            elif key == MTYPE:
                self._mtypeTranslator.translate(cell_properties, value)
            elif key == SYN_CLASS:
                cell_properties[bp.Cell.SYNAPSE_CLASS] = value
            elif key == MORPH_CLASS:
                cell_properties[bp.Cell.MORPH_CLASS] = value
            elif key == COLUMN:
                self._columnTranslator.translate(cell_properties, value)
            elif key == REGION:
                self._regionTranslator.translate(cell_properties, value)
        return cell_properties

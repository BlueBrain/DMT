"""
A class that represents circuit models developed at the Blue Brain Project.
"""
import warnings
import numpy as np
import bluepy.v2 as bp
import neuro_dmt.terminology as terminology
from neuro_dmt.terminology.atlas import translate
from .atlas import CircuitAtlas, _list_if_not_list


def is_O1(circuit):
    """check if is O1 circuit"""

    def is_O1_atlas(atl):
        rmap = atl.load_region_map()
        return rmap.find("O1", "acronym")

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


def is_paxinos_watson(circuit):
    return 'S1' in circuit.cells.get()[bp.Cell.REGION][0]


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
        else:
            self.translate = self.string_layers
        super().__init__(circuit)

    def string_layers(self, cell_properties, value):
        # TODO: better solution than this
        cell_properties[bp.Cell.LAYER] = [v if v != "RT" else "Rt"
                                          for v in value]

    def _int_layers(self, cell_properties, value):
        """
        layers in circuit are integers.
        sets 'layer' in cell_properties to integer representation of value
        """
        cell_properties[bp.Cell.LAYER] = [int(v[1]) for v in value]


class _MSClassTranslator(Translator):
    """translates morphology_subclass to cell group query"""
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
                warnings.warn(Warning("morphology_subclass: {} "\
                                      "not present in circuit"
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
            if is_paxinos_watson(circuit):
                self.translate = self._paxinos_watson_regions
            else:
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
        TODO: dont we?
        """
        return

    def _paxinos_watson_regions(self, cell_properties, value):
        cell_properties[bp.Cell.REGION] = [
            translate.ABI_to_Paxinos(r) for r in value]

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


class CircuitModel:
    """
    adapter for bluepy circuits
    infers what functionality is needed based on the circuit provided
    currently fully supports atlas based O1(not all), S1,
    and Isocortex circuits
    and partially supports old (no atlas) O1 SSCX circuits.
    """

    # TODO: define all components as properties

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
            from os.path import join, dirname
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

            self.circuit_atlas = CircuitAtlas(
                path=atlas.dirpath, represented_region=represented_region)

        else:
            warnings.warn(
                Warning("old circuit with no atlas,"
                        " cell_density method is unavailable"))
            self.cell_density = self._cell_density_no_atlas

        self._layerTranslator = _LayerTranslator(self._circuit)
        self._mscTranslator = _MSClassTranslator(self._circuit)
        self._columnTranslator = _ColumnTranslator(self._circuit)
        self._regionTranslator = _RegionTranslator(self._circuit)

    def _cell_density_no_atlas(self, *args):
        raise NotImplementedError(
            "cell density is currently not supported"
            " for this circuit type")

    @terminology.use(terminology.circuit.region,
                     terminology.circuit.layer,
                     terminology.circuit.mesocolumn,
                     terminology.circuit.height,
                     terminology.circuit.depth,
                     terminology.cell.mtype,
                     terminology.cell.synapse_class,
                     terminology.cell.morphology_class,
                     terminology.cell.morphology_subclass)
    def cell_density(self, **parameters):
        """
        get cell density from the circuit

        Arguments:
            {parameters}

        Returns:
            density: the density in cells/mm^3 under the provided parameters
        """
        ncells = self.get_cells(**parameters).shape[0]
        mask = self.circuit_atlas.get_mask(**{
            param: value for param, value in parameters.items()
            if param in terminology.circuit.all})
        nvoxels = np.sum(mask)
        voxel_volume = self.circuit_atlas.voxel_volume * 1e-9
        return ncells / (nvoxels * voxel_volume)

    def mtypes(self, properties=(terminology.circuit.layer,
                                 terminology.cell.mtype,
                                 terminology.cell.morphology_subclass)):
        """
        get a list of all mtypes in the circuit

        Returns:
           list of parameter sets describing mtypes
           (e.g. {'layer': 'L2', 'mtype': 'MC'})
        """
        supported_props =(
            terminology.circuit.layer,
            terminology.cell.mtype,
            terminology.cell.morphology_subclass,
            terminology.cell.synapse_class)
        for p in properties:
            if p not in supported_props:
                raise ValueError(
                    "property {} not currently supported for"
                    " mtypes method, sorry!".format(p))
        return [self._mtype_parameters(mtype_name, properties)
                for mtype_name in _mtypes(self._circuit)]

    # TODO: perhaps sample_size should be the only kwarg
    #       and refer to the number of pairs sampled
    # TODO: these methods are probably too high level - they contain elements of
    #       'experimental procedure', and this is why it is difficult to conceptualize
    #       a validation with a histogram of connprob by soma distance
    #       probably these methods should just be to sample pairs/connections in a pathway
    #       returning requested properties of each connection
    #       then e.g. by soma distance can be handled by the measurement
    @terminology.use(
        terminology.cell.presynaptic,
        terminology.cell.postsynaptic)
    def connection_probability(self, sample_size=50, **parameters):
        """
        get the connection probabilty for two groups of cells

        Arguments:
           {parameters}
           sample_size: the number of pairs to take for one sample
        Returns:
            float or list of floats: connection probabiltiy
        """
        return self._sample_connectome(self._connection_probability,
                                       sample_size=sample_size,
                                       **parameters)

    def _connection_probability(self, connectome, pre_ids, post_ids,
                                sample_size=None):

        if sample_size is not None:
            pre_ids = np.random.choice(pre_ids, sample_size)
            post_ids = np.random.choice(post_ids, sample_size)
        num_conn = len(tuple(connectome.iter_connections(
            pre=pre_ids, post=post_ids)))
        num_pairs = pre_ids.shape[0] * post_ids.shape[0]
        return num_conn / num_pairs

    @terminology.use(
        terminology.cell.presynaptic,
        terminology.cell.postsynaptic)
    def synapses_per_connection(self, sample_size=50, **parameters):
        """
        get the number of synapses per connection between two groups of cells

        Arguments:
            {parameters}
            sample_size: how many cells to sample from each group
                         actual number of pairs sampled will be this squared

        Returns:
            float or list of floats: number of synapses per connection
        """
        return self._sample_connectome(self._synapses_per_connection,
                                       sample_size, **parameters)

    def _synapses_per_connection(self, connectome, pre_ids, post_ids,
                                 sample_size=None):
        """
        get the synapses per connection for each connection between
        the cells identified by pre_ids and post_ids
        """
        if sample_size is not None:
            pre_ids = np.random.choice(pre_ids, sample_size)
            post_ids = np.random.choice(post_ids, sample_size)
        return np.mean([conn[2] for conn in connectome.iter_connections(
            pre=pre_ids, post=post_ids, return_synapse_count=True)])

    @terminology.use(
        terminology.cell.presynaptic,
        terminology.cell.postsynaptic)
    def pathway_synapses(self, sample_size=None, **parameters):
        """
        get the total number of synapses between two groups of cells

        Arguments:
            {parameters}
            sample_size: int, number of presynaptic cells to sample
        Returns:
            number of synapses:: int
            if sample_size is None this is precisely the number of synapses
            else, it is an estimate based on the mean number in the sample
            multiplied by the total number of cells of the postsynaptic type
        """
        pre_ids = self.get_cells(
            **parameters[terminology.cell.presynaptic]).index.values
        post_ids = self.get_cells(
            **parameters[terminology.cell.postsynaptic]).index.values

        if sample_size is not None:
            # TODO: seeds?
            all_post_ids = post_ids
            post_ids = np.random.choice(post_ids, sample_size)

        nsynapses = len(
            self.get_connectome(**parameters)
            .pathway_synapses(pre=pre_ids, post=post_ids))

        if sample_size is not None:
            nsynapses = len(all_post_ids) * nsynapses / sample_size

        return nsynapses

    @terminology.use(
        terminology.cell.presynaptic,
        terminology.cell.postsynaptic)
    def divergence(self, sample_size=50, **parameters):
        """
        get the divergence from presynaptic group to postsynaptic group
        Arguments:
            {parameters}
            sample_size: number of cells in presynaptic group to sample
        """
        return _flatten(self._sample_connectome(
            self._divergence,  sample_size=sample_size,
            **parameters))

    def _divergence(self, connectome, pre_ids, post_ids, sample_size):
        # assume by synapse for now
        return connectome.stats.sample_divergence(
            pre_ids, post_ids, by='syn', sample=sample_size)

    # TODO: get all data from iter_connections, cache results?
    @terminology.use(
        terminology.cell.presynaptic,
        terminology.cell.postsynaptic)
    def _sample_connectome(self, method, sample_size, **parameters):
        """
        sample pre- and post- synaptic groups and apply method to them

        Arguments:
            method: method to use on the samples of cells to measure a property
                    of the connectome. Must take arguments:
                         connectome, pre_gids, post_gids, sample_size
            sample size: the number of cells/connections in the sample
                         (whether cells or connections depends on their
                          measurement)
            {parameters}
        """
        connectome =\
            self.get_connectome(**parameters)
        pre_cells =\
            self.get_cells(**parameters[terminology.cell.presynaptic])\
                .index.values
        post_cells =\
            self.get_cells(**parameters[terminology.cell.postsynaptic])\
                .index.values
        total_pairs =\
            pre_cells.shape[0] * post_cells.shape[0]
        if total_pairs == 0:
            return np.nan
        return method(connectome, pre_cells, post_cells, sample_size)

    # TODO: should this be internal?
    @terminology.use(
        terminology.circuit.region,
        terminology.circuit.layer,
        terminology.circuit.mesocolumn,
        terminology.circuit.hypercolumn,
        terminology.circuit.height,
        terminology.circuit.depth,
        terminology.cell.mtype,
        terminology.cell.morphology_subclass,
        terminology.cell.synapse_class,
        terminology.cell.morphology_class)
    def get_cells(self, properties=None, **parameters):
        """
        get cells satisfying parameters 'parameters'

        Arguments:
            {parameters}
            properties: a tuple of bluepy cell properties

        Returns:
            DataFrame of cell properties
        """
        cells = self._circuit.cells.get(
            self._translate_parameters_cells(parameters),
            properties=properties)

        def cells_positions(cells):
            return cells[[bp.Cell.X, bp.Cell.Y, bp.Cell.Z]].values

        if terminology.circuit.height in parameters:
            height_vd =\
                self.circuit_atlas.voxeldata(
                    self.circuit_atlas.get_mask(**{
                        terminology.circuit.height: parameters[
                            terminology.circuit.height]}))
            cells =\
                cells[height_vd.lookup(cells_positions(cells))]
        if terminology.circuit.depth in parameters:
            depth_vd =\
                self.circuit_atlas.voxeldata(
                    self.circuit_atlas.get_mask(**{
                        terminology.circuit.depth: parameters[
                            terminology.circuit.depth]}))
            cells =\
                cells[depth_vd.lookup(cells_positions(cells))]

        return cells

    @terminology.use(
        terminology.cell.presynaptic,
        terminology.cell.postsynaptic)
    def get_connectome(self, **parameters):
        # TODO: make dummy connectome that selects chunks for hemispheres,
        #       and forwards operations seperately to the two before pooling
        #       the result.
        self._circuit.connectome.stats = self._circuit.stats
        return self._circuit.connectome

    def _mtype_parameters(self, mtype_name, properties):
        """
        translate a raw mtype name (generally <layer>_<mtype>) to a
        parameter dict (e.g. {LAYER: <layer>, MTYPE: <mtype>})

        Arguments:
            mtype_name: string, raw mtype name as in the circuit

        Returns:
            mtype_parameters: a dict of measurement parameters
                             representing this mtyoe
        """
        props = {}
        if terminology.circuit.layer in properties:
            layer = mtype_name.split("_")[0]
            if layer == "L23":
                layer = ["L2", "L3"]
            props[terminology.circuit.layer] = layer
        if terminology.cell.mtype in properties:
            props[terminology.cell.mtype] = mtype_name
        if terminology.cell.morphology_subclass in properties:
            props[terminology.cell.morphology_subclass] =\
                "_".join(mtype_name.split("_")[1:])
        if terminology.cell.synapse_class in properties:
            props[terminology.cell.synapse_class] =\
                list(self._circuit.cells.get(
                    {bp.Cell.MTYPE: mtype_name},
                    properties=[bp.Cell.SYNAPSE_CLASS])[
                        bp.Cell.SYNAPSE_CLASS].unique())
        return props

    def depths(self, **parameters):
        return self.circuit_atlas.depths(**parameters)

    def heights(self, **parameters):
        return self.circuit_atlas.heights(**parameters)

    # TODO: support lists for each param
    # TODO: kwargs and use?
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
            elif key == terminology.circuit.layer:
                self._layerTranslator.translate(cell_properties, value)
            elif key == terminology.cell.morphology_subclass:
                if terminology.cell.mtype not in parameters:
                    # TODO: test case for this
                    self._mscTranslator.translate(cell_properties, value)
            elif key == terminology.cell.mtype:
                cell_properties[bp.Cell.MTYPE] = value
            elif key == terminology.cell.synapse_class:
                cell_properties[bp.Cell.SYNAPSE_CLASS] = value
            elif key == terminology.cell.morphology_class:
                cell_properties[bp.Cell.MORPH_CLASS] = value
            elif key == terminology.circuit.mesocolumn:
                self._columnTranslator.translate(cell_properties, value)
            elif key == terminology.circuit.region:
                self._regionTranslator.translate(cell_properties, value)
        return cell_properties

"""Define a mock circuit to test and develop code with."""
import numpy as np
import pandas as pd
from bluepy.v2.enums\
    import Cell
from dmt.vtk.utils.logging\
    import Logger
from dmt.vtk.utils\
    import collections
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.utils.descriptor\
    import Field\
    ,      WithFCA
from neuro_dmt.models.bluebrain.circuit.mock.synapse\
    import MockSynapse

logger=\
    Logger(
        __file__,
        level=Logger.level.DEBUG)

cell_properties=[
    Cell.ID,
    Cell.LAYER,
    Cell.MTYPE,
    Cell.MORPHOLOGY,
    Cell.MORPH_CLASS,
    Cell.ME_COMBO,
    Cell.REGION,
    Cell.X,
    Cell.Y,
    Cell.Z,
    Cell.SYNAPSE_CLASS]


class MockCells(
        WithFCA):
    """Mock of Circuit Cells"""

    number_cells=\
        Field(
            __name__ = "number_cells",
            __type__ = int,
            __doc__ = "Number of cells in the circuit")
    layers=\
        Field(
            __name__ = "layers",
            __type__ = list,
            __default__ = list(range(7)),
            __doc__ = "layers in the circuit.")
    dimensions=\
        Field(
            __name__ = "dimensions",
            __type__ = np.ndarray,
            __default__ = 100 * np.ones(3),
            __doc__ = """Dimensions of the cuboidal mock circuit.""")
    etypes=\
        Field(
            __name__ = "etypes",
            __type__ = list,
            __default__ = ["etype_{}".format(i) for i in range(12)],
            __doc__ = """List of cell electrical types. We should replace the
            default list by a biological looking one.""")
    mtype_classes=\
        Field(
            __name__ = "mtype_classes",
            __type__ = list,
            __default__ = ["PC", "MC", "BTC", "TPC"],
            __doc__ = "List of biological sounding mtype suffixes.")
    regions=\
        Field(
            __name__ = "regions",
            __type__ = list,
            __default__ = ["Region{}".format(r) for r in range(7)],
            __doc__ = """Some region names. We should replace the default by
            atlas regions.""")

    def __init__(self,
        *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)
        self._cells = None

    @property
    def all_gids(self):
        """..."""
        return list(range(self.number_cells))

    def _random_layer(self):
        """..."""
        return np.random.choice(
            self.layers)

    def _random_morphclass(self,
            mtype):
        """..."""
        return\
            np.random.choice(
                ["PYR", "INT"])

    def _random_synapse_class(self,
            mtype):
        """..."""
        return\
            np.random.choice(
                ["EXC", "INH"])

    def _random_morphology(self,
            mtype):
        """..."""
        return "mtype_{}_morphology_{}".format(
            mtype,
            np.random.choice(range(1000)))
            
    def _random_mtype(self,
            layer):
        """..."""
        return\
            "L{}".format(
                np.random.choice(
                    self.mtype_classes))
    
    def _random_etype(self):
        """..."""
        return\
            np.random.choice(
                self.etypes)

    def _random_me_combo(self,
            mtype,
            etype):
        """mtype, etype combo"""
        return "{}_{}".format(mtype, etype)
            
    def _random_region(self):
        """..."""
        return\
            np.random.choice(
                self.regions)

    def _random_X(self):
        """..."""
        return\
            np.random.uniform(
                0., self.dimensions[0])

    def _random_Y(self):
        """..."""
        return\
            np.random.uniform(
                0., self.dimensions[1])

    def _random_Z(self):
        """..."""
        return\
            np.random.uniform(
                0., self.dimensions[2])

    def _get_cell(self,
            gid):
        """Generate a _random pandas Series describing a bluepy cell."""
        layer=\
            self._random_layer()
        mtype=\
            self._random_mtype(layer)
        etype=\
            self._random_etype()
        return\
            pd.Series({
                Cell.ID: gid,
                Cell.LAYER: layer,
                Cell.MTYPE: mtype,
                Cell.MORPHOLOGY: self._random_morphology(mtype),
                Cell.MORPH_CLASS: self._random_morphclass(mtype),
                Cell.ME_COMBO: self._random_me_combo(mtype, etype),
                Cell.REGION: self._random_region(),
                Cell.X: self._random_X(),
                Cell.Y: self._random_Y(),
                Cell.Z: self._random_Z(),
                Cell.SYNAPSE_CLASS: self._random_synapse_class(mtype)})

    def _populate(self):
        """Populate with _random cells."""
        self._cells=\
            pd.DataFrame([
                self._get_cell(gid)
                for gid in self.all_gids])

    def get(self,
            cell_group={},
            properties=cell_properties):
        """Cell group will be disregarded,
        in the first implementation."""

        if self._cells is None:
            self._populate()

        cells =  self._cells[properties]
        for prop, value in cell_group.items():
            if prop not in properties:
                continue
            if collections.check(value):
                cells= cells[cells[prop] in value]
            else:
                cells= cells[cells[prop] == value]
        return cells

    def positions(self,
            cell_gids):
        """_random positions"""
        if not collections.check(cell_gids):
            cell_gids = [cell_gids]
        return\
            self._cells.loc[
                cell_gids][
                    [Cell.X, Cell.Y, Cell.Z]]


class MockConnectome(
        WithFCA):
    """A _random connectome, wired up as a directed ER graph"""
    circuit_cells=\
        Field(
            __name__ = "circuit_cells",
            __type__ = pd.DataFrame,
            __doc__ = """Cells to be connected by this connectome.""")
    mean_connectivity=\
        Field(
            __name__ = "mean_connectivity",
            __type__ = int,
            __doc__ = """Mean number of connections of a cell.""",
            __default__ = 100)
    max_number_connection_synapses=\
        Field(
            __name__ = "max_number_connection_synapses",
            __type__ = int,
            __doc__  = "Maximum number of synapses in a connection.",
            __default__ = 6)


    def __init__(self,
            *args, **kwargs):
        """..."""
        self._efferent_gids= []
        self._afferent_gids= []

        self._pair_synapses= []
        self._afferent_synapses = []
        self._efferent_synapses = []

        super().__init__(
            *args, **kwargs)

        self.number_cells=\
            self.circuit_cells.shape[0]

    def _check_gid(self,
            gid):
        if gid >= self.number_cells:
            raise ValueError(
                "Cell GID {} not in index".format(gid),
                "Cell GID must be  less than {}".format(self.number_cells))

    @property
    def all_gids(self):
        """..."""
        return range(self.number_cells)

    def _connect(self):
        """Wire up the connectome.
        """
        self._efferent_gids=[
            list(np.random.choice(
                self.all_gids,
                self._get_number_neighbors(),
                replace=False))
            for _ in self.all_gids] 

        self._afferent_gids=\
            [[] for _ in self.all_gids]

        for pre_gid in self.all_gids:
            for post_gid in self._efferent_gids[pre_gid]:
                self._afferent_gids[post_gid]\
                    .append(pre_gid)
            
        def __random_connection_synapses(
                pre_gid,
                post_gid):
            """..."""
            pre_cell=\
                self.circuit_cells.loc[pre_gid]
            assert\
                pre_cell.gid == pre_gid
            post_cell=\
                self.circuit_cells.loc[post_gid]
            assert\
                post_cell.gid == post_gid
            return[
                MockSynapse(pre_cell, post_cell, index)
                for index in range(
                        np.random.choice(
                            range(
                                self.max_number_connection_synapses)))]
        
        self._pair_synapses=[
            {post_gid: __random_connection_synapses(pre_gid, post_gid)
             for post_gid in self._efferent_gids[pre_gid]}
            for pre_gid in self.all_gids]

        self._efferent_synapses=[
            synapse for pre_gid in self.all_gids
            for post_gid in self._efferent_gids[pre_gid]
            for synapse in self._pair_synapses[pre_gid][post_gid]]

        self._afferent_synapses=[
            synapse for post_gid in self.all_gids
            for pre_gid in self._afferent_gids[post_gid]
            for synapse in self._pair_synapses[pre_gid][post_gid]]

    def efferent_gids(self,
            pre_gid):
        """..."""
        self._check_gid(pre_gid)
        if not self._efferent_gids:
            self._connect()

        return self._efferent_gids[pre_gid]

    def afferent_gids(self,
            post_gid):
        """..."""
        self._check_gid(post_gid)

        if not self._afferent_gids:
            self._connect()

        return self._afferent_gids[post_gid]

    def pair_synapses(self,
            pre_gid,
            post_gid):
        """..."""
        self._check_gid(pre_gid)
        self._check_gid(post_gid)

        if not self._pair_synapses:
            self._connect()

        try:
            return self._pair_synapses[pre_gid][post_gid]
        except KeyError:
            return 0

    def efferent_synapses(self,
            pre_gid):
        """..."""
        self._check_gid(pre_gid)
        if not self._efferent_synapses:
            self._connect()

        return self._efferent_synapses[pre_gid]

    def afferent_synapses(self,
            post_gid):
        """..."""
        self._check_gid(post_gid)
        if not self._afferent_synapses:
            self._connect()

        return self._afferent_gids[post_gid]


    @property
    def spatial_index(self):
        """..."""
        raise NotImplementedError()

    def _get_number_neighbors(self):
        """..."""
        N = float(self.mean_connectivity)
        dN = np.sqrt(N)
        return int(
            np.random.uniform(
                N - dN, N + dN))


class MockStats:
    "mock circuit stats"

    def bouton_density(self,
            gid):
        """..."""
        return np.random.uniform(0., 1.)


class MockCircuit(
        WithFCA):
    """A mock of a bluepy circuit."""

    number_cells=\
        Field(
            __name__ = "number_cells",
            __type__ = int,
            __doc__ = "Number of cells in the circuit",
            __default__ = 200)

    def __init__(self,
            circuit_config,
            *args, **kwargs):
        """Nothing to initialize in a mock circuit."""

        super().__init__(
            *args, **kwargs)

        self._cells=\
            MockCells(
                number_cells = self.number_cells,
                *args, **kwargs)
        self._conn=\
            MockConnectome(
                circuit_cells=self._cells.get(),
                *args, **kwargs)

    @property
    def cells(self):
        """..."""
        return self._cells

    @property
    def connectome(self):
        """..."""
        return self._conn

    @property
    def morph(self):
        """..."""
        raise NotImplementedError()

    @property
    def stats(self):
        """..."""
        return MockStats()

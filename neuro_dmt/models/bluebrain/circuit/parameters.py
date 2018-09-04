"""Parameters that should be valid for all Blue Brain Circuit Models."""

import numpy as np
from bluepy.v2.enums import Cell
from dmt.vtk.utils.collections import *
from dmt.vtk.measurement.parameters import Parameter, GroupParameter
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper


class Mtype(GroupParameter):
    """Mtype groups cell gids."""
    label = "mtype"
    value_type = str
    grouped_variable = Record(__type__ = int, name="cell_gid")
                              

    def __init__(self, circuit, *args, **kwargs):
        """..."""
        self._circuit = circuit
        self._helper  = BlueBrainModelHelper(circuit=circuit)
        self._values = None #initialized when 'self.values' first called
        self._order_dict  = None #initialized when 'self.order' first called
        self._mtype_groups = None #cells GIDs for a given mtype
        super(Mtype, self).__init__(*args, **kwargs)

    @property
    def mtype_groups(self):
        """..."""
        if self._mtype_groups is None:
            self._mtype_groups = self._helper.cell_mtypes().groupby(Cell.MTYPE)
        return self._mtype_groups

    @property
    def values(self):
        """What mtypes may cells have in a circuit?
        Since this computation can be expensive, we will cache the results."""
        if not self._values:
            self._values = set(self.mtype_groups.keys())
        return self._values

    def order(self, mtype):
        """We need the values to order them."""
        if not self._order_dict:
            N = len(self.values)
            self._order_dict\
                = dict(zip(sorted(list(self.values)), range(1, N + 1)))
        return self._order_dict[mtype]

    def is_valid(self, value):
        """..."""
        return True

    def repr(self, value):
        """..."""
        return value

    def cell_gids(self, mtype):
        """Cell gids for a given mtype."""
        return self.mtype_groups[mtype]

    def grouped_values(self, mtype, *args, **kwargs):
        """Generator of all the values of the grouped variable"""
        target = kwargs.get("target", None)
        target_cells = self._helper.target_cells(target)

        while True:
            try:
                g = np.random.choice(self.cell_gids(mtype))
            except:
                raise ValueError("No cells of mtype {} in the circuit."\
                                 .format(mtype))
            if g in target_cells:
                yield g
            else:
                continue

    def __call__(self, *args, **kwargs):
        """Sample cell gids for each mtype in circuit 'self._circuit'.

        Return
        ------------------------------------------------------------------------
        Generator[(mtype, gid)]
        """
        n = kwargs.get("sample_size", 20)

        return ((mtype, g) for mtype in self.values
                for g in take(n, self.grouped_values(mtype, *args, **kwargs)))
                

class PreMtype(Mtype):
    """PreMtype is the same as Mtype except some labels..."""
    label = "pre_mtype"
    grouped_variable = Record(__type__=int, name="pre_gid")


class PostMtype(Mtype):
    """PostMtype is the same as Mtype except some labels..."""
    label = "post_mtype"
    grouped_variable = Record(__type__=int, name="post_gid")


class Pathway(GroupParameter):
    """Pathway groups mtype-->mtype connections."""

    label = "pathway"
    value_type = tuple #(pre_mtype :: str, post_mtype :: str)
    grouped_variable = Record(
        __type__=tuple, #(pre_gid :: int, post_gid :: int)
        name="connection"
    )
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        self._circuit = circuit
        self._helper  = BlueBrainModelHelper(circuit=circuit)
        self._mtypes = None
        self._values = None #initialized when first needed
        self._order_dict = None #initialized when first needed
        self._connections = None #this will be a dictionary -- to cache results
        super(Pathway, self).__init__(*args, **kwargs)

    @property
    def mtypes(self):
        """..."""
        if self._mtypes is None:
            self._mtypes = self._helper.cell_mtypes()
        return self._mtypes

    @property
    def values(self):
        """All Pathway values (pre_mtype, post_mtype), that are possible."""
        if not self._values:
            self._values = set([(pre, post) for pre in self.mtypes.values
                               for post in self.mtypes.values])
        return self._values

    def order(self, connection):
        """An order on Pathway values."""
        if not self._order_dict:
            N = len(self.values)
            self._order_dict\
                = dict(zip(sorted(self.values), range(1, N + 1)))
        return self._order_dict[connection]

    def is_valid(self, value):
        """Implement this."""
        return True

    def repr(self, value):
        return "{}-->{}".format(value[0], value[1])

    def connections(self, pre_mtype, post_mtype):
        """Get connections for pathway pre_mtype --> post_mtype."""
        def __efferent(pre_gid):
            """..."""
            conn = self._circuit.connectome
            return (post_gid for post_gid in conn.efferent_gids(pre_gid)
                    if self.mtypes.iloc[post_gid] == post_mtype)
                   
        if not self._connections:
            self._connections = {}
        if pre_mtype not in self._connections:
            self._connections[pre_mtype] = {}
        if post_mtype not in self._connections[pre_mtype]:
            pre_gids = self.mtypes.index[self.mtypes[Cell.MTYPE] == pre_mtype]

            self._connections[pre_mtype][post_mtype]\
                = [(pre, post) for pre in pre_gids for post in __efferent(pre)]

        return self._connections[pre_mtype][post_mtype]


    def grouped_values(self, pathway, *args, **kwargs):
        """..."""
        target = kwargs.get("target", None)
        target_cells = self._helper.target_cells(target)

        pre_mtype = pathway[0]
        post_mtype = pathway[1]

        raise NotImplementedError("Complete this!")
        

    def __call__(self, **kwargs):
        """Sample cell gid pairs for each pathway in circuit 'self._circuit'.

        Return
        ------------------------------------------------------------------------
        Iterable[ Tuple[ Tuple[pre_mtype :: str, post_mtype :: str],
        ~                Tuple[pre_gid   :: int, post_gid   :: int]] ]
        """

        sample_size = kwargs.get("sample_size", 20)

        cs = [(pre, post) for pre,post in self.connections(pre_mtype, post_mtype)
              if pre in target_cells and post in target_cells]

        return ((p, c) for p in self.values
                for c in np.random.choice(cs, n, replace=False))

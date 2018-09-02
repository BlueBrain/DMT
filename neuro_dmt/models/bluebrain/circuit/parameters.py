"""Parameters that should be valid for all Blue Brain Circuit Models."""

import numpy as np
from bluepy.v2.enums import Cell
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameters import GroupParameter
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
        super(Mtype, self).__init__(*args, **kwargs)

    @property
    def cell_mtypes(self):
        if not self._cell_mtypes:
            self._cell_mtypes = self._helper.cell_mtypes
        return self._cell_mtypes

    @property
    def values(self):
        """What mtypes may cells have in a circuit?
        Since this computation can be expensive, we will cache the results."""
        if not self._values:
            self._values = set(self._helper.cell_mtypes()[Cell.MTYPE]) 
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

    def __call__(self, **kwargs):
        """Sample cel gids for this Mtype in circuit 'circuit'.

        Return
        ------------------------------------------------------------------------
        Generator[(mtype, gid)]
        """
        target = kwargs.get("target", None)
        sample_size = kwargs.get("sample_size", 20)

        mtypes = self._helper.cell_mtypes(target=target)

        def __get_gids(mtype):
            """..."""
            mgids = np.array(mtypes[mtypes[Cell.MTYPE] == mtype].index)
            return (np.random.choice(mgids, sample_size, replace=False)
                    if sample_size < len(mgids) else mgids)

        return ((mtype, g) for mtype in self.values for g in __get_gids(mtype))
                

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
    value_type = tuple #(str, str)
    grouped_variable = Record(__type__ = tuple, #(int, int)
                              name = "connection")
    





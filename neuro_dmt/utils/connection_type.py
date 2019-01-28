"""Connection between two cell types."""
from abc import ABC, abstractmethod
from functools import reduce
from dmt.vtk.utils import collections
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.collections.emuset import emuset
from dmt.vtk.utils.descriptor import Field, WithFCA
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from neuro_dmt.utils.cell_type import CellProperty, CellType

class ConnectionType(
        WithFCA):
    """Defines a pre-cell==>post-cell connection type. It can be used to
    extract properties of this connection."""
    pre_cell_type=\
        Field(
            __name__="pre_cell_type",
            __type__=CellType,
            __default__=CellType.Any,
            __doc__="""Specify the type of the neuronal cell
            at the pre-synatic end.""")
    post_cell_type=\
        Field(
            __name__="post_cell_type",
            __type__=CellType,
            __default__=CellType.Any,
            __doc__="""Specify the type of the neuronal cell
            at the post-synatic end.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

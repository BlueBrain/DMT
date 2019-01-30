"""Parameters that should be valid for all Blue Brain Circuit Models."""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from bluepy.v2.circuit\
    import Circuit
from bluepy.v2.enums\
    import Cell
from bluepy.geometry.roi\
    import ROI
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.utils.collections\
    import *
from dmt.vtk.measurement.parameter\
    import Parameter
from dmt.vtk.measurement.parameter.finite\
    import FiniteValuedParameter
from neuro_dmt.measurement.parameter\
    import BrainCircuitMeasurementParameter
from dmt.vtk.measurement.parameter.random\
    import ConditionedRandomVariate
from dmt.vtk.utils.logging\
    import Logger, with_logging
from dmt.vtk.utils.descriptor\
    import Field, WithFCA
from neuro_dmt.models.bluebrain.circuit\
    import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry\
    import \
    Cuboid,  random_location
from neuro_dmt.measurement.parameter\
    import BrainCircuitSpatialParameter, Column

class CircuitDefined:
    """Mixin with objects whose 'values' depend on the circuit.
    For example mtypes depend on the circuit."""
    circuit=\
        Field(
            __name__="circuit",
            __type__=Circuit,
            __doc__="""Circuit instance from which this parameter values
            should be read.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

class Mtype(
        BrainCircuitMeasurementParameter):
    """mtypes in a circuit."""

    @classmethod
    def validated_mtypes(cls,
            circuit,
            mtypes):
        """.."""
        if len(mtypes) == 0:
            return list(circuit.cells.mtypes)
        for mtype in mtypes:
            if not mtype in circuit.cells.mtypes:
                cls.logger.alert(
                    cls.logger.get_source_info(),
                    "mtype value {} not in the circuit {}"\
                    .format(mtype, circuit))
        return\
            list(circuit\
                 .cells\
                 .mtypes\
                 .intersection(
                     mtypes))

    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        kwargs["values"]=\
            self.validated_mtypes(
                circuit,
                kwargs.get("values", []))
        if "value_type" not in kwargs:
            kwargs["value_type"] = str
        super().__init__(
            label=Cell.MTYPE,
            *args, **kwargs)


class MtypePathway(
        BrainCircuitMeasurementParameter):
    """A pathway is pre-cell-type to post-cell-type.
    In our first implementation we will use mtype to define the cell types.
    We can also implement a general 'Pathway' that would take an arbitrary type
    to group cells into pre and post cells."""

    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        pre_mtypes=\
            Mtype.validated_mtypes(
                circuit,
                kwargs.get("pre_mtypes", []))
        post_mtypes=\
            Mtype.validated_mtypes(
                circuit,
                kwargs.get("post_mtypes", []))
        super().__init__(
            label="pathway",
            value_type=tuple,
            values=[(pre, post)
                    for pre in pre_mtypes
                    for post in post_mtypes])


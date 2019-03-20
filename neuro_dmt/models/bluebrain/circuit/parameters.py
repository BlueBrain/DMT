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
    import Logger\
    ,      with_logging
from dmt.vtk.utils.descriptor\
    import Field\
    ,      WithFCA
from neuro_dmt.models.bluebrain.circuit\
    import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry\
    import  Cuboid\
    ,      random_location
from neuro_dmt.measurement.parameter\
    import BrainCircuitSpatialParameter\
    ,      BrainCircuitConnectomeParameter

class CircuitModelDependent:
    """Mixin with objects whose 'values' depend on the circuit.
    For example mtypes depend on the circuit.
    """
    circuit=\
        Field.Optional(
            __name__="circuit",
            __type__=Circuit,
            __doc__="""Circuit instance from which this parameter values
            should be read. We set this Field to optional, expecting the user
            to invoke the 'for_circuit' method provided below.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

    def for_circuit(self,
            circuit):
        """..."""
        return self.__class__(
            circuit=circuit,
            label=self.label,
            values=self.values)


class Mtype(
        CircuitModelDependent,
        BrainCircuitConnectomeParameter):
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
            sorted(list(
                circuit\
                .cells\
                .mtypes\
                .intersection(
                    mtypes)))

    def __init__(self,
            circuit=None,
            values=[],
            label=Cell.MTYPE,
            *args, **kwargs):
        """..."""
        if circuit is not None:
            values=\
                self.validated_mtypes(
                    circuit,
                    values)
        super().__init__(
            circuit=circuit,
            label=label,
            value_type=str,
            values=values,
            *args, **kwargs)


class MtypePathway(
        CircuitModelDependent,
        BrainCircuitConnectomeParameter):
    """A pathway is pre-cell-type to post-cell-type.
    In our first implementation we will use mtype to define the cell types.
    We can also implement a general 'Pathway' that would take an arbitrary type
    to group cells into pre and post cells."""

    def __init__(self,
            circuit=None,
            *args, **kwargs):
        """..."""
        pre_mtypes=\
            kwargs.get(
                "pre_mtypes",
                [])
        post_mtypes=\
            kwargs.get(
                "post_mtypes",
                [])
        if circuit is not None:
            pre_mtypes=\
                Mtype.validated_mtypes(
                    circuit,
                    pre_mtypes)
            post_mtypes=\
                Mtype.validated_mtypes(
                    circuit,
                    post_mtypes)
        values=[
            (pre, post)
            for pre in pre_mtypes
            for post in post_mtypes]

        super().__init__(
            label="mtype_pathway",
            value_type=tuple,
            values=values)

    @classmethod
    def for_circuit(cls,
            circuit):
        """MtypePathway instance for a given circuit."""
        return cls(circuit=circuit)

    def get_values(self,
            circuit):
        """Get values for the provided circuit."""
        pre_mtypes=\
            PreMtype.validated_mtypes(
                circuit,
                [pre_mtype for pre_mtype, _ in self.values]) 
        post_mtypes=\
            PostMtype.validated_mtypes(
                circuit,
                [post_mtype for _, post_mtype in self.values])
        return[
            (pre, post)
            for pre in pre_mtypes
            for post in post_mtypes]

    def filled(self,
            dataframe,
            sorted=True,
            ascending=True,
            with_index_renamed=True):
        """Override the method in superclass FiniteValuedParameter,
        to change the dataframe's index."""
        dataframe=\
            super().filled(
                dataframe,
                sorted=sorted,
                ascending=ascending,
                with_index_renamed=with_index_renamed)
        dataframe.index=\
            pd.MultiIndex.from_tuples(
                dataframe.index.values,
                names=["pre_mtype", "post_mtype"])
        return dataframe

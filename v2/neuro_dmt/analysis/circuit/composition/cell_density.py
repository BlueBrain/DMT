"""
Analyze cell density of a brain circuit.
"""

from abc import ABC, abstractmethod
import pandas
import numpy
from dmt.model.interface import Interface
from dmt.tk.field import WithFields, Field, lazyproperty
from dmt.tk.phenomenon import Phenomenon
from . import CompositionAnalysis

class CellDensityAnalysis(ABC):
    """
    Analysis of a circuit's cell density.

    `class CellDensityAnalysis` is intended to be used as a mixin.
    However there are methods that the must be satisfied by the class
    that mixes `CellDensityAnalysis` into its behavior. These methods
    are marked as abstractmethods.
    """

    phenomenon = Field(
        """
        An object that provide information about the circuit phenomenon 
        analyzed.
        """,
        __default_value__ = Phenomenon(
            name="Cell Density",
            description="""Number of cells in a unit volume,
            measured in the physical space of the brain.""",
            group="Circuit Composition"))

    measurement_parameters = Field(
        """
        The class mixing in `class CellDensityAnalysis` must provide
        the parameters with which to make this measurement.

        These parameters should be packaged as pandas.MultiIndex or a
        pandas.Index.

        Type
        ---------------
        Either a pandas.Index, or a pandas.MultiIndex
        pandas.Index: when there is only parameter to measure cell density
        pandas.MultiIndex: when there are more than parameter to measure
        """,
        __type__=(pandas.Index, pandas.MultiIndex))

    class AdapterInterface(
            Interface):
        """
        All methods listed under `class AdapterInterface` must be implemented
        by an adapter of this `Interface`.
        """
        def get_label(self
                circuit_model):
            """
            Get a label for a circuit model.

            Arguments:
            `circuit_model`: model of a brain circuit.
            """
            raise NotImplementedError

        def get_cell_density(self,
                circuit_model,
                mtype=None,
                etype=None,
                region=None,
                layer=None):
            """
            Get number of cells in a unit volume in the circuit represented by
            `circuit_model`. This method must be defined for the model adapter
            object that will adapt a circuit model to the requirements of this
            analysis.

            Implementation Guideline
            ------------------------
            The cell density must be measured for the values of parameters
            passed as keyword arguments. For example,

            `model_adapter.get_cell_density(`
            `   mtype=L23_MC,`
            `   region='SSp',`
            `   layer=1)`

            should return the density of L23_MC cells in layer 1 of the primary
            Somatosensory cortex.

            The implementation may compute:
            1. the mean density sampled over the space implied by the
            ~  parameters passed
            2. mean density in a randomly selected volume in the confines
            ~  of the physical space implied by the parameters passed.

            Arguments
            ---------------------
            `circuit_model`: model of a brain circuit
            `**spatial_parameters`: key value 

            Returns
            ---------------------
            a float value
            """
            raise NotImplementedError

        pass

    def get_measurement(self,
            circuit_model,
            sample_size=20,
            *args, **kwargs):
        """
        Required method of an `Analysis`.

        Returns
        ----------------
        A pandas data-frame with  measurement parameters in its index.
        """
        return pandas\
            .DataFrame(
                [self.adapter.get_cell_density(**parameters)
                 for parameters in self.measurement_parameters]
                index=self.measurement_parameters)

"""Test if the cell density of a model circuit is close to that obtained
from an experiment."""

from abc import abstractmethod
from dmt.validation import ValidationTestCase
from dmt.model import ModelAdapter

class CanMeasureCellDensity(ModelAdapter):
    """A ModelAdapter is a base class to define a simple model like object that 
    measures specific phenomena."""

    @classmethod
    @abstractmethod
    def get_layer_cell_densities(self):
        """Get cell densities by layer.
        Users who want to include CellDensity test in their Validation suite
        should specify the details in their concrete implementation of this
        ModelAdapter """
        pass


class CellDensity(ValidationTestCase):
    """Test if the cell density of a model circuit matches that obtained
    from an experiment.

    Notes
    -----
    We include all the methods needed for testing cell density here.
    In our first attempt, we will use this validation test as a learning ground
    to understand how to structure our validation framework dmt, as well as
    how to structure validation of a neuronal model circuit."""

    def __init__(self, real_system):
        """
        Parameters
        -----------
        real_system :: RealMeasurableSystem

        Notes
        -----
        A validation is tied to a RealMeasurableSystem. Our code will require
        a RealMeasurableSystem to behave exactly like the ModelMeasurableSystem
        it will validate.
        """
        self._real_system = real_system
        self._real_observation = self.generate_observation(real_system)

    @classmethod
    def generate_observation(cls, measurable_system):
        """
        Parameters
        ----------
        @measurable_system :: MeasurableSystem

        Desired Behavior
        ----------------
        ???

        Improvements
        ------------
        For now, we use a naked assert, which on failure
        will throw an ugly looking exception. We want a more descriptive
        explanation.
        """
        #assert isinstance(measurable_system, CanMeasureCellDensity)
        try:
            return measurable_system.get_layer_cell_densities()
        except:
            raise RequiredMeasurementException(
                """To use this cell density test case in a validation,
                your model adapter must have provide an implementation of
                get_layer_cell_densities"""
            )


    @property
    def real_system(self) :
        """@attr :: RealMeasurableSystem"""
        return self._real_system

    @property
    def real_observation(self):
        """@attr :: Measurement"""
        return self._real_observation

    def __call__(self, model_system):
        """call / run this test for a given model_system.

        Parameters
        ----------
        @model_system :: ModelMeasurableSystem

        Notes
        -----
        In our first attempt, we will dump all details of testing cell density
        here, learn some lessons and move common patterns out into base
        classes."""

        model_observation = self.generate_observation(model_system)



        

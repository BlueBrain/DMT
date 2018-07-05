"""We cannot assume that the authors of validation test cases and models will
use identical method names for measuring the model's phenomena. So we have to
code a validation using the interface of a model adapter. This interface will
effectively list all the methods that a concrete implementation of this
model adapter will have to implement."""

from abc import ABC, abstractmethod


class ModelAdapter(ABC):
    """A ModelAdapter adapts a model to an interface."""

    @abstractmethod
    def adapts(self, model):
        """Check if this ModelAdapter has implemented all the required
        methods."""
        pass

    @abstractmethod
    def get_measurement(self, measurable_system):
        """get the measurement.

        Parameters
        ----------
        @measurable_system :: MeasurableSystem

        Return
        -------
        Measurement

        """
        pass

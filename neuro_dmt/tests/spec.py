"""Common specifications for testing."""
from abc import ABC, abstractmethod
import os
import time
import datetime
import numpy as np
from dmt.vtk.utils.descriptor import Field
from neuro_dmt.tests.


class CircuitSpec(ABC):
    """Base class to specify a circuit."""
    def __init__(self, circuit_model, animal,
                 brain_region, brain_sub_region=None):
        """Specify a circuit for testing, along with metadata."""
        self._circuit = circuit_model
        self._animal = animal
        self._brain_region = brain_region
        if brain_sub_region is not None:
            self._brain_sub_region  = brain_sub_region

    @property
    def defines_brain_sub_region(self):
        return hasattr(self, '_brain_sub_region')

    @property
    def description(self):
        """What is this test about?"""
        if not self.defines_brain_sub_region:
            return "Specifies a brain circuit model for {} for the animal."\
                .format(self._brain_region, self._animal)

        return "Specifies a brain circuit model for {} in {} for the animal."\
            .format(self._brain_sub_region, self._brain_region, self._animal)


class TestSpec:
    """Base class to specify a test suite for a Circuit. """
    reference_datasets_uri = Field(
        __name__ = "reference_datasets_dir",
        __type__ = str,
        __doc__  = """Directory path to reference datasets to be used
        for validations in testing."""
    )
    def __init__(self, circuit_spec,
                 reference_datasets_uri,
                 output_parent_dir=".",
                 *args, **kwargs):
        """..."""
        self.circuit_spec = circuit_spec
        self.reference_datasets_uri = reference_datasets_uri
        self.output_parent_dir = output_parent_dir
        super(TestSpec, self).__init__(*args, **kwargs)

    @property
    @abstractmethod
    def reference_datasets(self):
        """Reference datasets can be loaded from the URI
        'reference_datasets_uri'"""
        pass

    def get_output_directory(self):
        """Where should the outputs go?
        This will help you organize your test result outputs by
        brain-region/sub-region/animal/time/..."""
        today = datetime.date.today().strftime("%Y%m%d")
        now = time.localtime()

        def two_figured(x):
            """Convert a number to contain two figures."""
            return ("" if x > 9 else "0") + str(x)

        hour = two_figured(now.tm_hour)
        minute = two_figured(now.tm_min)
        if circuit_spec.defines_brain_sub_region:
            return os.path.join(self.output_parent_dir,
                                circuit_spec._brain_region,
                                circuit_spec._brain_sub_region,
                                circuit_spec._animal,
                                today, hour + minute)
        else:
            return os.path.join(self.output_parent_dir,
                                circuit_spec._brain_region,
                                circuit_spec._animal,
                                today, hour + minute)

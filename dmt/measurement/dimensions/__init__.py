"""A physical quantity is a physical property of a phenomenon, body,
or substance, that can be quantified by measurement. A physical quantity can be
expressed as the combination of a magnitude expressed by a number and a unit.
A physical quantity will have physical dimensions. For example, measurement of
length will provide a quantity with physical dimensions of [L].
We begin by defining PhysicalDimension. PhysicalDimension will not have state.
These will be singleton classes."""

from abc import ABC, abstractmethod

class PhysicalDimension(ABC):
    """Behavior of a physical dimension."""

    @abstractmethod
    @property

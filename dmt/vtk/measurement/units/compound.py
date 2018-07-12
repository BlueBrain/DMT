"""CompoundUnits, like those of velocity"""

from dmt.measurement.units import Unit

class CompoundUnit(Unit):
    """A CompoundUnit is a non-trivial transform of one or more AtomicUnits.
    If you look carefully, for now the only difference between CompoundUnit
    and AtomicUnit is this doc string.

    Development Notes
    -----------------
    We do not need a  standard scale factor for compound units ---
    we should be able to deduce a compount unit's standard scale factor from
    it's Physical Dimension --- it is a simple computation :

    A CompoundUnit's PhysicalDimension ( we can make a code-validation that it
    is in fact a CompoundPhysicalDimension ) will tell us how each composing
    AtomicUnit's standard scaling factor has to be combined with others. Raise
    each composing AtomicUnit's standard scaling factor to its corresponding
    power in the CompoundUnit's PhysicalDimension, and then take a product over
    them. This will require that we have a list of AtomicUnit instances, that
    we can lookup by AtomicPhysicalDimension.
    """

    def conversion_factor(self, alt_unit):
        """Convert this unit to an alternate unit

        Parameters
        ----------
        @alt_units :: the alternate unit to convert to."""

        if self.physical_dimensions != alt._unit.physical_dimensions:
            raise Exception("Incomplete Units {} and {}".format(
                self.physical_dimensions.__repr__(),
                alt_unit.physical_dimensions.__repr__()
            ))

        return self.std_scale / alt_unit.std_scale
                

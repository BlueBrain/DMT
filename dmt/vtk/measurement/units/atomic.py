"""An AtomicUnit is a unit for an AtomicPhysicalDimension."""


from dmt.measurement.units import Unit
from dmt.physical_dimension import AtomicPhysicalDimension

class AtomicUnit(Unit):
    """An atomic unit is a building block for compound units.
    In physics units for length, mass, time, current, and luminosity are
    atomic. To this we can add a unit for currency, and may be one for count
    of things."""

    def conversion_factor(self, alt_unit):
        """Convert this unit to an alternate unit.
            Parameters
            ----------
            @alt_unit :: the alternate unit to convert to"""
        if self.physical_dimensions != alt_unit.physical_dimensions:
            raise Exception(
                "Incompatible Units " +
                self.physical_dimensions.__repr__() + " and " +
                alt_unit.physical_dimensions.__repr__()
            )
        return self.std_scale / alt_unit.std_scale



from dmt.physical_dimension import Length

class LengthUnit(AtomicUnit):
    """Unit of length."""
    standard_unit = "Meter"

Meter = LengthUnit("Meter", "m", Length, 1.0)
Centimeter = LengthUnit("Centimeter", "cm", Length, 1.e-2)
Kilometer = LengthUnit("Kilometer", "km", Length, 1.e3)


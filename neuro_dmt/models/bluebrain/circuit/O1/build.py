"""O1 circuit build"""
from neuro_dmt.models.bluebrain.circuit.build import CircuitBuild
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location


class O1Circuit(CircuitBuild):
    """Specializations of methods for the O1.v6a circuits."""

    def __init__(self, *args, **kwargs):
        super(O1Circuit, self).__init__(*args, **kwargs)

    def random_position(self, brain_region, condition, offset = 50.,
                        *args, **kwargs):
        query = brain_region.cell_query(condition, *args, **kwargs)
        bounds\
            = self._helper\
                  .geometric_bounds(query, target=brain_region.target)
                                    
        if bounds is None:
            return None
        box = Cuboid(bounds.bbox[0] + offset, bounds.bbox[1] - offset)
        return random_location(box)

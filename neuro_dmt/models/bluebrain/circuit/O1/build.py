"""O1 circuit build"""
from dmt.vtk.utils.collections import Record
from neuro_dmt.utils import brain_regions
from neuro_dmt.models.bluebrain.circuit.brain_regions import BrainRegionSpecific
from neuro_dmt.models.bluebrain.circuit.build import CircuitBuild
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location

class Cortical(BrainRegionSpecific):
    """..."""
    brain_region = brain_regions.cortex

    def __init__(self, by=tuple(), target="mc2_Column", *args, **kwargs):
        """..."""
        cell_group_params = by if by else ("layer", "$target")
        super(Cortical, self).__init__(cell_group_params, target=target,
                                       *args, **kwargs)

    def cell_query(self, condition, *args, **kwargs):
        """A dict that can be passed to circuit.cells.get(...).
        Concrete implementation may override """
        return {p: condition.get_value(p) for p in self.cell_group_params}


class Hippocampal(BrainRegionSpecific):
    """..."""
    brain_region = brain_regions.hippocampus

    def __init__(self, by=None, *args, **kwargs):
        """..."""
        cell_group_params = by if by else ("layer",)
        super(Hippocampal, self).__init__(cell_group_params, *args, **kwargs)

    def cell_query(self, condition, *args, **kwargs):
        """A dict that can be passed to circuit.cells.get(...).
        Concrete implementation may override """
        return {p: condition.get_value(p) for p in self.cell_group_params}


class O1Circuit(CircuitBuild):
    """Specializations of methods for the O1.v6a circuits."""

    specializations = {
        brain_regions.cortex: Cortical(by=("layer", "$target")),
        brain_regions.hippocampus: Hippocampal(by=("layer",))
    }


    def __init__(self, *args, **kwargs):
        self.label = "O1"
        super(O1Circuit, self).__init__(*args, **kwargs)

    def random_position(self, brain_region, condition, offset = 50.,
                        *args, **kwargs):
        brain_region_spec = self.specializations[brain_region]
        query = brain_region_spec.cell_query(condition, *args, **kwargs)
                                                              
        bounds\
            = self._helper\
                  .geometric_bounds(query, target=brain_region_spec.target)
                                    
        if bounds is None:
            return None
        box = Cuboid(bounds.bbox[0] + offset, bounds.bbox[1] - offset)
        return random_location(box)

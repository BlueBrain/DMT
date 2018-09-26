"""Utility class to work with brain regions.
This is a good playground to understand descriptors and type validations."""

from abc import ABC, abstractmethod
from dmt.vtk.utils.descriptor import Field, WithFCA
from dmt.vtk.utils.string_utils import make_label, make_name


class BrainRegion(WithFCA, ABC):
    """Base class to represent regions of the brain.

    Attributes
    ----------------------------------------------------------------------------
    __subtypes__ :: Dict
    __values__ :: List, or a Generator ()

    __label__ :: String #deriving class should modify, eg Cortex
    """
    name = Field(
        __name__="name",
        __type__=str,
        __doc__="""A name that will be used to point to this BrainRegion.
        Make sure that you enter as unique name as you can imagine. Some
        level disambiguation will be used to make name unique."""
    )
    label = Field(
        __name__="label",
        __type__=str,
        __doc__="Specify how to call this BrainRegion in reports and plots."
    )
    acronyms = Field(
        __name__="acronyms",
        __type__=list,
        __doc__="""A list of acronyms that may be used for this brain-region."""
    )
    subregions = Field(
        __name__="subregions",
        __type__=dict,
        __doc__="""You may specify the regions contained within this BrainRegion.
        This enables a brain region hierarchy. Its value will default to an
        empty dict."""
    )

    __known_brain_regions = {}

    """Layer in the cortex."""
    def __new__(cls, name, acronym=None, subregions=[]):
        """Check if a brain region with this label is already known."""
        label = make_label(name)
        if label in BrainRegion.__known_brain_regions:
            return BrainRegion.__known_brain_regions[label]
        return super(BrainRegion, cls).__new__(cls)

    def __init__(self, name, acronym=None, subregions=[]):
        """..."""
        label = make_label(name)
        if label not in BrainRegion.__known_brain_regions:
            self.label = label
            self.name = make_name(name)
            self.acronyms = [] if not acronym else [acronym]
            self.subregions = {r.label: r for r in subregions}
            BrainRegion.__known_brain_regions[label] = self
        else:
            self.name = make_name(name)
            if acronym and acronym not in self.acronyms:
                self.acronyms.append(acronym)
            self.subregions.update({r.label: r for r in subregions})

    def add(self, subregion):
        """Add a subtype."""
        self.subregions[subregion.label] = subregion

    def __str__(self):
        """..."""
        return self.label

    def __repr__(self):
        """represent this BrainRegion"""
        return "{}({})".format(self.__class__.__name__, self.__str__())


    @classmethod
    def known_regions(self):
        return [v for v in self.__known_brain_regions.values()]


whole_brain = BrainRegion("whole_brain", acronym=["WB"])

cerebrum = BrainRegion("cerebrum", acronym=["CH"])
whole_brain.add(cerebrum)

cortex = BrainRegion("cortex", acronym=["CTX"])
cerebrum.add(cortex)

hippocampus = BrainRegion("hippocampus", acronym=["HIP"])
cerebrum.add(hippocampus)


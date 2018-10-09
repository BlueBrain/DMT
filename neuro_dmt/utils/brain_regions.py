"""Utility class to work with brain regions.
This is a good playground to understand descriptors and type validations."""

from abc import ABC, abstractmethod
from dmt.vtk.utils.descriptor import Field, WithFCA
from dmt.vtk.utils.string_utils import make_label, make_name
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter


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
        level disambiguation will be used to make name unique.""")
    
    label = Field(
        __name__="label",
        __type__=str,
        __doc__="Specify how to call this BrainRegion in reports and plots.")
    
    acronyms = Field(
        __name__="acronyms",
        __type__=list,
        __doc__="""A list of acronyms that may be used for this brain-region.""")
    
    subregions = Field(
        __name__="subregions",
        __type__=dict,
        __is_valid_value__=Field.typecheck.mapping(str, "__class__"),
        __doc__="""You may specify the regions contained within this BrainRegion.
        This enables a brain region hierarchy. Its value will default to an
        empty dict.""")
    
    spatial_parameters = Field(
        __name__="spatial_parameters",
        __type__=dict,
        __is_valid__=Field.typecheck.mapping(str, FiniteValuedParameter),

        __doc__="""Spatial parameters.""")

    reference_atlas = Field.Optional(
        __name__="reference_atlas",
        __type__=object,
        __doc__="The atlas in which this BrainRegion is defined.")
    
    hierarchy_path = Field.Optional(
        __name__="hierarchy_path",
        __type__=tuple,
        __is_valid__=Field.typecheck.collection(tuple),
        __doc__="""Hierarchical path to this BrainRegion, starting from
        the root in a Brain Atlas. We make this Field optional, as a concept
        that might become useful in the future. The inner tuples should be
        type (str, int), with the first element an abbreviation, the second
        an integer.""",
        __examples__=[(('Br', 65535), ('SSCtx', 1100), ('S1', 721), ('S1HL', 726))])

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
            self.subregions = {}
            for r in subregions:
                self.subregions = self.add_subregion(r)
            self.spatial_parameters = {}
            BrainRegion.__known_brain_regions[label] = self
        else:
            self.name = make_name(namej)
            if acronym and acronym not in self.acronyms:
                self.acronyms.append(acronym)
            self.subregions.update({r.label: r for r in subregions})

    def add_subregion(self, subregion):
        """..."""
        self.subregions[subregion.label]\
            = self.subregions.get(subregion.label, set()).union({subregion})
        return self.subregions

    def add_spatial_parameter(self, param):
        """..."""
        self.spatial_parameters[param.label]\
            = self.spatial_parameters.get(param.label, set()).union({param})
        for subregion_set in self.subregions.values():
            for subregion in subregion_set:
                subregion.add_spatial_parameter(param)
        return

    def add(self, something):
        """Add a subtype."""
        if isinstance(something, BrainRegion):
            self.add_subregion(something)
        elif isinstance(something, FiniteValuedParameter):
            self.add_spatial_parameter(something)
        else:
            self.logger.warn(
                self.logger.get_source_info(),
                "Unknown type '{}'.".format(something.__class__.__type__)
            )
        return

    def __str__(self):
        """..."""
        return self.name

    def __repr__(self):
        """represent this BrainRegion"""
        return "{}({})".format(self.__class__.__name__, self.__str__())

    @classmethod
    def known_regions(self):
        return [v for v in self.__known_brain_regions.values()]


whole_brain = BrainRegion("Whole Brain", acronym=["WB"])

cerebrum = BrainRegion("Cerebrum", acronym=["CH"])
whole_brain.add(cerebrum)

cortex = BrainRegion("Cortex", acronym=["CTX"])
cerebrum.add(cortex)

sscx = BrainRegion("Somatosensory Cortex", acronym=["SSCX"])
cortex.add(sscx)

hippocampus = BrainRegion("Hippocampus", acronym=["HIP"])
cerebrum.add(hippocampus)

ca1 = BrainRegion("Cornus Ammonis 1", acronym=["CA1"])

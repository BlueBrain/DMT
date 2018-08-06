"""Phenomena that occur in the brain."""

from abc import ABC, abstractmethod
from typing import List
from dmt.vtk.phenomenon import Phenomenon

class BrainRegionPhenomenon(Phenomenon):
    """A phenomenon that involves a brain region.
    Suppose the phenomenon describes a scalar quantity in each of the
    subregions of this region. The result of a single measurement of this 
    phenomenon will thus be a tuple, with an element for each of the 
    sub-region. Thus the same phenomenon, such as cell density, will result in
    a measurement that has a different type that depends on the brain region
    where it is made. We decide to make this dependence explicit by having a
    different type of the same phenomenon for each brain region."""


    @abstractmethod
    @property
    def is_atlas_based(self) -> bool:
        """Was the circuit atlas based?"""
        pass

    @abstractmethod
    @property
    def reference_atlas(self) -> str:
        """URI for the brain atlas used for determining brain regions.
        Return "NA" if the atlas is not applicable."""
        pass

    @abstractmethod
    @property
    def region_label(self) -> str:
        """The label of this brain region can be the acronym
        used in the atlas."""
        pass

    @abstractmethod
    @property
    def region_hierarchy_path(self) -> List[(str, int)]:
        """a list of (subregion name, integer IDs)
        of the hierarchical path leading up to this brain region."""
        pass

    @abstractmethod
    @property
    def subregions(self) -> List[str]:
        """Subregions of the primary brain region that
        this is a cell density of.
        For example, in the cortex this should return
        ['L1', 'L2', 'L3', 'L4', 'L5', 'L6'].
        This method may be mixed in by a class that
        represents brain region hierarchy."""
        pass

class AtlasBasedRegion:
    """Behavior for atlas based regions to be mixed in."""

    is_atlas_based = True

    def __init__(self, atlas_uri):
        self._atlas_uri = atlas_uri

    @property
    def is_atlas_based(self) -> bool:
        return True


class SomatosensoryCortexHindLimbPhenomenon(AtlasBasedRegion,
                                            BrainRegionPhenomenon):
    """Phenomenon in the Somatosensory cortex hind limb."""

    def __init__()

    @property
    def region_label(self) -> str:
        return "S1HL"

    @property
    def region_hierarchy_path(self) -> List[(str, int)]:
        """the hierarchical path leading to
        the somatosensory cortex hind limb, hard coded for now"""
        return [('Br', 65535), ('SSCtx', 1100), ('S1', 721), ('S1HL', 726)]

    @property
    def subregions(self) -> List[str]:
        """Hard coded sub-regions inside the S1HL.
        This method should be available for all cortex regions."""
        return ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']



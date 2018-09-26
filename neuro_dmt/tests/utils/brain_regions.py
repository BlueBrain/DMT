"""Test Develop BrainRegion"""

from neuro_dmt.utils.brain_regions import *

sscx = BrainRegion("somatosensory")

cortex2 = BrainRegion("cortex", acronym="CX", subregions=[sscx])

assert cortex == cortex2
assert hash(cortex) == hash(cortex2)



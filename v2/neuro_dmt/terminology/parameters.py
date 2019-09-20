from dmt.tk.terminology.parameters import Parameter

LAYER = Parameter('layer', 'a layer of some brain region')
MTYPE = Parameter('mtype', 'mtype classification')
SYNAPSE_CLASS = Parameter("synapse_class", 'synapse class of cell, excitatory, inhibitory, etc.')
MORPH_CLASS = Parameter("morphology_class", "class of morphology, such as pyramidal, interneuron")
MESOCOLUMN = Parameter("mesocolumn", "not actually sure tbh")
HYPERCOLUMN = Parameter("hypercolumn", "yeah... this isn't really clear")
BRAIN_REGION = Parameter("region", "region of the brain, as BBA-style acronym")
PRESYNAPTIC = Parameter('pre', "presynaptic cell group, as a dict of other parameters")
POSTSYNAPTIC = Parameter('post', "postsynaptic cell group as a dict of other parameters")
DEPTH = Parameter('depth', "depth into region")
HEIGHT = Parameter('height', "height from bottom of region")

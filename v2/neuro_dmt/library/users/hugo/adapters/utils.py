LAYER = 'layer'
MTYPE = 'mtype'
SYN_CLASS = 'sclass'
MORPH_CLASS = 'mclass'
COLUMN = 'column'
REGION = 'region'


def _list_if_not_list(item):
    """make something a list if it isn't"""
    if isinstance(item, list):
        return item
    return [item]


# TODO: in principle, translating between naming conventions is the
#       domain of nexus, right?
def translate_ABI_to_Paxinos(ABI_region):
    return ABI_region.replace("SSp", "S1").replace("-bfd", "BF")\
                     .replace("-ul", "FL").replace("-ll", "HL")\
                     .replace("-m", "J").replace("-tr", "Tr")\
                     .replace("-dz", "DZ").replace("-dzo", "DZO")\
                     .replace("-sh", "Sh").replace("-ulp", "ULp")\
                     .replace("SS", "SSCtx").replace("SSs", "S2")

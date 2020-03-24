"""
Translate atlas terminologies.
"""

def ABI_to_Paxinos(region):
    """
    Translate an ABI region to a Paxinos regio n.

    TODO: Provide explanation for each `replace below.`

    TODO: An explicit mapping will be easier :to understand.
    """
    return region\
        .replace("SSp", "S1")\
        .replace("-bfd", "BF")\
        .replace("-ul", "FL")\
        .replace("-ll", "HL")\
        .replace("-m", "J")\
        .replace("-tr", "Tr")\
        .replace("-dz", "DZ")\
        .replace("-dzo", "DZO")\
        .replace("-sh", "Sh")\
        .replace("-ulp", "ULp")\
        .replace("SS", "SSCtx")\
        .replace("SSs", "S2")

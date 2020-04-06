# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published
# by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License 
# for more details.

# You should have received a copy of the GNU Lesser General Public License 
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

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

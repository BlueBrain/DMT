# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Test develop mock circuit.
(An attempt at a loose approach towards test / behavior driven development.)
"""

import pandas as pd
from dmt.tk.journal import Logger
from .. import CircuitComposition, SimpleUniformRandomConnectivity

__log = Logger(client = "test develop mock circuit")

__layers = (1, 2, 3, 4, 5, 6)

__thickness_layer ={
    1: 122.3,
    2: 113.5,
    3: 302.9,
    4: 176.4,
    5: 477.9,
    6: 647.3}

__cell_density_layer ={
    1: 18566,
    2: 131561,
    3: 81203,
    4: 183128,
    5: 98080,
    6: 116555}

__ei_ratio_layer ={
    1: 0.,
    2: 2.55,
    3: 5.63,
    4: 9.55,
    5: 4.93,
    6: 9.49}

__length_base = 250.

__mtypes =[
    'L1_DAC',
    'L1_DLAC',
    'L1_HAC',
    'L1_NGC-DA',
    'L1_NGC-SA',
    'L1_SLAC',
    'L23_BP',
    'L23_BTC',
    'L23_ChC',
    'L23_DBC',
    'L23_LBC',
    'L23_MC',
    'L23_NBC',
    'L23_NGC',
    'L23_PC',
    'L23_SBC',
    'L4_BP',
    'L4_BTC',
    'L4_ChC',
    'L4_DBC',
    'L4_LBC',
    'L4_MC',
    'L4_NBC',
    'L4_NGC',
    'L4_PC',
    'L4_SBC',
    'L4_SP',
    'L4_SS',
    'L5_BP',
    'L5_BTC',
    'L5_ChC',
    'L5_DBC',
    'L5_LBC',
    'L5_MC',
    'L5_NBC',
    'L5_NGC',
    'L5_SBC',
    'L5_STPC',
    'L5_TTPC1',
    'L5_TTPC2',
    'L5_UTPC',
    'L6_BP',
    'L6_BPC',
    'L6_BTC',
    'L6_ChC',
    'L6_DBC',
    'L6_IPC',
    'L6_LBC',
    'L6_MC',
    'L6_NBC',
    'L6_NGC',
    'L6_SBC',
    'L6_TPC_L1',
    'L6_TPC_L4',
    'L6_UTPC']

def __get_layers(mtype):
    """
    Extract layer info from the name of a mtype.
    """
    n = int(mtype.split('_')[0][1:])
    l0 = n % 10
    l1 = int(n / 10)
    return [l1, l0] if l1 != 0 else [l0]

def __get_mtypes(layer):
    """
    Get mtypes found in 'layer'.
    Out assumption is that the layer info in the mtype string
    is actually the layer or layers where this mtype is found.
    """
    return [
        mtype for mtype in __mtypes
        if layer in __get_layers(mtype)]

def __is_excitatory(mtype):
    """
    Is 'mtype' excitatory?
    """
    return  "PC" in mtype

def __get_exc_cell_density(layer):
    """
    Density of an excitatory cells in given 'layer'
    """
    number_excitatory_mtypes = sum(
        __is_excitatory(mtype)
        for mtype in __get_mtypes(layer))
    excitatory_fraction =\
        __ei_ratio_layer[layer] / (1. + __ei_ratio_layer[layer])
    total_density =\
        __cell_density_layer[layer]
    
    __log.debug(
        __log.get_source_info(),
        "get excitatory cell density for layer {}".format(layer),
        "with number of excitatory mtypes: {}"\
        .format(number_excitatory_mtypes))
    return\
        total_density * excitatory_fraction / number_excitatory_mtypes\
        if excitatory_fraction > 0. else\
           0.

def __get_inh_cell_density(layer):
    """
    Density of an inhibitory cells in given 'layer'
    """
    number_inhibitory_mtypes = sum(
        not __is_excitatory(mtype)
        for mtype in __get_mtypes(layer))
    inhibitory_fraction =\
        1. / (1. + __ei_ratio_layer[layer])
    total_density =\
        __cell_density_layer[layer]
    return\
        total_density * inhibitory_fraction / number_inhibitory_mtypes

def __get_cell_density(layer, mtype):
    """
    'mtype' cell density in 'layer'
    """
    density =\
        0. if layer not in __get_layers(mtype)\
        else (__get_exc_cell_density(layer)\
              if __is_excitatory(mtype)\
              else __get_inh_cell_density(layer))
    return {
        "mtype": mtype,
        "layer": layer,
        "mean": density,
        "std": 0.}

__cell_density =\
    pd.DataFrame([
        __get_cell_density(layer, mtype)
        for mtype in __mtypes
        for layer in __layers])\
      .set_index(
          ["mtype", "layer"])

circuit_composition =\
    CircuitComposition(
        layers=__layers,
        thickness_layer=__thickness_layer,
        length_base=__length_base,
        mtypes=__mtypes,
        cell_density=__cell_density)

circuit_connectivity =\
    SimpleUniformRandomConnectivity(
        afferent_degree_mtype={
            mtype: 2000 for mtype in __mtypes},
        synapse_count_pathway={
            pre_mtype: {
                post_mtype: 4
                for post_mtype in __mtypes}
            for pre_mtype in __mtypes})

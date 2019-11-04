"""
Test develop mock circuit.
(An attempt at a loose approach towards test / behavior driven development.)
"""

import pandas as pd
from bluepy.v2.enums import Synapse
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
    'L1_SLAC',
    'L23_MC',
    'L23_ChC',
    'L23_SBC',
    'L4_LBC',
    'L4_NGC',
    'L4_TPC',
    'L5_DBC',
    'L5_MC',
    'L5_TPC:A',
    'L5_TPC:B',
    'L5_UPC',
    'L6_ChC',
    'L6_IPC',
    'L6_MC',
    'L6_TPC:A',
    'L6_TPC:B',
    'L6_UPC']

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
            mtype: 200 for mtype in __mtypes},
        synapse_count_pathway={
            pre_mtype: {
                post_mtype: 4
                for post_mtype in __mtypes}
            for pre_mtype in __mtypes})

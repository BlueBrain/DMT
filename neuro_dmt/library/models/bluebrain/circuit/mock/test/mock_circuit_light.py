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
from .. import\
    CircuitComposition,\
    SimpleUniformRandomConnectivity,\
    SimpleUniformRandomConnectivityWithMtypeDependence

log = Logger(client = "test develop mock circuit")

layers =  (1, 2, 3, 4, 5, 6)

regions = ("S1HL", "S1FL", "S1Tr", "S1Sh")

thickness_layer ={
    1: 122.3,
    2: 113.5,
    3: 302.9,
    4: 176.4,
    5: 477.9,
    6: 647.3}

cell_density_layer ={
    1: 18566,
    2: 131561,
    3: 81203,
    4: 183128,
    5: 98080,
    6: 116555}

ei_ratio_layer ={
    1: 0.,
    2: 2.55,
    3: 5.63,
    4: 9.55,
    5: 4.93,
    6: 9.49}

length_base = 250.

mtypes =[
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

def get_layers(mtype):
    """
    Extract layer info from the name of a mtype.
    """
    n = int(mtype.split('_')[0][1:])
    l0 = n % 10
    l1 = int(n / 10)
    return [l0, l1]\
        if l1 != 0 else\
           [l0]

def get_mtypes(layer):
    """
    Get mtypes found in 'layer'.
    Out assumption is that the layer info in the mtype string
    is actually the layer or layers where this mtype is found.
    """
    return [
        mtype for mtype in mtypes
        if layer in get_layers(mtype)]

def is_excitatory(mtype):
    """
    Is 'mtype' excitatory?
    """
    return  "PC" in mtype

def get_exc_cell_density(layer):
    """
    Density of an excitatory cells in given 'layer'
    """
    number_excitatory_mtypes = sum(
        is_excitatory(mtype)
        for mtype in get_mtypes(layer))
    excitatory_fraction =\
        ei_ratio_layer[layer] / (1. + ei_ratio_layer[layer])
    total_density =\
        cell_density_layer[layer]
    
    log.debug(
        log.get_source_info(),
        "get excitatory cell density for layer {}".format(layer),
        "with number of excitatory mtypes: {}"\
        .format(number_excitatory_mtypes))
    return\
        total_density * excitatory_fraction / number_excitatory_mtypes\
        if excitatory_fraction > 0. else\
           0.

def get_inh_cell_density(layer):
    """
    Density of an inhibitory cells in given 'layer'
    """
    number_inhibitory_mtypes = sum(
        not is_excitatory(mtype)
        for mtype in get_mtypes(layer))
    inhibitory_fraction =\
        1. / (1. + ei_ratio_layer[layer])
    total_density =\
        cell_density_layer[layer]
    return\
        total_density * inhibitory_fraction / number_inhibitory_mtypes

def get_cell_density(region, layer, mtype):
    """
    'mtype' cell density in 'layer'
    """
    density =\
        0. if layer not in get_layers(mtype)\
        else (get_exc_cell_density(layer)\
              if is_excitatory(mtype)\
              else get_inh_cell_density(layer))
    return {
        "mtype": mtype,
        "region": region,
        "layer": layer,
        "mean": density,
        "std": 0.}

cell_density =\
    pd.DataFrame([
        get_cell_density(region, layer, mtype)
        for mtype in mtypes
        for region in regions
        for layer in layers])\
      .set_index(
          ["mtype", "region", "layer"])

circuit_composition =\
    CircuitComposition(
        layers=layers,
        regions=regions,
        thickness_layer=thickness_layer,
        length_base=length_base,
        mtypes=mtypes,
        cell_density=cell_density)

circuit_connectivity_mtype_dependent =\
    SimpleUniformRandomConnectivityWithMtypeDependence(
        afferent_degree_mtype={
            mtype: 200 for mtype in mtypes},
        synapse_count_pathway={
            pre_mtype: {
                post_mtype: 4
                for post_mtype in mtypes}
            for pre_mtype in mtypes})
circuit_connectivity =\
    SimpleUniformRandomConnectivity(
        mean_afferent_degree=200,
        mean_synapse_count=4)

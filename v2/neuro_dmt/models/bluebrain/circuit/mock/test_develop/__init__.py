"""
Test develop mock circuit.
(An attempt at a loose approach towards test / behavior driven development.)
"""

import pandas as pd
from bluepy.v2.enums import Synapse
from ..mock import CircuitComposition

Synapse.
def get_test_circuit_composition():
    """
    A Test Composition
    """

    layers = (1, 2, 3, 4, 5, 6)

    thickness_layer ={
        1: 122.3,
        2: 113.5,
        3: 302.9,
        4: 176.4,
        5: 477.9,
        6: 647.3}

    ei_ratio_layer ={
        1: 0.,
        2: 0.18,
        3: 0.18,
        4: 0.12,
        5: 0.20,
        6: 0.16}

    base_column = 1000

    mtypes =[
        'L1_NGC-SA',
        'L1_SAC',
        'L23_NBC',
        'L2_TPC:A',
        "L23_BTC",
        "L23_LBC",
        "L23_MC",
        "L23_NBC",
        "L23_SBC",
        'L4_NBC',
        "L4_BTC",
        "L4_LBC",
        "L4_MC",
        "L4_SBC",
        'L4_SSC',
        'L4_UPC',
        "L5_BRC",
        "L5_MC",
        'L5_TPC:B',
        'L5_TPC:C',
        'L6_CHC',
        'L6_DBC',
        'L6_NGC',
        'L6_SBC',
        "L6_BTC",
        'L6_TPC:A',
        'L6_TPC:C',
        'L6_UPC']

    cell_density_layer ={
        1: 18566,
        2: 131561,
        3: 81203,
        4: 183128,
        5: 98080,
        6: 116555}

    @property
    def cell_density(self):
        """
        Example density of cells by mtype, and layer,
        per cubic milli-meter
        """
        def __get_layers(mtype):
            """
            Extract layer info from the name of a mtype.
            """
            n = int(m.split('_')[0][1:])
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
                mtype for mtype in self.mtypes
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
                1 for mtype in __get_mtypes(layer)
                if __is_excitatory(mtype))
            excitatory_fraction =\
                self.ei_ratio[layer] / (1. + self.ei_ratio[layer])
            total_density =\
                self.cell_density_layer[layer]
            return\
                 total_density * excitatory_fraction / number_excitatory_mtypes

        def __get_inh_cell_density(layer):
            """
            Density of an inhibitory cells in given 'layer'
            """
            number_inhibitory_mtypes = sum(
                1 for mtype in __get_mtypes(layer)
                if not __is_excitatory(mtype))
            inhibitory_fraction =\
                1. / (1. + self.ei_ratio[layer])
            total_density =\
                self.cell_density_layer[layer]
            return\
                total_density * inhibitory_fraction / number_inhibitory_mtypes


        def __get_cell_density(layer, mtype):
            """
            Generate a random cell density.
            """
            density =\
                __get_exc_cell_density(layer) if __is_excitatory(mtype)\
                else __get_inh_cell_density(layer)
            return {
                "mtype": mtype,
                "layer": layer,
                "mean": density,
                "error": 0.}

        return\
            pd.DataFrame([
                __get_cell_density(mtype, layer),
                for mtype in self.mtypes
                for layer in self.layers])\
              .set_index(
                  ["mtype", "layer"])

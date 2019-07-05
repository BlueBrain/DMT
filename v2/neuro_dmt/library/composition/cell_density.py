import pandas as pd
from dmt.analysis import Analysis
from dmt.model.interface import interfacemethod, Interface
from neuro_dmt.library.composition import SimpleValidation
from neuro_dmt.library.composition.utils import plot_columns


class CellDensityValidation(SimpleValidation):
    """validate cell density"""

    phenomenon = "cell_density"

    # wrapper because python is bizarre
    # TODO: make it work like it should
    def plot(self, *args, **kwargs):
        return plot_columns(*args, **kwargs)

    class AdapterInterface(Interface):

        @interfacemethod
        def cell_density(adapter_self, query):
            """
            return the cell density of the adapted model
            for parameters specified by query

            Args:
            adapter_self: the adapted model. Will be implicitly passed when
                         the adaptermethod is invoked
            query: a dict or dict-like object with key-value pairs specifying
                  where to get cell density, and of what cell types
                  # TODO: document keys in a reusable enum
                  keys may include:
                      'region': brain region acronym
                                (using BBA/ABI region acronyms)
                      'layer': the layer of the brain region modelled
                               as a string, not integer. For cortex:
                               "L1, L2..." etc. rather than '1', '2'
                      'sclass': the synapse class of the cell
                                ('EXC', 'INH' or 'UN')
                      'mclass': the morphological class ('PC' or 'INT')
                      'mtype': the Mtype of the cell, without region or
                               layer prefix ('IPC', rather than 'L2_IPC')
                               to specify layer or region, use the associated
                               keys
            Returns: One or more samples of cell density (float)
            """
            pass

    def get_measurement(self, model, q):
        return model.cell_density(q)


class INHRatioValidation(CellDensityValidation):

    phenomenon = "inhibitory_ratio"

    def get_measurement(self, model, q):
        q_INH = dict(**q)
        q_INH['sclass'] = 'INH'
        return model.cell_density(q_INH) / model.cell_density(q)

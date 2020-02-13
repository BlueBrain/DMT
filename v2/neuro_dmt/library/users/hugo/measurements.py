import numpy as np
from neuro_dmt.terminology import cell, circuit, neuroscience
from dmt.tk import terminology
# TODO: docstrings

cell_density = terminology.Term(
    "Cell Density",
    "number of cells per cubic millimeter (cells / mm3)")


class CellDensityMeasurement:

    phenomenon = cell_density

    def __call__(self, adapter, model, **parameters):
        return adapter.get_cell_density(model, **parameters)


inhibitory_proportion = terminology.Term(
    "Inhibitory Proportion",
    "proportion of cells which are inhibitory")


class InhibitoryProportionMeasurement:

    phenomenon = inhibitory_proportion

    # TODO: this way of characterizing ratios is restrictive.
    #       what if you want to do by some spatial property?
    #       e.g what proportion of cells in ncx are in L1?
    @terminology.use(*circuit.all)
    def __call__(self, adapter, model, **parameters):
        total_density = adapter.get_cell_density(model, **parameters)
        inh_density = adapter.get_cell_density(
            model, **{cell.synapse_class: 'INH'},
            **parameters)
        print(inh_density)
        return inh_density / total_density


synapse_density = terminology.Term(
    "Synapse Density",
    "Number of synapses per cubit millimeter")


class SynapseDensityMeasurement:

    phenomenon = synapse_density

    def __call__(self, adapter, model, **parameters):
        return adapter.get_synapse_density(model, **parameters)


class _HasSampleSize:
    def __init__(self, sample_size=100):
        self.sample_size=sample_size


connection_probability = terminology.Term('Connection Probability',
                              "The probability of a connection existing between two random cells, "
                              "one from a presynaptic group, one from a postsynaptic group")


class ConnectionProbabilityMeasurement(_HasSampleSize):

    phenomenon = connection_probability

    def __call__(self, adapter, model, **parameters):
        connprob = adapter.get_connection_probability(
            model, sample_size=self.sample_size, **parameters)
        return connprob if connprob != 0 else np.nan


synapses_per_connection = terminology.Term(
    'Synapses per Connection',
    "the mean number of synapses on each connection between cells")


class SynapsesPerConnectionMeasurement(_HasSampleSize):

    phenomenon = synapses_per_connection

    def __call__(self, adapter, model, **parameters):
        return adapter.get_synapses_per_connection(
            model, sample_size=self.sample_size, **parameters)


pathway_synapses = terminology.Term(
    "Pathway Synapses",
    "The total number of synapses from one cell group to another")


class PathwaySynapsesMeasurement(_HasSampleSize):

    phenomenon = pathway_synapses

    def __call__(self, adapter, model, **parameters):
        return adapter.get_pathway_synapses(model, **parameters,
                                            sample_size=self.sample_size)

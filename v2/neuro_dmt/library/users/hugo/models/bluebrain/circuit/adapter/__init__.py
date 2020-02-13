"""
Adapt circuit models developed at the Blue Brain Project.
"""
from dmt.model import Adapter
from neuro_dmt import terminology


class CircuitAdapter(Adapter):
    """
    Adapt circuit models developed at the Blue Brain Project.
    """

    def get_cell_density(self, model, **parameters):
        return model.cell_density(**parameters)

    # TODO: parameters?
    def get_mtypes(self, model, properties=(terminology.cell.mtype, )):
        return model.mtypes(properties=properties)

    def get_synapses_per_connection(self, model, **params):
        return model.synapses_per_connection(**params)

    def get_pathway_synapses(self, model, **params):
        return model.pathway_synapses(**params)

    def get_connection_probability(self, model, **params):
        return model.connection_probability(**params)

    def get_divergence(self, model, **params):
        return model.divergence(**params)

    def get_heights(self, model, **params):
        return model.heights(**params)

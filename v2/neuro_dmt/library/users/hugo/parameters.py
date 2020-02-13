import numpy as np
from collections import OrderedDict
from neuro_dmt.terminology import neuroscience


# TODO: measurement and parameters should both declare their interface
class ByHeight:

    def __init__(self, nbins=None, bin_size=None, other_params={}):
        if nbins is None and bin_size is None:
            raise Exception("either nbins or bin_size must be specified")
        if nbins is not None and bin_size is not None:
            raise Exception("nbins and bin_size cannot both be specified")
        self.nbins = nbins
        self.bin_size = bin_size
        self.other_params = other_params
        return

    def __call__(self, adapter, model):
        heights = adapter.get_heights(model, **self.other_params)
        minimum = np.min(heights)
        maximum = np.max(heights)
        if self.nbins is None:
            bin_size = self.bin_size
            nbins = np.ceil(maximum - minimum / bin_size)
        else:
            nbins = self.nbins
            bin_size = (maximum - minimum) / nbins
        return [
            dict(**{neuroscience.height:
                    (minimum + bin_size * i, minimum + bin_size * (i+1))},
                 **self.other_params)
            for i in range(nbins)]


class ByMtypeByEtype:

    def __call__(self, adapter, model):
        return [{neuroscience.mtype: mt, neuroscience.etype: et}
                for mt in adapter.get_mtypes(model)
                for et in adapter.get_etypes(model)]


class MtypeMtypePathways:

    def __call__(self, adapter, model):
        """
        gets the available mtypes from the model
        effectively makes this a 'by mtype' validation
        """
        mtypes = adapter.get_mtypes(model, properties=[neuroscience.mtype, neuroscience.layer, neuroscience.synapse_class])
        def list_if_not_list(item):
            if isinstance(item, list):
                return item
            return [item]
        sorted_mtypes = sorted(mtypes, key=lambda d: (list_if_not_list(d[neuroscience.layer]), d[neuroscience.synapse_class]))
        out= [OrderedDict([(neuroscience.presynaptic, pre), (neuroscience.postsynaptic, post)])
              for post in sorted_mtypes for pre in sorted_mtypes]
        return out


class MtypeMtypePathwaysInCentralColumn:

    def __call__(self, adapter, model):
        pathways = MtypeMtypePathways()(adapter, model)
        for pathway in pathways:
            presynaptic = pathway[neuroscience.presynaptic]
            postsynaptic = pathway[neuroscience.postsynaptic]
            presynaptic[neuroscience.mesocolumn] = 'mc2'
            postsynaptic[neuroscience.mesocolumn] = 'mc2'
        return pathways

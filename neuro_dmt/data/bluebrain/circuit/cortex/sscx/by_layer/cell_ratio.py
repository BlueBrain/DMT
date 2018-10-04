"""By layer cell ratio data."""
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.circuit.composition.by_layer \
    import summarized, with_metadata
from dmt.vtk import datasets

def get_reference_datasets(reference_data_dir):
    ghobril2012  = datasets.load(reference_data_dir, 'Ghobril2012')
    lefort2009   = datasets.load(reference_data_dir, 'Lefort2009')
    beaulieu1992 = datasets.load(reference_data_dir, 'Beaulieu1992')

    #Ghobril does not provide ratios, but counts

    cinh = np.array(ghobril2012['count_inh'])
    call = np.array(ghobril2012['count_all'])
    ghobril2012['ratio_means'] = cinh / call
    ghobril2012['ratio_stds']  = np.sqrt(1./cinh + 1./call) * (cinh / call)

    return dict(
        ghobril2012=with_metadata(ghobril2012
                                  summarized(
                                      ghobril2012['ratio_means'],
                                      ghobril2012['ratio_stds']
                                  )),
        lefort2009=with_metadata(lefort2009,
                                 summarized(lefort2009['ratio_means'],
                                            lefort2009['ratio_stds']
                                 )),
        beaulieu1992=with_metadata(beaulieu1992,
                                   summarized(
                                       beaulieu1992['ratio_means'],
                                              beaulieu1992['ratio_stds']
                                   ))
    )

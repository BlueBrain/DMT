"""By layer cell ratio data."""
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.circuit.composition.by_layer \
    import summarized, get_metadata
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

    ghobril2012_ref_data = get_metadata(ghobril2012)
    ghobril2012_ref_data.data = summarized(ghobril2012['ratio_means'],
                                           ghobril2012['ratio_stds'])

    lefort2009_ref_data = get_metadata(lefort2009)
    lefort2009_ref_data.data = summarized(lefort2009['ratio_means'],
                                          lefort2009['ratio_stds'])

    beaulieu1992_ref_data = get_metadata(beaulieu1992)
    beaulieu1992_ref_data.data = summarized(beaulieu1992['ratio_means'],
                                            beaulieu1992['ratio_stds'])

    return [
        Record(label = "Ghobril 2012",
               region_label = "layer",
               url = ghobril2012.get('url', 'NA'),
               citation = ghobril2012.get('citation', 'NA'),
               what = ghobril2012.get('what', 'inhibitory cell ratio'),
               data = summarized(ghobril2012['ratio_means'],
                                 ghobril2012['ratio_stds'])),
        Record(label = "LeFort 2009",
               region_label = "layer",
               url = lefort2009.get("url", "NA"),
               citation = lefort2009.get("citation", "NA"),
               what = lefort2009.get("what", "inhibitory cell ratio"),
               data = summarized(lefort2009['ratio_means'],
                                 lefort2009['ratio_stds'])),
        Record(label = "Beaulieu 1992",
               region_label = "layer",
               url = beaulieu1992.get("url", "NA"),
               citation = beaulieu1992.get("citation", "NA"),
               what = beaulieu1992.get("what", "inhibitory cell ratio"),
               data = summarized(beaulieu1992['ratio_means'],
                                 beaulieu1992['ratio_stds']))
    ]

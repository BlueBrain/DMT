"""By layer cell ratio data."""
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.circuit.composition.by_layer import summarized
from dmt.vtk import datasets

def get_reference_datasets(reference_data_dir):
        defelipe2011  = datasets.load(reference_data_dir, "DeFelipe2011")
        defelipe2002  = datasets.load(reference_data_dir, "DeFelipe2002")
        anton2014 = datasets.load(reference_data_dir, "AntonSanchez2014")

        return [
            Record(label = 'constraint 1 (DeFelipe et al. 2011)',
                   region_label = 'layer',
                   url = defelipe2011.get('url', 'NA'),
                   citation = defelipe2011.get('citation', 'NA'),
                   what = defelipe2011.get('what', 'synapse density'),
                   data = summarized(defelipe2011['density_means'],
                                        defelipe2011['density_stds'])),
            Record(label = 'constraint 2 (DeFelipe et al. 2002)',
                   region_label = 'layer',
                   url = defelipe2002.get('url', 'NA'),
                   citation = defelipe2002.get('citation', 'NA'),
                   what = defelipe2002.get('what', 'synapse density'),
                   data = summarized(defelipe2002['density_means'],
                                     defelipe2002['density_stds'])),
            Record(label = 'constraint 3 (Anton Sanchez et al. 2014)',
                   region_label = 'layer',
                   url = anton2014.get('url', 'NA'),
                   citation = anton2014.get('citation', 'NA'),
                   what = anton2014.get('what', 'synapse density'),
                   data = summarized(anton2014['density_means'],
                                     anton2014['density_stds']))]

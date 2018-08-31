"""By layer cell ratio data."""
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.circuit.composition.by_layer import summarized
from dmt.vtk import datasets

def get_reference_datasets(reference_data_dir):
        defelipe2011  = datasets.load(reference_data_dir, "DeFelipe2011")
        return [
            Record(label = 'constraint 1 (DeFelipe2011  et al. 2011)',
                   region_label = "layer",
                   citation = defelipe2011.get("citation", "NA"),
                   what = defelipe2011.get("what", "cell density by layer"),
                   url = defelipe2011.get("url", "NA"),
                   data  = summarized(defelipe2011['density_means'],
                                        defelipe2011['density_stds'])
            )
        ]

"""Reference data for layer composition."""
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record

def get_metadata(reference_dataset):
    return Record(
        label = reference_dataset.get('short_name', 'unknown'),
        region_label = 'layer',
        url = reference_dataset.get('url', 'unknown'),
        citation = reference_dataset.get('citation', 'unknown'),
        what = reference_dataset.get('what', 'dunno')
    )
def summarized(means, stdevs, scale_factor=1.0):
    means = np.array(means)
    stdevs = np.array(stdevs)
    return pd.DataFrame({'region': ['L{}'.format(l) for l in range(1, 7)],
                         'mean': scale_factor * means,
                         'std': scale_factor * stdevs})


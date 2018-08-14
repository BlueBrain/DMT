"""By layer cell density data."""

from dmt.vtk.utils.collections import Record

def get_measurement_record(mdict):
    """Convert a dictionary to a Record with meta-data."""
    return Record(
        measurement_label = "cell density",
        region_label = "Layer",
        data = mdict['summary'],
        citation = mdict.get("citation", "NA"),
        what = mdict.get("what", "Cell density by layer.")
    )

def get_reference_datasets(reference_data_dir):
    """Available reference data to be used to validate cell density."""
    import dmt.vtk.datasets as datasets
    import numpy as np
    import pandas as pd
    defelipe2002 = datasets.load(reference_data_dir, "DeFelipe2002")
    defelipe2011 = datasets.load(reference_data_dir, "DeFelipe2011")
    defelipe2014 = datasets.load(reference_data_dir, "DeFelipe2014")
    defelipe2017 = datasets.load(reference_data_dir, "DeFelipe2014")
    meyer2010    = datasets.load(reference_data_dir, "Meyer2010")
    sonja        = datasets.load(reference_data_dir, "Sonja")

    df2014Densities = np.vstack([
        ckt['densities'] for ckt in defelipe2014['circuits'].values()
    ])
    defelipe2014['density_means'] = np.mean(df2014Densities, axis=0)
    defelipe2014['density_stds']  = np.std(df2014Densities, axis=0)
    
    df2017Densities = np.vstack([
        ckt['densities'] for ckt in defelipe2017['circuits'].values()
    ])
    defelipe2017['density_means'] = np.mean(df2017Densities, axis=0)
    defelipe2017['density_stds']  = np.std(df2017Densities, axis=0)
    
    def summarized(ds, scale=1.):
        return pd.DataFrame([
            dict(region = 'L{}'.format(l+1),
                 mean = scale * ds['density_means'][l],
                 std = scale * ds['density_stds'][l])
            for l in range(6)
        ])
    
    defelipe2002["summary"] = summarized(defelipe2002)
    defelipe2011["summary"] = summarized(defelipe2011)
    defelipe2014["summary"] = summarized(defelipe2014, scale=1.e-3)
    defelipe2017["summary"] = summarized(defelipe2017, scale=0.8229e-3)
    sonja["summary"] = summarized(sonja)
    meyer2010["summary"] = summarized(meyer2010)
    
    return [get_measurement_record(defelipe2017),
            get_measurement_record(defelipe2014),
            get_measurement_record(defelipe2011),
            get_measurement_record(defelipe2002),
            get_measurement_record(sonja),
            get_measurement_record(meyer2010)]

 

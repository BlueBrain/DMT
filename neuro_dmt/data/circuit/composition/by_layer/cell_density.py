"""By layer cell density data."""
import numpy as np
import dmt.vtk.datasets as datasets

from dmt.vtk.utils.collections import Record
from neuro_dmt.data.circuit.composition.by_layer import summarized
    

def get_reference_datasets(reference_data_dir):
    """Available reference data to be used to validate cell density."""
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
    
    return [
        Record(label = "De Felipe 2017",
               uri = defelipe2017.get("uri", "NA"),
               region_label = "layer",
               data = summarized(defelipe2017['density_means'],
                                 defelipe2017['density_stds'],
                                 scale_factor=0.8229e-3),
               citation = defelipe2017.get("citation", "NA"),
               what = defelipe2017.get("what", "cell density by layer")),
        Record(label = "De Felipe 2014",
               uri = defelipe2014.get("uri", "NA"),
               region_label = "layer",
               data = summarized(defelipe2014['density_means'],
                                 defelipe2014['density_stds'],
                                 scale_factor=1.e-3),
               citation = defelipe2014.get("citation", "NA"),
               what = defelipe2014.get("what", "cell density by layer")),
        Record(label = "De Felipe 2011",
               uri = defelipe2011.get("uri", "NA"),
               region_label = "layer",
               data = summarized(defelipe2011['density_means'],
                                 defelipe2011['density_stds']),
               citation = defelipe2011.get("citation", "NA"),
               what = defelipe2011.get("what", "cell density by layer")),
        Record(label = "De Felipe 2002",
               uri = defelipe2002.get("uri", "NA"),
               region_label = "layer",
               data = summarized(defelipe2002['density_means'],
                                 defelipe2002['density_stds']),
               citation = defelipe2002.get("citation", "NA"),
               what = defelipe2002.get("what", "cell density by layer")),
        Record(label = "Meyer et. al. 2010",
               uri = meyer2010.get("uri", "NA"),
               region_label = "layer",
               data = summarized(meyer2010['density_means'],
                                 meyer2010['density_stds']),
               citation = meyer2010.get("citation", "NA"),
               what = meyer2010.get("what", "cell density by layer")),
        Record(label = "Sonja et. al.",
               uri = sonja.get("uri", "NA"),
               region_label = "layer",
               data = summarized(sonja['density_means'],
                                 sonja['density_stds']),
               citation = sonja.get("citation", "NA"),
               what = sonja.get("what", "cell density by layer"))
    ]


"""Test if the cell density of a model circuit is close to that obtained
from an experiment."""

from abc import abstractmethod
from dmt.validation.test_case import ValidationTestCase
from dmt.aii import requiredmethod, implementation
from neuro_dmt.utils.brain_region import CorticalLayer


def reference_datasets(reference_data_dir):
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
    
    def summarized(ds):
        return pd.DataFrame([
            dict(region='L{}'.format(l+1),
                 mean=ds['density_means'][l],
                 std=ds['density_stds'][l])
            for l in range(6)
        ])
    
    defelipe2002["summary"] = summarized(defelipe2002)
    defelipe2011["summary"] = summarized(defelipe2011)
    defelipe2014["summary"] = summarized(defelipe2014)
    defelipe2017["summary"] = summarized(defelipe2017)
    sonja["summary"] = summarized(sonja)
    meyer2010["summary"] = summarized(meyer2010)
    
    defelipe2014['scale'] = 1.0e-3
    defelipe2017['scale'] = 0.8229e-3
    
    return {'defelipe2017': defelipe2017,
            'defelipe2014': defelipe2014,
            'defelipe2011': defelipe2011,
            'defelipe2002': defelipe2002,
            'sonja': sonja,
            'meyer2010': meyer2010}

    
class CellDensity(ValidationTestCase):
    """CellDensity is a unit test case for validation."""

    def __init__(self, reference_path, p_value_threshold=0.05):
        """
        Parameters
        ----------
        @reference_path :: DirectoryPath #to reference dataset(s)
        """

    @requiredmethod
    def get_cell_density(adapter, circuit):
        """Get cell density for a circuit.
        Parameters
        ----------
        @circuit :: ModelCircuit
        ------------------------
        Return
        ------------------------
        pandas.DataFrame["region", "mean", "std"]"""
        pass

    def __call__(self, circuit, *args, **kwargs):
        """makes CellDensity a callable"""
        output_dir = kwargs.get("output_dir", None)
        model_measurement = self.adapter.get_cell_density(circuit)
        data_measurement  = self.data

        #compare, statistically model measurement against data measurement
        
        raise NotImplementedError("Complete this implementation!!!")

    
    @classmethod
    def probability_of_validity(cls, data_measurement,
                                model_measurement,
                                **kwargs):
        """What is the probability that model's measurement is valid?"""
        from scipy_special import erf
        from dmt.vtk.statistics import FischersPooler






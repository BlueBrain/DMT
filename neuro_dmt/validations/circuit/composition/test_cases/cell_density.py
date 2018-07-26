"""Test if the cell density of a model circuit is close to that obtained
from an experiment."""

import os
import matplotlib as pylab
from dmt.validation.test_case import ValidationTestCase
from dmt.aii import requiredmethod, implementation
from dmt.vtk.utils.plotting import golden_figure
from dmt.vtk.utils.collections import Record
from neuro_dmt.utils.brain_region import CorticalLayer
import neuro_dmt.validations.circuit.composition.by_layer as LayerComposition



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
    """CellDensity is a unit test case for validation.
    Cell density is a spatial composition phenomenon.
    Hence we assume that all measurements are made by region
    in the brain, i.e., the pandas DataFrame passed around as
    measurements must have a column labeled 'region'."""

    def __init__(self, reference_path,
                 p_value_threshold=0.05,
                 plot_customization={}):
        """
        Parameters
        ----------
        @reference_path :: DirectoryPath #to reference dataset(s)
        @p_value_threshold :: Float
        #plot_customization :: dict # that provides customization for a plot

        TODO
        ----------
        Provide a default plot_customization
        """

    @adaptermethod
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

    @adaptermethod
    def get_anatomically_ordered(adapter, data_frame):
        """A pandas DataFrame with one column labelled 'region',
        ordered anatomically.

        MethodType
        ----------
        Adapter -> DataFrame -> DataFrame


        Parameters
        ------------
        @adapter :: Adapter # for a model or for a data-object
        @data_frame :: DataFrame # with the same columns as argument data_frame

        Return
        ------------
        Anatomically ordered data-frame

        Examples
        ---------
        If the region is CorticalDepth, the order can be 
        ['L1', 'L2', 'L3', 'L4', 'L5', 'L6'] or its reverse.
        """
        pass

    def __call__(self, circuit, *args, **kwargs):
        """Make CellDensity a callable"""

        template_dir_name = kwargs.get(
            'template_dir_name', os.path.dirname(LayerComposition.__file__)
        )
        template_file_name = kwargs.get(
            'template_file_name', 'report_html_template.cheetah'
        )
        output_dir = kwargs.get('output_dir', os.getcwd())

        model_measurement = Record(
            label=self.model_adapter.get_label(circuit),
            data=self.model_adapter.get_cell_density(circuit),
        )
        exptl_measurement = Record(
            label=self.experimental.label,
            data=self.experimental.data
        )
        validation_plot_path = LayerComposition.plot_comparison(
            [model_measurement, exptl_measurement],
            title="Cell Density",
            output_dir_path=kwargs.get("output_dir", None)
        )
        self._statistic\
            = LayerComposition.probability_of_validity(
                model_measurement,
                exptl_measurement
            )
        report = Report(...)
        LayerComposition.save_report(report,
                                     template_dir_name,
                                     template_file_name,
                                     output_path=)

"""Provide a method that plugs our Adapter for Blue Brain Circuits into
circuit composition validations, and runs them."""
from abc import abstractmethod
import os
import numpy as np
import pandas as pd
import dmt.vtk.datasets as datasets
from dmt.vtk.utils.collections import Record
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from dmt.vtk.utils.exceptions import MissingRequiredKeywordArgument
from neuro_dmt.validations.circuit.composition.by_layer import \
    CellDensityValidation, \
    CellRatioValidation, \
    InhibitorySynapseDensityValidation, \
    SynapseDensityValidation
from neuro_dmt.data.circuit.composition.cortex.sscx.by_layer \
    import reference_datasets
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.O1.build import O1Circuit
from neuro_dmt.library.bluebrain.circuit import BlueBrainCompositionData


class BlueBrainCellDensityData(BlueBrainCompositionData):
    """..."""
    spatial_parameter = CorticalLayer()

    def __init__(self, location = None, *args, **kwargs):
        """..."""
        kwargs["data"] = (location if location else 
                          os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                                       "work/validations/dmt",
                                       "examples/datasets/cortex/sscx/rat",
                                       "cell_density"))
        super().__init__(*args, **kwargs)

    @classmethod
    def with_metadata(cls, reference_dataset, reference_dataframe):
        return Record(
            label = reference_dataset.get('short_name', 'unknown'),
            region_label = cls.spatial_parameter.label,
            uri = reference_dataset.get('url', 'unknown'),
            citation = reference_dataset.get('citation', 'unknown'),
            what = reference_dataset.get('what', 'dunno'),
            data=reference_dataframe
    )
    @classmethod
    def summarized(cls, means, stdevs, scale_factor=1.0):
        means = np.array(means)
        stdevs = np.array(stdevs)
        return pd.DataFrame(
            {cls.spatial_parameter.label:  range(1, 7),
             'mean': scale_factor * means,
             'std': scale_factor * stdevs}
        ).set_index(cls.spatial_parameter.label)


    @classmethod
    def get_reference_datasets(cls, reference_data_dir):
        """Available reference data to be used to validate cell density."""
        defelipe2002 = datasets.load(reference_data_dir, "DeFelipe2002")
        defelipe2011 = datasets.load(reference_data_dir, "DeFelipe2011")
        defelipe2014 = datasets.load(reference_data_dir, "DeFelipe2014")
        defelipe2017 = datasets.load(reference_data_dir, "DeFelipe2017")
        meyer2010    = datasets.load(reference_data_dir, "Meyer2010")
        sonja        = datasets.load(reference_data_dir, "Sonja")

        df2014Densities = np.vstack([
            ckt['densities'] for ckt in defelipe2014.circuits.values()
        ])
        defelipe2014.density_means = np.mean(df2014Densities, axis=0)
        defelipe2014.density_stds  = np.std(df2014Densities, axis=0)
    
        df2017Densities = np.vstack([
            ckt['densities'] for ckt in defelipe2017.circuits.values()
        ])
        defelipe2017.density_means = np.mean(df2017Densities, axis=0)
        defelipe2017.density_stds  = np.std(df2017Densities, axis=0)

        return Record(
            primary=defelipe2017.short_name,
            datasets={
                defelipe2017.short_name: cls.with_metadata(
                    defelipe2017,
                    cls.summarized(
                        defelipe2017.density_means,
                        defelipe2017.density_stds,
                        scale_factor=0.8229e-3
                    )
                ),
                defelipe2014.short_name: cls.with_metadata(
                    defelipe2014,
                    cls.summarized(
                        defelipe2014.density_means,
                        defelipe2014.density_stds,
                        scale_factor=1.e-3
                    )
                ),
                defelipe2011.short_name: cls.with_metadata(
                    defelipe2011,
                    cls.summarized(
                        defelipe2011.density_means,
                        defelipe2011.density_stds
                    )
                ),
                defelipe2002.short_name: cls.with_metadata(
                    defelipe2002,
                    cls.summarized(
                        defelipe2002.density_means,
                        defelipe2002.density_stds
                    )
                ),
                meyer2010.short_name: cls.with_metadata(
                    meyer2010,
                    cls.summarized(
                        meyer2010.density_means,
                        meyer2010.density_stds
                    )
                ),
                sonja.short_name: cls.with_metadata(
                    sonja,
                    cls.summarized(
                        sonja.density_means,
                        sonja.density_stds
                    )
                )
            }
        )


    def _get_data(self, data, *args, **kwargs):
        """..."""
        #if "data" not in kwargs:
        #    raise MissingRequiredKeywordArgument("data")

        if not self._is_location(data):
            if isinstance(data, Record):
                try:
                    return (data.datasets, data.primary)
                except AttributeError:
                    pass
        else:
            return self._get_data(self._load_from_location(data))

        primary = kwargs.get("primary", None)
        return (data, primary)


    @property
    def description(self):
        """..."""
        try:
            return self._description
        except AttributeError:
            try:
                return self.primary.what
            except AttributeError as e:
                return "Not Available."
        return None



class BlueBrainCellDensityValidation(CellDensityValidation):
    """..."""
    def __init__(self, sample_size=20,
                 sampled_box_shape=50.*np.ones(3),
                 *args, **kwargs):
        super().__init__(
            reference_data=BlueBrainCellDensityData(),
            brain_region=brain_regions.cortex,
            spatial_parameters={CorticalLayer()},
            plotter_type=BarPlotComparison,
            adapter=BlueBrainModelAdapter(
                brain_region=brain_regions.cortex,
                circuit_build=O1Circuit,
                model_label="Blue Brain O1 Circuit for SSCx",
                sample_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs))


validation = dict(cell_density=BlueBrainCellDensityValidation)

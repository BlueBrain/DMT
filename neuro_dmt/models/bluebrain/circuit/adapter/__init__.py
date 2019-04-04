"""Adapters for circuits from the Blue Brain Project.
These adapters leverage the bluepy API.

Guidelines
--------------------------------------------------------------------------------
As a first proof-of-principle we will implement assuming an O1.v6a circuit.
However, we may want to add another level of indirection to abstract away this
detail.
The Circuit type has changed drastically over past years, however if we 
use 'bluepy.v2.circuit.Circuit' as a type for all of them, we will rely on 
manual book-keeping to organize all the different adapters.
"""
from dmt.model import\
    interface, adapter
import numpy as np
import pandas as pd
from bluepy.v2.circuit\
    import Circuit
from bluepy.v2.enums\
    import Cell
#from bluepy.geometry.roi import ROI as RegionOfInterest
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.author\
     import Author
from dmt.vtk.measurement\
     import StatisticalMeasurement
from dmt.vtk.utils.descriptor\
     import Field\
     ,      WithFCA
from dmt.vtk.measurement.parameter.group\
    import ParameterGroup
from dmt.vtk.measurement.parameter.random\
     import get_conditioned_random_variate
from dmt.vtk.utils.logging\
    import Logger\
    ,      with_logging
from dmt.vtk.measurement.condition\
    import Condition, ConditionGenerator
from neuro_dmt.utils.enums\
    import Direction
from neuro_dmt.utils.cell_type\
    import CellType
from neuro_dmt.analysis.comparison.validation.circuit.composition.by_layer\
    import CellDensityValidation\
    ,      CellRatioValidation\
    ,      InhibitorySynapseDensityValidation\
    ,      SynapseDensityValidation
from neuro_dmt.utils.brain_regions\
    import BrainRegion
from neuro_dmt.models.bluebrain.circuit\
     import geometry\
     ,      cell_collection\
     ,      utils\
     ,      BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import BlueBrainCircuitModel
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomSpatialVariate\
    ,      RandomRegionOfInterest\
    ,      RandomSpanningColumnOfInterest\
    ,      RandomCellVariate\
    ,      RandomPairs\
    ,      RandomConnectionVariate\
    ,      RandomPathwayConnectionVariate
from neuro_dmt.models.bluebrain.circuit.geometry\
    import Cuboid, collect_sample, random_location
from neuro_dmt.models.bluebrain.circuit.measurements\
    import composition as composition_measurements
from neuro_dmt.models.bluebrain.circuit.measurements\
    import connectome as connectome_measurements
from neuro_dmt.measurement.parameter.spatial\
    import SomaDistance
from neuro_dmt.measurement.parameter\
    import AtlasRegion
from neuro_dmt.models.bluebrain.circuit.parameters\
    import Mtype\
    ,      MtypePathway


@interface.implementation(CellDensityValidation.AdapterInterface)
@interface.implementation(CellRatioValidation.AdapterInterface)
@interface.implementation(InhibitorySynapseDensityValidation.AdapterInterface)
@interface.implementation(SynapseDensityValidation.AdapterInterface)
@adapter.adapter(BlueBrainCircuitModel) #circuit model type adapted
class BlueBrainModelAdapter(
        WithFCA):
    """Adapt a circuit from the Blue Brain Project (BBP).
    This adapter was developed for the O1.v6a models developed at BBP in 2017-
    2018. The brain (micro-)circuit models are not atlas based, but are
    organized as hexagonal columns, while respecting the connectivity patterns
    observed in real brain circuits.
    """
    author=\
        Author.zero
    label=\
        "adapter"
    brain_region=\
        Field.Optional(
            __name__="brain_region",
            __type__=BrainRegion,
            __doc__="Provides a model independent tag for the brain region.")
    sample_size=\
        Field(
            __name__="sample_size",
            __type__=int,
            __default__=20,
            __doc__="""Number of samples to be drawn for each
            statistical measurement.""")
    model_label=\
        Field(
            __name__="model_label",
            __type__=str,
            __default__="BlueBrainCircuitAdapter.",
            __doc__="""Label to be used in reporting.""")
    
    def __init__(self,
            sampled_box_shape=100.*np.ones(3), 
            *args, **kwargs):
        """..."""
        self._sampled_box_shape\
            = sampled_box_shape
        super().__init__(
            *args, **kwargs)

    def get_label(self,
            circuit):
        """method required by adapter interface."""
        return self.model_label

    def filled(self,
            measurement,
            by):
        """...

        Parameters
        ------------------------------------------------------------------------
        measurement :: pandas.DataFrame,#with columns 'mean' and 'std'
        by :: List[FiniteValuedParameter] #the parameters conditioning
        ~                                 #self.spatial_random_variate
        """
        if measurement.data.empty:
            if len(by) > 1:
                parameter_group=\
                    ParameterGroup(*by)
                parameter_value_dicts=\
                    list(ParameterGroup(*by).kwargs)
                index=\
                    pd.MultiIndex.from_tuples(
                        tuples=[
                            tuple(parameter_value[parameter.label]
                                  for parameter in by)
                            for parameter_value in parameter_value_dicts],
                        names=[parameter.label for parameter in by])

            if len(by) == 1:
                index=\
                    pd.Index(
                        by.values,
                        name=by.label)
            measurement.data=\
                pd.DataFrame(
                    [{"mean": np.nan, "std": np.nan} for _ in index],
                    index = index)
        else:
            for p in by:
                measurement.data\
                    = p.filled(
                    measurement.data)
        return measurement

    def statistical_measurement(self,
            circuit_model,
            method,
            get_random_variate,
            parameters={},
            fill_missing_param_values=True,
            *args, **kwargs):
        """..."""
        self.logger.debug(
            self.logger.get_source_info(),
            """get statistical measurement from adapter with parameters {}"""\
            .format(parameters))
        self.logger.debug(
            self.logger.get_source_info(),
            """get statitistical measurement from adapter with kwargs {}"""\
            .format(list(kwargs.keys())))
        if not "is_permissible" in kwargs:
            raise ValueError(
                "statistical measurement called without is_permissible")
        measurement=\
            StatisticalMeasurement(
                random_variate=get_random_variate(
                    circuit_model,
                    *args, **kwargs
                ).given(
                    *parameters,
                    **kwargs),
                sample_size=self.sample_size
            ).get(
                method,
                *args, **kwargs)
        if fill_missing_param_values:
            measurement=\
                self.filled(
                    measurement,
                    by=parameters)
        return measurement.plus(
            model_label=circuit_model.get_label(),
            model_uri=circuit_model.get_uri())

    def spatial_measurement(self,
            circuit_model,
            method,
            parameters=[],
            fill_missing_param_values=True,
            *args, **kwargs):
        """..."""
        if not parameters: #special case, sensible for specific area circuits (sscx, CA1)
            measurment=\
                self.statistical_measurement(
                    circuit_model,
                    method,
                    get_random_variate=RandomSpanningColumnOfInterest,
                    parameters={circuit_model\
                                .geometry\
                                .spanning_column_parameter()},
                    fill_missing_param_values=fill_missing_param_values,
                    *args, **kwargs)
        measurement=\
            self.statistical_measurement(
                circuit_model,
                method,
                get_random_variate=RandomRegionOfInterest,
                parameters=parameters,
                sampled_box_shape=self._sampled_box_shape,
                *args, **kwargs)
        return Record(
            brain_region=circuit_model.brain_region,
            **measurement.as_dict)
        return measurement
    
    def get_cell_density(self,
            circuit_model,
            spatial_parameters=[],
            by_property=None,
            for_cell_type=CellType.Any,
            *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                circuit_model=circuit_model,
                method=composition_measurements.CellDensity(
                    circuit_model.bluepy_circuit,
                    by_property=by_property,
                    for_cell_type=for_cell_type,
                    *args, **kwargs),
                parameters=spatial_parameters,
                *args, **kwargs)

    def get_mtype_cell_density(self,
                circuit_model,
                spatial_parameters=[],
                *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                circuit_model=circuit_model,
                method=composition_measurements.MtypeCellDensity(
                    circuit_model.bluepy_circuit,
                    *args, **kwargs),
                parameters=spatial_parameters,
                *args, **kwargs)

    def get_cell_ratio(self,
            circuit_model,
            spatial_parameters=[],
            *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                circuit_model=circuit_model,
                method=composition_measurements.CellRatio(
                    circuit_model.bluepy_circuit),
                parameters=spatial_parameters,
                *args, **kwargs)

    def get_inhibitory_synapse_density(self,
            circuit_model,
            spatial_parameters=[],
            *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                circuit_model=circuit_model,
                method=composition_measurements.InhibitorySynapseDensity(
                    circuit_model.bluepy_circuit),
                parameters=spatial_parameters,
                *args, **kwargs)

    def get_excitatory_synapse_density(self,
            circuit_model,
            spatial_parameters=[],
            *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                circuit_model=circuit_model,
                method=composition.ExcitatorySynapseDensity(
                    circuit_model.bluepy_circuit),
                parameters=spatial_parameters,
                *args, **kwargs)

    def get_synapse_density(self,
            circuit_model,
            spatial_parameters=[],
            *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                circuit_model=circuit_model,
                method=composition_measurements.ExtrinsicIntrinsicSynapseDensity(
                    circuit_model.bluepy_circuit),
                parameters=spatial_parameters,
                *args, **kwargs)

    def _get_pathways_permissible(self,
            is_permissible,
            pathways):
        """..."""
        def pathways_permissible(condition):
            """..."""
            pathway=(
                condition.get_value("pre_mtype"),
                condition.get_value("post_mtype"))
            return\
                is_permissible(condition) and\
                pathway in pathways

        return pathways_permissible

    def pathway_measurement(self,
            circuit_model,
            get_measurement_method,
            get_random_variate,
            parameters={},
            fill_missing_param_values=False,
            *args, **kwargs):
        """Meassure (mtype --> mtype) pathways.
        Arguments
        --------------
        pathways: List[Tuple(PreMtype, PostMtype)]"""
        pathways=\
            kwargs.get(
                "pathways", set())
        if not parameters:
             parameters=[
                 Mtype(
                     circuit=circuit_model.bluepy_circuit,
                     label="pre_mtype"),
                 Mtype(
                     circuit=circuit_model.bluepy_circuit,
                     label="post_mtype")]
        if pathways:
            kwargs["is_permissible"]=\
                self._get_pathways_permissible(
                    kwargs.get(
                        "is_permissible",
                        lambda condition: True),
                    pathways)
        return\
            self.statistical_measurement(
                circuit_model,
                method=get_measurement_method(
                    circuit=circuit_model.bluepy_circuit,
                    *args, **kwargs),
                get_random_variate=get_random_variate,
                parameters=parameters,
                fill_missing_param_values=fill_missing_param_values,
                *args, **kwargs)

    def get_pathway_synapse_count(self,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """Get statistics for number of synapses in a connection."""
        return\
            self.pathway_measurement(
                circuit_model,
                connectome_measurements.PairSynapseCount,
                get_random_variate=RandomConnectionVariate,
                parameters=parameters,
                *args, **kwargs)

    def get_pathway_connection_strength(self,
            circuit_model,
            parameters={},
            *args, **kwargs):
        """Measure the strength of connections in a (mtype->mtype) pathway."""
        return\
            self.pathway_measurement(
                circuit_model,
                connectome_measurements.ConnectionStrength,
                parameters=parameters,
                *args, **kwargs)

    def get_pathway_connection_count(self,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """Get statistical summary of the number of connections in a
        (mtype --> mtype) pathway.
        The analyzed phenomenon is essentially connection probability ---
        that is the probability that two neurons with given pre and post mtypes
        are connected.
        We have a separate method to directly compute connection probability
        without using the statistical measurement infrastructure used for
        this version...
        """
        return\
            self.pathway_measurement(
                circuit_model,
                connectome_measurements.PairConnection,
                get_random_variate=RandomPairs,
                parameters=parameters,
                *args, **kwargs)

    def get_pathway_connection_probability(self,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """Get pathway connection probability
        as a function of distance.
        """
        self.logger.debug(
            self.logger.get_source_info(),
            *["{}:{}".format(key, value) for key, value in kwargs.items()])
        upper_bound_soma_distance=\
            kwargs.get(
                "upper_bound_soma_distance", 250.)
        if not parameters:
            parameters=[
                AtlasRegion(
                    values=[circuit_model.representative_subregion]),
                Mtype(
                    circuit_model.bluepy_circuit,
                    label="pre_mtype"),
                Mtype(
                    circuit_model.bluepy_circuit,
                    label="post_mtype")]
        soma_distance_params=[
            param for param in parameters
            if param.label == "soma_distance"]
        assert len(soma_distance_params) <= 1
        by_distance=\
            len(soma_distance_params) == 1
        if not by_distance:
            soma_distance=\
                SomaDistance(0., 2 * upper_bound_soma_distance, 2)
            parameters.append(
                soma_distance)
        else:
            soma_distance=\
                soma_distance_params[0]
        self.logger.debug(
            self.logger.get_source_info(),
            "get pathway connection probability with parameter values",
            "region: {}".format(parameters[0].values),
            "pre_mtype: {}".format(parameters[1].values),
            "post_mtype: {}".format(parameters[2].values),
            "soma distance: {}".format(soma_distance.values))
        measurement=\
            self.pathway_measurement(
                circuit_model,
                connectome_measurements.PairConnection,
                get_random_variate=RandomPairs,
                parameters=parameters,
                distance_binner=soma_distance._binner,
                *args, **kwargs)
        if not by_distance:
            measurement.data=\
                measurement.data.xs(
                    (0., upper_bound_soma_distance),
                    level=soma_distance.label)
        return measurement

    def get_pathway_efferent_connection_count(self,
            circuit_model,
            parameters=[],
            upper_bound_soma_distance=100.,
            cache_size=None,
            *args, **kwargs):
        """Get number of outgoing connections in a pathway.
        For now, a cut-paste solution, will be cleaned up"""
        if not parameters:
            parameters=[
                AtlasRegion(
                    values=[circuit_model.representative_subregion]),
                Mtype(
                    circuit_model.bluepy_circuit,
                    label="pre_mtype"),
                Mtype(
                    circuit_model.bluepy_circuit,
                    label="post_mtype")]
        soma_distance_params=[
            param for param in parameters
            if param.label == "soma_distance"]
        assert len(soma_distance_params) <= 1
        by_distance=\
            len(soma_distance_params) == 1
        if not by_distance:
            soma_distance=\
                SomaDistance(0., 2 * upper_bound_soma_distance, 2)
            parameters.append(
                soma_distance)
        else:
            soma_distance=\
                soma_distance_params[0]
        self.logger.progress(
            self.logger.get_source_info(),
            "get pathway efferent connection count with parameter values",
            "region: {}".format(parameters[0].values),
            "pre_mtype: {}".format(parameters[1].values),
            "post_mtype: {}".format(parameters[2].values),
            "soma distance: {}".format(soma_distance.values))

        def __random_sample(gids):
            """..."""
            if len(gids) == 0:
                return np.array([])
            return\
                np.random.choice(gids, cache_size)\
                if cache_size else gids
                   
        region_label=\
            circuit_model.region_label
        XYZ=[
            Cell.X, Cell.Y, Cell.Z]
        empty_dataframe=\
            pd.DataFrame(
                [],
                columns=["mean", "std"])
        was_cached=\
            set()
        number_cells_mtype=\
            {}
        has_efferent_connections=\
            {}
        connection_counts=\
            {}

        def __get_distances(
                origin,
                cells):
            """..."""
            return\
                soma_distance._binner\
                .get_bins(
                    np.linalg.norm(
                        cells[XYZ].values - origin,
                        axis=1))

        def __get_efferent_mtype_counts(
                pre_gid,
                all_cells):
            """..."""
            origin=\
                all_cells.loc[pre_gid][XYZ]\
                         .values\
                         .astype(float)
            post_gids=\
                circuit_model\
                .connectome\
                .efferent_gids(pre_gid)
            post_cells=\
                all_cells\
                .reindex(post_gids)\
                .dropna()
            N = post_cells.shape[0]
            return\
                pd.DataFrame(
                    {"count": np.ones(N),
                     "post_mtype": post_cells[Cell.MTYPE].values,
                     "soma_distance": __get_distances(origin, post_cells)})\
                  .groupby(["post_mtype", "soma_distance"])\
                  .agg(sum)\
                  .dropna()

        def __add_to_cache(
                mtype,
                region,
                all_cells):
            """..."""
            cell_type={
                Cell.MTYPE: mtype}
            if region:
                cell_type[Cell.REGION]=\
                    region
            mtype_gids=\
                __random_sample(
                    all_cells.index[
                        all_cells[Cell.MTYPE].values == mtype])
            number_cells_mtype[mtype]=\
                len(mtype_gids)
            self.logger.progress(
                self.logger.get_source_info(),
                "cache {} mtype {} cells, region {}"\
                .format(
                    len(mtype_gids),
                    mtype,
                    region))
            if len(mtype_gids) > 0:
                has_efferent_connections[mtype]=\
                    True
                connection_counts[(region, mtype)]=\
                    pd.concat([
                        __get_efferent_mtype_counts(gid, all_cells)
                        for gid in mtype_gids])\
                      .groupby(["post_mtype", "soma_distance"])\
                      .agg(["mean", "std"])\
                      .dropna()\
                      ["count"]
            else:
                has_efferent_connections[mtype]=\
                    False
            was_cached.add(mtype)

        def __get_cell_type(
                mtype,
                region):
            """..."""
            return\
                {Cell.MTYPE: mtype,
                 region_label: region}\
                 if region else\
                    {Cell.MTYPE: mtype}

        def __get_pathway_efferent_connection_count(
                condition):
            """..."""
            self.logger.debug(
                self.logger.get_source_info(),
                "get pathway connection probability for condition {}"\
                .format(condition.value))
            region=\
                condition.get_value(
                    region_label)
            pre_mtype=\
                condition.get_value(
                    "pre_mtype")
            post_mtype=\
                condition.get_value(
                    "post_mtype")
            soma_distance=\
                condition.get_value(
                    "soma_distance")
            pre_cell_type=\
                __get_cell_type(
                    pre_mtype, region)
            post_cell_type=\
                __get_cell_type(
                    post_mtype, region)
            pathway=\
                (region, pre_mtype, post_mtype)
            all_cells=\
                circuit_model\
                  .cells\
                  .get(
                      group={region_label: region} if region else None,
                      properties=[Cell.MTYPE] + XYZ)
            if pre_mtype not in was_cached:
                __add_to_cache(
                    pre_mtype,
                    region,
                    all_cells)
            if not (region, pre_mtype) in connection_counts:
                return empty_dataframe
            try:
                dataframe=\
                    connection_counts[(region, pre_mtype)]
                return\
                    dataframe.xs(
                        (post_mtype, soma_distance),
                        level=("post_mtype", "soma_distance"))
            except KeyError as key_error:
                self.logger.alert(
                    self.logger.get_source_info(),
                    "KeyError {}".format(key_error),
                    "while looking for post_mtype {}, soma_distance{}"\
                    .format(
                        post_mtype,
                        soma_distance))
                return empty_dataframe

        def __get_parameter_values(
                condition ):
            """..."""
            region=\
                condition.get_value(
                    region_label)
            if not region:
                return(
                    "Any",
                    condition.get_value("pre_mtype"),
                    condition.get_value("post_mtype"),
                    condition.get_value("soma_distance"))
            return(
                region,
                condition.get_value("pre_mtype"),
                condition.get_value("post_mtype"),
                condition.get_value("soma_distance"))
        
        is_permissible=\
            self._get_pathways_permissible(
                kwargs.get(
                    "is_permissible",
                    lambda condition: True),
                kwargs.get(
                    "pathways",
                    set()))
        conditions = list(
            ConditionGenerator(
                parameters,
                is_permissible=is_permissible))
        self.logger.info(
            self.logger.get_source_info(),
            "Efferent connection count given {} conditions will be computed"\
            .format(len(conditions)))
        condition_dataframe_list=[
            (condition, __get_pathway_efferent_connection_count(condition))
            for condition in conditions]
        measurement=\
            pd.concat([
                dataframe for _, dataframe in condition_dataframe_list
                if not dataframe.empty])\
              .set_index(
                  pd.MultiIndex.from_tuples(
                      [__get_parameter_values(condition)
                       for condition, dataframe in condition_dataframe_list
                       if not dataframe.empty],
                      names=[
                          "region","pre_mtype","post_mtype","soma_distance"]))
        return\
            Record(
                phenomenon=Phenomenon(
                    "Pathway Efferent Connection Count",
                    "Number of efferent connections in an mtype-->mtype pathway.",
                    group="connectome"),
                label="in-silico",
                model_label=circuit_model.get_label(),
                model_uri=circuit_model.get_uri(),
                sampling_method="All pathway pairs and connections were used",
                sample_size=np.nan,
                measurement_method="""Pre-mtype cells were sampled randomly,
                and their efferent connections grouped by mtype and
                soma distance and counted.""",
                data=measurement,
                units="",
                parameter_groups=[p.label for p in parameters])


    def get_pathway_afferent_connection_count(self,
            circuit_model,
            parameters=[],
            upper_bound_soma_distance=100.,
            cache_size=None,
            *args, **kwargs):
        """Get number of outgoing connections in a pathway.
        For now, a cut-paste solution, will be cleaned up"""
        if not parameters:
            parameters=[
                AtlasRegion(
                    values=[circuit_model.representative_subregion]),
                Mtype(
                    circuit_model.bluepy_circuit,
                    label="pre_mtype"),
                Mtype(
                    circuit_model.bluepy_circuit,
                    label="post_mtype")]
        soma_distance_params=[
            param for param in parameters
            if param.label == "soma_distance"]
        assert len(soma_distance_params) <= 1
        by_distance=\
            len(soma_distance_params) == 1
        if not by_distance:
            soma_distance=\
                SomaDistance(0., 2 * upper_bound_soma_distance, 2)
            parameters.append(
                soma_distance)
        else:
            soma_distance=\
                soma_distance_params[0]
        self.logger.debug(
            self.logger.get_source_info(),
            "get pathway afferent connection count with parameter values",
            "region: {}".format(parameters[0].values),
            "pre_mtype: {}".format(parameters[1].values),
            "post_mtype: {}".format(parameters[2].values),
            "soma distance: {}".format(soma_distance.values))

        def __random_sample(gids):
            """..."""
            return\
                np.random.choice(gids, cache_size)\
                if cache_size else gids
                   
        region_label=\
            circuit_model.region_label
        XYZ=[
            Cell.X, Cell.Y, Cell.Z]
        empty_dataframe=\
            pd.DataFrame(
                [],
                columns=["mean", "std"])
        was_cached=\
            set()
        number_cells_mtype=\
            {}
        has_afferent_connections=\
            {}
        connection_counts=\
            {}

        def __get_distances(
                origin,
                cells):
            """..."""
            return\
                soma_distance._binner\
                .get_bins(
                    np.linalg.norm(
                        cells[XYZ].values - origin,
                        axis=1))

        def __get_afferent_mtype_counts(
                post_gid,
                all_cells):
            """..."""
            origin=\
                all_cells.loc[post_gid][XYZ]\
                         .values\
                         .astype(float)
            pre_gids=\
                circuit_model\
                .connectome\
                .afferent_gids(post_gid)
            pre_cells=\
                all_cells\
                .reindex(pre_gids)\
                .dropna()
            N = pre_cells.shape[0]
            return\
                pd.DataFrame(
                    {"count": np.ones(N),
                     "pre_mtype": pre_cells[Cell.MTYPE].values,
                     "soma_distance": __get_distances(origin, pre_cells)})\
                  .groupby(["pre_mtype", "soma_distance"])\
                  .agg(sum)\
                  .dropna()

        def __add_to_cache(
                mtype,
                region,
                all_cells):
            """..."""
            cell_type={
                Cell.MTYPE: mtype}
            if region:
                cell_type[Cell.REGION]=\
                    region
            mtype_gids=\
                __random_sample(
                    all_cells.index[
                        all_cells[Cell.MTYPE].values == mtype])
            number_cells_mtype[mtype]=\
                len(mtype_gids)
            self.logger.debug(
                self.logger.get_source_info(),
                "cache {} mtype {} cells, region {}"\
                .format(
                    len(mtype_gids),
                    mtype,
                    region))
            if len(mtype_gids) > 0:
                has_afferent_connections[mtype]=\
                    True
                connection_counts[(region, mtype)]=\
                    pd.concat([
                        __get_afferent_mtype_counts(gid, all_cells)
                        for gid in mtype_gids])\
                      .groupby(["pre_mtype", "soma_distance"])\
                      .agg(["mean", "std"])\
                      .dropna()\
                      ["count"]
            else:
                has_afferent_connections[mtype]=\
                    False
            was_cached.add(mtype)

        def __get_cell_type(
                mtype,
                region):
            """..."""
            return\
                {Cell.MTYPE: mtype,
                 region_label: region}\
                 if region else\
                    {Cell.MTYPE: mtype}

        def __get_pathway_afferent_connection_count(
                condition):
            """..."""
            self.logger.debug(
                self.logger.get_source_info(),
                "get pathway connection probability for condition {}"\
                .format(condition.value))
            region=\
                condition.get_value(
                    region_label)
            pre_mtype=\
                condition.get_value(
                    "pre_mtype")
            post_mtype=\
                condition.get_value(
                    "post_mtype")
            soma_distance=\
                condition.get_value(
                    "soma_distance")
            pre_cell_type=\
                __get_cell_type(
                    pre_mtype, region)
            post_cell_type=\
                __get_cell_type(
                    post_mtype, region)
            pathway=\
                (region, pre_mtype, post_mtype)
            all_cells=\
                circuit_model\
                  .cells\
                  .get(
                      group={region_label: region} if region else None,
                      properties=[Cell.MTYPE] + XYZ)
            if post_mtype not in was_cached:
                __add_to_cache(
                    post_mtype,
                    region,
                    all_cells)
            if not (region, post_mtype) in connection_counts:
                return empty_dataframe
            try:
                dataframe=\
                    connection_counts[
                        (region, post_mtype)]
                return\
                    dataframe.xs(
                        (pre_mtype, soma_distance),
                        level=("pre_mtype", "soma_distance"))
            except KeyError as key_error:
                self.logger.alert(
                    self.logger.get_source_info(),
                    "KeyError {}".format(key_error),
                    "while looking for pre_mtype {}, soma_distance{}"\
                    .format(
                        pre_mtype,
                        soma_distance))
                return empty_dataframe

        def __get_parameter_values(
                condition ):
            """..."""
            region=\
                condition.get_value(
                    region_label)
            if not region:
                return(
                    "Any",
                    condition.get_value("pre_mtype"),
                    condition.get_value("post_mtype"),
                    condition.get_value("soma_distance"))
            return(
                region,
                condition.get_value("pre_mtype"),
                condition.get_value("post_mtype"),
                condition.get_value("soma_distance"))
        
        is_permissible=\
            self._get_pathways_permissible(
                kwargs.get(
                    "is_permissible",
                    lambda condition: True),
                kwargs.get(
                    "pathways",
                    set()))
        conditions = list(
            ConditionGenerator(
                parameters,
                is_permissible=is_permissible))
        condition_dataframe_list=[
            (condition, __get_pathway_afferent_connection_count(condition))
            for condition in conditions]
        measurement=\
            pd.concat([
                dataframe for _, dataframe in condition_dataframe_list
                if not dataframe.empty])\
              .set_index(
                  pd.MultiIndex.from_tuples(
                      [__get_parameter_values(condition)
                       for condition, dataframe in condition_dataframe_list
                       if not dataframe.empty],
                      names=[
                          "region","pre_mtype","post_mtype","soma_distance"]))
        return\
            Record(
                phenomenon=Phenomenon(
                    "Pathway Efferent Connection Count",
                    "Number of efferent connections in an mtype-->mtype pathway.",
                    group="connectome"),
                label="in-silico",
                model_label=circuit_model.get_label(),
                model_uri=circuit_model.get_uri(),
                sampling_method="All pathway pairs and connections were used",
                sample_size=np.nan,
                measurement_method="""Pre-mtype cells were sampled randomly,
                and their efferent connections grouped by mtype and
                soma distance and counted.""",
                data=measurement,
                units="",
                parameter_groups=[p.label for p in parameters])

    def get_pathway_soma_distance(self,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """Get a statistical summary of the distance between cell somas."""
        return\
            self.pathway_measurement(
                circuit_model,
                connectome_measurements.SomaDistance,
                parameters=parameters,
                pathways=pathways,
                *args, **kwargs)

    def cell_group_measurement(self,
            circuit_model,
            get_measurement_method,
            parameters=[],
            *args, **kwargs):
        """Make (statistical) measurements of cell groups in a circuit."""
        if not parameters:
            parameters = [
                Mtype(circuit_model.bluepy_circuit)]
        return\
            self.statistical_measurement(
                circuit_model,
                method=get_measurement_method(
                    circuit=circuit_model.bluepy_circuit,
                    *args, **kwargs),
                get_random_variate=RandomCellVariate,
                parameters=parameters,
                *args, **kwargs)

    def get_cell_bouton_density(self,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """..."""
        return\
            self.cell_group_measurement(
                circuit_model,
                connectome_measurements.BoutonDensity,
                parameters=parameters,
                *args, **kwargs)

    def get_cell_interbouton_interval(self,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """Get a statistical summary of interbouton intervals"""
        return\
            self.cell_group_measurement(
                circuit_model,
                connectome_measurements.InterboutonInterval,
                parameters=parameters,
                *args, **kwargs)

    def get_cell_connection_count(
            circuit_model,
            connection_type=Direction.IN,
            parameters=[],
            *args, **kwargs):
        """Statistical summary of Afferent or Efferent connection count
        of cells in a group, specified by 'parameters'"""
        if connection_type not in {Direction.IN, Direction.OUT}:
            raise ValueError(
                "Unknown connection type {}".format(connection_type),
                "Please set connection_type to one of:\n\t 1.{}\n\t 2.{}"\
                .format(Direction.IN, Direction.OUT))
        get_measurement_method=\
            connectome_measurements.AfferentConnectionCount\
            if connection_type == Direction.IN else\
               connectome_measurements.EfferentConnectionCount
        return\
            self.cell_group_measurement(
                circuit_model,
                get_measurement_method,
                parameters=parameters,
                *args, **kwargs)

    def get_cell_synapse_count(
            circuit_model,
            connection_type=Direction.IN,
            parameters=[]):
        """..."""
        if connection_type not in {Direction.IN, Direction.OUT}:
            raise ValueError(
                "Unknown connection type {}".format(connection_type),
                "Please set connection_type to one of:\n\t 1.{}\n\t 2.{}"\
                .format(Direction.IN, Direction.OUT))
        get_measurement_method=\
            connectome_measurements.AfferentSynapseCount\
            if connection_type == Direction.IN else\
               connectome_measurements.EfferentSynapseCount
        return\
            self.cell_group_measurement(
                cirucit_model,
                get_measurement_method,
                parameters=parameters,
                *args, **kwargs)


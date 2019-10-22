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
                method=composition_measurements.ExcitatorySynapseDensity(
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

    def get_pathway_connection_probability_directly(self,
            circuit_model,
            parameters=[],
            pre_mtype_sample_size=100,
            post_cells_sample_size=100000,
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
        region_params=[
            param for param in parameters
            if param.label == "region"]
        assert len(region_params) == 1
        region_parameter=\
            region_params[0]
        assert len(region_parameter.values) == 1
        region=\
            region_parameter.values[0]
        pre_mtype_params=[
            param for param in parameters
            if param.label == "pre_mtype"]
        assert len(pre_mtype_params) == 1
        pre_mtype_parameter=\
            pre_mtype_params[0]
        post_mtype_params=[
            param for param in parameters
            if param.label == "post_mtype"]
        assert len(post_mtype_params) == 1
        post_mtype_parameter=\
            post_mtype_params[0]
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

        Cell.XYZ = [Cell.X, Cell.Y, Cell.Z]

        def _random_sample(
                size,
                mtype=None,
                with_gid=True):
            """..."""
            cell_type=\
                {Cell.MTYPE: mtype, Cell.REGION: region}\
                if mtype else\
                   {Cell.REGION: region}
            all_cells=\
                circuit_model.cells.get(
                    cell_type,
                    properties=[Cell.MTYPE] + Cell.XYZ)
            result=\
                all_cells if all_cells.shape[0] <= size\
                else all_cells.sample(size)
            return\
                result.assign(gid=result.index.values.astype(int))\
                if with_gid else result

        circuit_cells_sample=\
            _random_sample(
                size=post_cells_sample_size)\
                .rename(
                    columns={
                        Cell.MTYPE: "post_mtype",
                        "gid": "post_gid"})

        def _get_distances(origin):
            """..."""
            return\
                circuit_cells_sample\
                .assign(
                    soma_distance=soma_distance._binner.get_bins(
                        np.linalg.norm(
                            circuit_cells_sample[Cell.XYZ] - origin,
                            axis=1)),
                    post_gid=circuit_cells_sample.index)\
                [["post_mtype", "soma_distance", "post_gid"]]

        def _get_pre_gid_connectivity(pre_gid):
            """..."""
            pre_mtype=\
                circuit_model\
                .cells.get(pre_gid, properties=Cell.MTYPE)
            origin=\
                circuit_model\
                .cells.get(pre_gid, properties=Cell.XYZ)\
                .values.astype(float)
            distances=\
                _get_distances(origin)
            return\
                distances.assign(
                    connected=np.in1d(
                        distances["post_gid"].values.astype(int),
                        circuit_model.connectome.efferent_gids(pre_gid)))

        def _get_pre_mtype_connectivity(pre_mtype):
            """..."""
            self.logger.info(
                self.logger.get_source_info(),
                """compute pre mtype {} connectivity""".format(pre_mtype))
            pre_cells=\
                _random_sample(
                    size=pre_mtype_sample_size,
                    mtype=pre_mtype)
            pre_gid_connectivity=\
                pd.concat([
                    _get_pre_gid_connectivity(pre_gid)
                    for pre_gid in pre_cells.index.values])
            self.logger.debug(
                self.logger.get_source_info(),
                """found\n {} """.format(pre_gid_connectivity.head()),
                "of shape {}".format(pre_gid_connectivity.shape))
            post_mtypes=list(sorted(
                set(post_mtype_parameter.values)\
                .intersection(
                    pre_gid_connectivity["post_mtype"].unique())))
            result=\
                pre_gid_connectivity[
                    ["post_mtype", "soma_distance", "connected"]]\
                .set_index("post_mtype")\
                .loc[post_mtypes]\
                .groupby(["post_mtype", "soma_distance"])\
                .agg(["size", "mean", "std"])\
                ["connected"]
            self.logger.debug(
                self.logger.get_source_info(),
                "result ",
                "{}".format(result))
            return result

        pre_post_mtype_connectivity=\
            pd.concat(
                [_get_pre_mtype_connectivity(pre_mtype)
                 for pre_mtype in pre_mtype_parameter.values],
                keys=pre_mtype_parameter.values,
                names=["pre_mtype"])
        region_connectivity=\
            pd.concat(
                [pre_post_mtype_connectivity],
                keys=[region],
                names=["region"])
        measurement=\
            pd.concat(
                [region_connectivity if by_distance\
                 else region_connectivity.xs(
                         (0., upper_bound_soma_distance),
                         level="soma_distance")],
                axis=1,
                keys=["in-silico"])
                
        return\
            Record(
                phenomenon=Phenomenon(
                    "Pathway Connection Probability",
                    "Probability of connections in an mtype-->mtype pathway.",
                    group="connectome"),
                label="in-silico",
                model_label=circuit_model.get_label(),
                model_uri=circuit_model.get_uri(),
                sampling_method="All pathway pairs and connections were used",
                sample_size=np.nan,
                measurement_method="Please fill in",
                data=measurement,
                units="",
                parameter_groups=[p.label for p in parameters])

             


            


    def get_pathway_efferent_connection_count(self,
            circuit_model,
            parameters=[],
            upper_bound_soma_distance=100.,
            cache_size=None,
            default_value=0.0,
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
                  .fillna(0.)

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
                      .fillna(0.)\
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

        def __get_default(
                post_mtype,
                soma_distance):
            """..."""
            return\
                pd.DataFrame(
                    [{"mean": 0., "std": 0.}],
                    index=pd.MultiIndex.from_tuples(
                        [(post_mtype, soma_distance)],
                        names=[
                            "post_mtype","soma_distance"]))
                               
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
                return __get_default(
                    post_mtype, soma_distance)
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
                return __get_default(
                    post_mtype, soma_distance)

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
        non_empty_dataframes=[
            dataframe for _, dataframe in condition_dataframe_list
            if not dataframe.empty]
        if len(non_empty_dataframes) > 0:
            measurement=\
                pd.concat(
                    non_empty_dataframes)\
                  .set_index(
                      pd.MultiIndex.from_tuples(
                          [__get_parameter_values(condition)
                           for condition, dataframe in condition_dataframe_list
                           if not dataframe.empty],
                          names=[
                              "region",
                              "pre_mtype",
                              "post_mtype",
                              "soma_distance"]))
        else:
            measurement=\
                empty_dataframe

        return\
            Record(
                phenomenon=Phenomenon(
                    "Pathway Efferent Connection Count",
                    "Number of efferent connections in an mtype-->mtype pathway.",
                    group="connectome"),
                label="in-silico",
                model_label=circuit_model.get_label(),
                model_uri=circuit_model.get_uri(),
                sampling_method="""A sample of pre-gids with a specified
                pre-mtype was used. For each pre-gid all of its efferent gids
                were grouped by their mtype and soma distances, and counted""",
                sample_size=cache_size,
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
            default_value=0.,
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
                if len(gids) > 0 and cache_size else gids
                   
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
                  .fillna(0.)

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

        def __get_default(
                pre_mtype,
                soma_distance):
            """..."""
            return\
                pd.DataFrame(
                    [{"mean": 0., "std": 0.}],
                    index=pd.MultiIndex.from_tuples(
                        [(pre_mtype, soma_distance)],
                        names=[
                            "pre_mtype","soma_distance"]))
                               

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
                return __get_default(
                    pre_mtype, soma_distance)
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
                    """while looking for pre_mtype {},
                    post_mtype {}, soma_distance{}"""\
                    .format(
                        pre_mtype,
                        post_mtype,
                        soma_distance))
                return __get_default(
                    pre_mtype, soma_distance)

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
        non_empty_dataframes=[
            dataframe for _, dataframe in condition_dataframe_list
            if not dataframe.empty]
        if len(non_empty_dataframes) > 0:
            measurement=\
                pd.concat(
                    non_empty_dataframes)\
                  .set_index(
                      pd.MultiIndex.from_tuples(
                          [__get_parameter_values(condition)
                           for condition, dataframe in condition_dataframe_list
                           if not dataframe.empty],
                          names=[
                              "region",
                              "pre_mtype",
                              "post_mtype",
                              "soma_distance"]))
        else:
            measurement=\
                empty_dataframe
        return\
            Record(
                phenomenon=Phenomenon(
                    "Pathway Afferent Connection Count",
                    "Number of afferent connections in an mtype-->mtype pathway.",
                    group="connectome"),
                label="in-silico",
                model_label=circuit_model.get_label(),
                model_uri=circuit_model.get_uri(),
                sampling_method="""A sample of post-gids with a specified
                post-mtype was used. For each post-gid all of its afferent gids
                were grouped by their mtype and soma distances, and counted""",
                sample_size=cache_size,
                measurement_method="""Pre-mtype cells were sampled randomly,
                and their efferent connections grouped by mtype and
                soma distance and counted.""",
                data=measurement,
                units="",
                parameter_groups=[p.label for p in parameters])


    def get_pathway_afferent_connection_count_by_distance(
            self,
            circuit_model,
            parameters, #for now you have to send in parameters
            cache_sisze=None,
            default_value=0.,
            *args, **kwargs):
        """Afferent connection, by distance, explicitly"""

        soma_distance_params=[
            param for param in parameters
            if param.label == "soma_distance"]
        assert len(soma_distance_params) <= 1
        soma_distance_parameter=\
            soma_distance_params[0]
        pre_mtype_params=[
            param for param in parameters
            if param.label == "pre_mtype"]
        assert len(pre_mtype_params) <= 1
        pre_mtype_parameter=\
            pre_mtype_params[0]
        post_mtype_params=[
            param for param in parameters
            if param.label == "post_mtype"]
        assert len(post_mtype_params) <= 1
        post_mtype_parameter=\
            post_mtype_params[0]
        region_params=[
            param for param in parameters
            if param.label == "region"]
        assert len(region_params) <= 1
        region_parameter=\
            region_params[0]
        assert len(region_parameter.values) == 1

        def __random_sample(gids):
            """..."""
            return\
                np.random.choice(gids, cache_size)\
                if len(gids) > 0 and cache_size else gids
                   
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
                soma_distance_parameter._binner\
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
                  .fillna(0.)

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
                      .fillna(0.)\
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


        default_dataframe=\
            pd.DataFrame(
                {"mean":[
                    default_value
                    for _ in pre_mtype_parameter.values
                    for _ in soma_distance_parameter.values],
                 "std":[
                     default_value
                     for _ in pre_mtype_parameter.values
                     for _ in soma_distance_parameter.values]},
                index=pd.MultiIndex.from_tuples(
                    [(pre_mtype, distance)
                     for pre_mtype in pre_mtype_parameter.values
                     for distance in soma_distance_parameter.values],
                    names=["pre_mtype","soma_distance"]))

        def __get_mtype_afferent_connection_count(
                condition):
            """..."""
            self.logger.debug(
                self.logger.get_source_info(),
                "get pathway connection probability for condition {}"\
                .format(condition.value))
            region=\
                condition.get_value(
                    region_label)
            post_mtype=\
                condition.get_value(
                    "post_mtype")
            post_cell_type=\
                __get_cell_type(
                    post_mtype, region)
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
                return default_dataframe
            try:
                return\
                    connection_counts[
                        (region, post_mtype)]
            except KeyError as key_error:
                self.logger.alert(
                    self.logger.get_source_info(),
                    "KeyError {}".format(key_error),
                    """while looking for post_mtype {}"""\
                    .format(
                        post_mtype))
                return default_dataframe

        def __append_to_index(
                dataframe_index_tuples,
                condition):
            """condition should have only region and post_mtype"""
            region=\
                condition.get_value(
                    region_label)
            post_mtype=\
                condition.get_value(
                    "post_mtype")
            return\
                pd.MultiIndex.from_tuples(
                    [(region, pre_mtype, post_mtype, soma_distance)
                     for pre_mtype, soma_distance in dataframe_index_values],
                    names=["region","pre_mtype","post_mtype","soma_distance"])
        
        is_permissible=\
            self._get_pathways_permissible(
                kwargs.get(
                    "is_permissible",
                    lambda condition: True),
                kwargs.get(
                    "pathways",
                    set()))
        conditions_full = list(
            ConditionGenerator(
                [region_parameter, pre_mtype_parameter, post_mtype_parameter],
                is_permissible=is_permissible))
        condition_dataframe_list=[
            (condition, __get_mtype_afferent_connection_count(condition))
            for condition in conditions]
        if all(dataframe.empty for _,dataframe in condition_dataframe_list):
            measurement=\
                empty_dataframe
        else:
            measurement=\
                pd.concat([
                    dataframe for _, dataframe in condition_dataframe_list
                    if not dataframe.empty])\
                  .set_index(
                      pd.MultiIndex.from_tuples(
                          [index_tuple
                           for index_tuple in __append_to_index(
                                   dataframe.index.values, condition)
                           for condition, dataframe in condition_dataframe_list
                           if not dataframe.empty],
                          names=[
                              "region",
                              "pre_mtype",
                              "post_mtype",
                              "soma_distance"]))
        return\
            Record(
                phenomenon=Phenomenon(
                    "Pathway Afferent Connection Count",
                    "Number of afferent connections in an mtype-->mtype pathway.",
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


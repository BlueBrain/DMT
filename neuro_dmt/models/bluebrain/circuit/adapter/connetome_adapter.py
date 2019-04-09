"""An adapter specialized to compute connectome properties efficiently."""

from neuro_dmt.models.bluebrain.circuit.adapter\
    import *

class BlueBrainModelConnectomeAdapter(
        BlueBrainModelAdapter):
    """BlueBrainModelAdapter specialized for the connectome,
    for efficiency. A direct computation will make for efficiency."""

    def get_pathway_connection_probability(self,
            circuit_model,
            parameters=[],
            is_permissible=lambda condition: True,
            cache_size=None,
            upper_bound_soma_distance=300,#um
            *args, **kwargs):
        """Pathway connection probability between cells at a soma distance
        less than 'upper_bound_soma_distance'.
        """
        if not parameters:
            parameters=[
                AtlasRegion(
                    values=[circuit_model.representative_subregion]),
                Mtype(
                    circuit_model.bluepy.circuit,
                    label="pre_mtype"),
                Mtype(
                    circuit_model.bluepy.circuit,
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
        region_label=\
            circuit_model.region_label

        pathways=\
            kwargs.get(
                "pathways", set())
        kwargs["is_permissible"]=\
            self._get_pathways_permissible(
                is_permissible,
                pathways)\
                if pathways else\
                   is_permissible

        def __random_sample(gids):
            """..."""
            if not cache_size or len(gids) < cache_size:
                return gids
            return\
                np.random.choice(
                    gids, cache_size)

        XYZ=[
            Cell.X, Cell.Y, Cell.Z]
        empty_dataframe=\
            pd.DataFrame(
                [],
                columns=["mean", "std"])
        was_cached=\
            set()
        connection_counts_pathway=\
            {}
        number_cells_mtype=\
            {}
        possible_post_mtype_counts=\
            {}
        has_efferent_connections=\
            {}
        def __filter_close_by(
                origin,
                cells):
            """..."""
            positions=\
                cells[XYZ].values
            distances=\
                np.linalg.norm(
                    positions - origin,
                    axis=1)
            close_by=\
                distances < upper_bound_soma_distance
            self.logger.debug(
                self.logger.get_source_info(),
                "Filter close by to {}.".format(origin),
                "distance: ({} {}]".format(
                    np.nanmin(distances[close_by]),
                    np.nanmax(distances[close_by])))
            return cells.index[close_by].values

        def __add_to_cache(
                mtype,
                region,
                all_cells):
            """Cache connection data for 'mtype'"""
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
            if len(mtype_gids) == 0:
                has_efferent_connections[mtype]=\
                    False
                return
            possible_efferent_gids={
                gid: __filter_close_by(
                    all_cells[XYZ].loc[gid].values,
                    all_cells)
                for gid in mtype_gids}
            possible_post_mtype_counts[mtype]=\
                all_cells[Cell.MTYPE]\
                  .loc[
                      np.hstack(list(
                          possible_efferent_gids.values()))]\
                  .value_counts()\
                  .to_dict()
            actual_efferent_gids={
                gid: possible[
                    np.in1d(
                        possible,
                        circuit_model.connectome.efferent_gids(gid))]
                for gid, possible in possible_efferent_gids.items()}
            actual_post_mtype_counts=\
                all_cells[Cell.MTYPE]\
                  .loc[
                      np.hstack(list(
                          actual_efferent_gids.values()))]\
                  .value_counts()\
                  .to_dict()
            number_connections=\
                np.sum(list(
                    actual_post_mtype_counts.values()))
            if number_connections == 0:
                has_efferent_connections[mtype]=\
                    False
                return
            else:
                has_efferent_connections[mtype]=\
                    True
            connection_counts_pathway.update({
                (region, mtype, post_mtype): count
                for post_mtype, count in actual_post_mtype_counts.items()})
            was_cached.add(
                mtype)
            return

        def __get_cell_type(
                mtype,
                region):
            """..."""
            return\
                {Cell.MTYPE: mtype,
                 region_label: region}\
                 if region else\
                    {Cell.MTYPE: mtype}

        def __get_pathway_connection_probability(
                condition):
            """..."""
            self.logger.debug(
                self.logger.get_source_info(),
                "get pathway connection probability for condition {}"\
                .format(condition.value))
            pre_mtype=\
                condition.get_value(
                    "pre_mtype")
            post_mtype=\
                condition.get_value(
                    "post_mtype")
            region=\
                condition.get_value(
                    region_label)
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
            number_pairs=\
                possible_post_mtype_counts[pre_mtype][post_mtype]
            if number_pairs == 0:
                self.logger.info(
                    self.logger.get_source_info(),
                    "no efferent connections from {}"\
                    .format(
                        pre_mtype))
                return\
                    pd.Series({
                        "mean": 0.,
                        "std": 1. / np.sqrt(number_pairs)})
            number_connections=\
                connection_counts_pathway.get(pathway, 0)
            self.logger.debug(
                self.logger.get_source_info(),
                "condition {}".format(condition.value),
                "found number of pairs {}".format(number_pairs),
                "found number of connections {}".format(number_connections))
            probability_mean=\
                number_connections / number_pairs
            probability_var=\
                    probability_mean * (1. - probability_mean)
            return\
                pd.Series({
                    "mean": probability_mean,
                    "std": np.sqrt(probability_var/number_pairs)})

        def __get_parameter_values(
                condition):
            """..."""
            region=\
                condition.get_value(
                    region_label)
            if region:
                return(
                    region,
                    condition.get_value("pre_mtype"),
                    condition.get_value("post_mtype"))
            return(
                condition.get_value("pre_mtype"),
                condition.get_value("post_mtype"))
        conditions = list(
            ConditionGenerator(
                parameters,
                is_permissible=is_permissible))
        measurement=\
            pd.DataFrame(
                [__get_pathway_connection_probability(condition)
                 for condition in conditions],
                index=pd.MultiIndex.from_tuples(
                    tuples=[__get_parameter_values(condition)
                            for condition in conditions],
                    names=["region", "pre_mtype", "post_mtype"]))
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
                measurement_method="Pairs with theirs somas within {}um "
                "of each other were sampled. Probability was defined as "
                "#(pathway connections) / #(pathway pairs)"\
                .format(upper_bound_soma_distance),
                data=measurement,
                units="",
                parameter_groups=[p.label for p in parameters])


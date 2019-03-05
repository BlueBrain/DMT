"""A random parameter is just another parameter that can generate
random values."""

from abc import ABC, abstractmethod
import copy
import numpy as np
import pandas as pd
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.condition import Condition, ConditionGenerator
from dmt.vtk.utils import collections
from dmt.vtk.utils.collections import Record, take
from dmt.vtk.utils.logging import Logger, with_logging
from dmt.vtk.utils.descriptor import WithFCA


@with_logging(Logger.level.STUDY)
class RandomVariate(
        WithFCA,
        ABC):
    """Like a Parameter, but yields random values.
    """
    label = Field(
        __name__ = "label",
        __type__ = str,
        __is_valid_value__ = lambda instance, value: ' ' not in value,
        __doc__ = """Label for the random variable generated. May be used as a
        keyword for passing parameters to measurement methods.""")
    
    value_type = Field(
        __name__ = "value_type",
        __type__ = type,
        __doc__  = """Type of the variable generated by this
        RandomParameter.""")
    
    def __init__(self,
            *args, **kwargs):
        self.logger.inform(
            "initialize {} with kwargs: {}"\
            .format(self.__class__.__name__, kwargs))
        super().__init__(
            *args, **kwargs)

    def values(self,
            *args, **kwargs):
        """Returns a generator."""
        pass

    def repr(self,
            value):
        """Represent value 'value' of this random variate.
        Override if you wish to."""
        assert(
            isinstance(value, self.value_type))
        return str(value)

    @abstractmethod
    def sampling_method():
        """describe the sampling method."""
        raise NotImplementedError()


class ConditionedRandomVariate(
        RandomVariate):
    """RandomVariate conditioned on other variables."""
    condition_type=\
        Field(
            __name__="condition_type",
            __type__=Record,
            __default__=Record(),
            __doc__="""Record mapping field names to their types. The default
            value of a blank can be overridden using the 'given' method.""",
            __examples__=[Record(layer=int, target=str)] )
    reset_condition_type=\
        Field(
            __name__="reset_condition_type",
            __type__=bool,
            __default__=False,
            __doc__="""Should the condition type be reset to the type of the
            conditioning variables? If set to true, this will allow changing
            the condition type used with the random variate. However, a value
            of False constrains the random variate to accept the type set
            at initialization.""")
    columns=\
        Field(
            __name__="columns",
            __typecheck__=Field.typecheck.either(list, pd.Index),
            __doc__="""Columns of the dataframe generated
            by this random variate""")

    def __init__(self,
            conditions=None,
            *args, **kwargs):
        """Initialize this class with a 'values' parameter, or
        implement a 'values' method in a subclass.

        Parameters
        ------------------------------------------------------------------------
        label :: String
        """
        self._conditions=\
            conditions
        super().__init__(
            *args, **kwargs)

    @property
    def conditions(self):
        """..."""
        return self._conditions

    def is_valid(self,
            condition_generator):
        """..."""
        try: 
            fields = self.condition_type.fields
        except AttributeError:
            return False
        return(
            all(
                f in condition_generator.labels
                for f in fields )
            and all(
                issubclass(
                    condition_generator.value_type(f),
                    self.condition_type.get(f))
                for f in fields))

    def __with_condition_generator(self,
            condition_generator):
        """..."""
        instance=\
            copy.copy(self)
        instance._conditions=\
            condition_generator
        return instance

    def __with_condition_type(self,
            condition_type):
        """..."""
        instance=\
            copy.copy(self)
        instance.condition_type= \
            condition_type
        return instance

    def given(self,
            *conditioning_vars,
            is_permissible=lambda condition: True,
            **kwargs):
        """Set the condition type.
        This method can be used to reset the condition type accepted
        by this random variate. This feature allows us to pass any kind
        of Condition to this random variate's call method. This behavior is
        appropriate when values of the random variate are """
        if not conditioning_vars:
            self.logger.info(
                self.logger.get_source_info(),
                "no variables passed to condition {} instance with"\
                .format(self.__class__.__name__))
            return self

        l = len(conditioning_vars)
        self.logger.debug(
            "conditioning_vars length {}".format(l))
        if l == 1:
            self.logger.debug(
                self.logger.get_source_info(),
                "conditioning_vars{}"\
                .format(conditioning_vars))
            if collections.check(conditioning_vars):
                conditioning_vars=\
                    tuple(v for v in conditioning_vars[0])
            else:
                conditioning_vars=\
                    (conditioning_vars[0],)
        self.logger.debug(
            self.logger.get_source_info(),
            "conditioning_vars: {}".format(conditioning_vars))
        if self.reset_condition_type:
            self.condition_type \
                = Record(
                    **{v.label: v.value_type for v in conditioning_vars})
        for variable in conditioning_vars:
            if variable.label not in self.condition_type.fields:
                raise AttributeError(
                    """Illegal conditioning variable {}.\n
                    Variable {} does not appear in
                    {} instance condition_type."""\
                    .format(variable.label,
                            variable.label,
                            self.__class__.__name__))
            if not issubclass(variable.value_type,
                              self.condition_type.get(
                                  variable.label)):
                raise AttributeError(
                    """Unsupported type for conditioning variable {} 
                    in {} instance condition_type."""\
                    .format(variable.label,
                            self.__class__.__name__))
        return\
            self.__with_condition_generator(
                ConditionGenerator(
                    conditioning_vars,
                    is_permissible=is_permissible))

    def conditioned_values(self,
            condition,
            *args, **kwargs):
        """Yield random values of this RandomVariate
        for given conditions."""
        while True:
            value = self(condition)
            if value is None:
                break
            yield value

    @abstractmethod
    def __call__(self,
            condition,
            *args, **kwargs):
        pass

    def __iter__(self):
        """Iterate over me."""
        if not self._conditions:
            raise ValueError(
                "Conditions not set for this {} instance"\
                .format(self.__class__))
        while True:
            for condition in self._conditions:
                value = self.__call__(condition)
                if value is None:
                    break
                yield value
        
    def row(self,
        condition,
        value):
        """..."""
        return pd.DataFrame(
            [value],
            columns=self.columns,
            index=condition.index)

    def kwargs(self,
            condition,
            *args, **kwargs):
        """..."""
        return {
            self.label: self(
                condition,
                *args, **kwargs) }

    def sample_one(self,
            condition,
            size=20):
        """sample one"""
        values=\
            take(
                size,
                self.conditioned_values(
                    condition))
        df_list=[
            self.row(condition, value)
            for value in values]
        if len(df_list) == 0:
            return\
                pd.DataFrame(
                    [],
                    columns=self.columns)
        return\
            pd.concat(
                df_list)
                          
    def sample(self,
            conditions=None,
            size=20,
            *args, **kwargs):
        """..."""
        conditions\
            = conditions if conditions else self._conditions
        if conditions is None:
            self.logger.warn(
                self.logger.get_source_info(),
                """No condition generator, will pass empty conditions,
                that should be interpreted as no conditions.""")
            conditions = {}
        if not self.is_valid(conditions):
            self.logger.warn(
                self.logger.get_source_info(),
                """Invalid condition generator.
                Please provide one that produces conditions of type:\n {}"""\
                .format(self.condition_type))
            return None
        dataframes_for_conditions=[
            self.sample_one(condition, size=size)
            for condition in conditions]
        if len(dataframes_for_conditions) == 0:
            return pd.DataFrame([])
        return\
            pd.concat(
                dataframes_for_conditions)


    def transform(self,
            mapping):
        """Transform this ConditionedRandomVariate by transforming its value
        outputs."""
        modified\
            = copy.deepcopy(self)
        def __conditioned_values(
            condition,
            *args, **kwargs):
            """..."""
            for v in self.conditioned_values(
                    condition,
                    *args, **kwargs):
                yield mapping.function(v)

        modified.label\
            = mapping.label
        modified.conditioned_values\
            = conditioned_values
        return modified


def get_conditioned_random_variate(
        conditioning_variables,
        random_variate,
        *args, **kwargs):
    """Creates a class instance on the fly."""
    kwargs.update(dict(
        conditioning_variables=conditioning_variables,
        label=random_variate.label))
    middle_name\
        = "".join(
            w.capitalize()
            for w in random_variate.label.split('_'))
    full_name\
        = "Conditioned{}RandomVariate".format(
            middle_name)
    ancestors\
        = (ConditionedRandomVariate,
           random_variate.__class__,)
    T = type(
        full_name,
        ancestors,
        {} )
    return T(*args, **kwargs)

                                         

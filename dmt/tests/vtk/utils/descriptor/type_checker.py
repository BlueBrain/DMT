"""Test develop Field type checking"""

from abc import ABC, abstractmethod
from dmt.vtk.utils.descriptor import Field, WithFCA
from dmt.vtk.utils.logging import Logger, with_logging
from dmt.tests import ExceptionalTest

logger = Logger(__name__, level=Logger.level.STUDY)

class TestFieldType(WithFCA):
    """..."""
    value_type = int
    order_type = str
    field_one = Field(
        __name__="field_one",
        __type__=list,
        __is_valid__= Field.typecheck.collection(value_type),
        __doc__="Collection of type"
    )
    field_two = Field(
        __name__="field_two",
        __type__=set,
        __is_valid__=Field.typecheck.collection("value_type"),
        __doc__="Collection of type specified by this Test's 'value_type' attribute."

    )
    field_three = Field(
        __name__="field_three",
        __type__=dict,
        __is_valid__ = Field.typecheck.mapping(value_type, order_type),
        __doc__="check type of mapping"
    )
    field_four = Field(
        __name__="field_four",
        __type__=dict,
        __is_valid__=Field.typecheck.mapping("value_type", "order_type"),
        __doc__="check type of mapping"
    )
    optional_field = Field.Optional(
        __name__ = "optional_field",
        __type__=dict,
        __doc__="To test that WithFCA tolerates optional fields."
    )
    default_field = Field(
        __name__ = "default_field",
        __type__ = int,
        __doc__ = "To test a field is set to its default value.",
        __default__=1
    )
    def __init__(self, f1=[], f2=set([1,2]), f3={}, f4={}, **kwargs):
        """..."""
        self.field_one = f1
        self.field_two = f2
        self.field_three = f3
        #self.field_four = f4
        kwargs.update({"field_four": f4})
        super(TestFieldType, self).__init__(**kwargs)

    
def test1():
    """We can initialize a 'TestFieldType' without arguments"""
    t = TestFieldType()
    assert t.field_one == []
    assert t.field_two == set([1,2])
    assert t.field_three == {}
    assert t.field_four == {}

ExceptionalTest(test1, source_info=logger.get_source_info()).run()

def test2():
    """We can initiaize a 'TestFieldType' with argument f1 as a list of ints"""
    t = TestFieldType(f1=[1])
    assert t.field_one == [1]
    assert t.field_two == set([1,2])
    assert t.field_three == {}
    assert t.field_four == {}

ExceptionalTest(test2, source_info=logger.get_source_info()).run()

def test3():
    """We can initiaize a 'TestFieldType' with a set of ints"""
    t = TestFieldType(f2=set([1,2,3]))
    assert t.field_one == []
    assert t.field_two == set([1,2,3])
    assert t.field_three == {}
    assert t.field_four == {}

ExceptionalTest(test3, source_info=logger.get_source_info()).run()

def test4():
    """We cannot initialize a 'TestFieldType' with a dict of mixed types"""
    try:
        TestFieldType(f3={1: "one", "two": 2})
    except TypeError as e:
        pass

ExceptionalTest(test4, source_info=logger.get_source_info()).run()

def test5():
    """We can initialize a 'TestFieldType' as a dict of int->str"""
    f4 = {1: "one", 2: "two"}
    t = TestFieldType(f4=f4)
    assert t.field_one == []
    assert t.field_two == set([1,2])
    assert t.field_three == {}
    assert t.field_four == f4

ExceptionalTest(test5, source_info=logger.get_source_info()).run()

def test_default():
    """We can set default value for a field."""
    tyes = TestFieldType()
    assert tyes.default_field == 1
    tno  = TestFieldType(default_field=2)
    assert tno.default_field == 2, "default_field is {}".format(tno.default_field)

ExceptionalTest(test_default, source_info=logger.get_source_info()).run()

def test_optional():
    """We do not have to set an optional field."""
    t = TestFieldType()
    assert not hasattr(t, "optional_field")

ExceptionalTest(test_optional, source_info=logger.get_source_info()).run()


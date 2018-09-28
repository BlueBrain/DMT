"""Test develop Field type checking"""

from abc import ABC, abstractmethod
from dmt.vtk.utils.descriptor import Field, WithFCA
from dmt.vtk.utils.logging import Logger, with_logging

logger = Logger(__name__, level=Logger.level.STUDY)

@with_logging(Logger.level.TEST)
class Test:
    """..."""
    def __init__(self, test, source_info=None):
        """..."""
        self._test = test
        self._test_info = "TEST {}: \n\t{}".format(test.__name__, test.__doc__)
        self._source_info = "at {}".format(source_info) if source_info else ""

    def run(self, *args, **kwargs):
        """..."""
        try:
            self._test(*args, **kwargs)
        except Exception as e:
            self.logger.failure(self._test_info,
                                self._source_info,
                                "Exception {}:\n".format(e.__class__.__name__),
                                "\t{}".format(e))
            raise e
        self.logger.success(self._test_info)


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

    def __init__(self, f1=[], f2=set([1,2]), f3={}, f4={}):
        """..."""
        self.field_one = f1
        self.field_two = f2
        self.field_three = f3
        self.field_four = f4

    
def test1():
    """We can initialize a 'TestFieldType' without arguments"""
    TestFieldType()

Test(test1, source_info=logger.get_source_info()).run()

def test2():
    """We can initiaize a 'TestFieldType' with argument f1 as a list of ints"""
    TestFieldType(f1=[1])

Test(test2, source_info=logger.get_source_info()).run()

def test3():
    """We can initiaize a 'TestFieldType' with a set of ints"""
    TestFieldType(f2=set([1,2,2]))

Test(test3, source_info=logger.get_source_info()).run()

def test4():
    """We cannot initialize a 'TestFieldType' with a dict of mixed types"""
    try:
        TestFieldType(f3={1: "one", "two": 2})
    except TypeError as e:
        pass

Test(test4, source_info=logger.get_source_info()).run()

def test5():
    """We can initialize a 'TestFieldType' as a dict of int->str"""
    TestFieldType(f4={1: "one", 2: "two"})
    #TestFieldType(f4={1: 1, 2: 2})

Test(test5, source_info=logger.get_source_info()).run()

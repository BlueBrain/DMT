"""
Test develop class attribute
"""

from dmt.v2.tk.field import\
    Field,\
    ClassAttribute,\
    WithFields

class InstanceRepo(WithFields):
    """An instance repository knows about all its instances."""

    __mixin_repo__ = ClassAttribute(
        set(),
        """A list of all the classes that mix in InstanceRepo""")
    __instance_repo__ = ClassAttribute(
        __doc__="""A list of instances of classes that mix InstanceRepo in.""",
        __value__=[])

    index = Field(
        __doc__ = "An index to test Field initialization",
        __type__ = int)

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)
        cls = self.__class__
        cls.__mixin_repo__.add(cls)
        cls.__instance_repo__.append(self)


class Example(InstanceRepo):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)


def test_initialization():
    """
    Initialization of a class with ClassAttributes
    """
    eg0 = Example(index=0)
    assert len(eg0.__mixin_repo__) == 1
    assert "Example" in {cls.__name__ for cls in eg0.__mixin_repo__}
    assert len(eg0.__instance_repo__) == 1
    assert eg0.__instance_repo__[0].index == 0
    eg1 = Example(index=1)
    assert len(eg0.__mixin_repo__) == 1
    assert "Example" in {cls.__name__ for cls in eg1.__mixin_repo__}
    assert len(eg1.__instance_repo__) == 2
    assert eg1.__instance_repo__[1].index == 1

    try:
        eg0.__mixin_repo__ = []
        raise Exception(
            "A class attribute set from an instance",
            error)
    except Exception as error:
        pass

    for _ in range(10):
        ir = eg1.__description__["__instance_repo__"]
        assert\
            ir == "ClassAttribute<A list of instances of classes that mix InstanceRepo in.>"
        mr = eg1.__description__["__mixin_repo__"]
        assert\
            mr == "ClassAttribute<A list of all the classes that mix in InstanceRepo>"
        ix = eg1.__description__["index"]
        assert\
            ix == "Field<An index to test Field initialization>"

    print("PASS")

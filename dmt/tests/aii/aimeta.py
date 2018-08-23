"""Test class AIMeta"""

from dmt.aii import AIMeta, AIBase, adaptermethod

def test(description):
    print("""TEST:
    {}""".format(description))

class AIMetaTest(metaclass=AIMeta):
    """If this class declaration did not cause an error,
    it means that its metaclass could be AIMeta
    even if there were no adapter methods.
    """
    test(__doc__)
    pass

print("NEXT")
class AIBaseTest(AIBase):
    """If this class declaration did not cause an error,
    it means that it could have a concrete AIBase (sub-)class
    even if there were no adaptermethods in it!"""
    test(__doc__)
    pass


class AIMetaTestWithMethods(metaclass=AIMeta):
    """This class declaration should not cause any errors,
    or warnings."""
    test(__doc__)

    @adaptermethod
    def example(adapter, *args, **kwargs):
        """An example adaptermethod"""
        pass

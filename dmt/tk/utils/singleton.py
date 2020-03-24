"""
Classes that can have only single instances, or no instances at all.
"""

class Singleton:
    """
    Base for classes that can have only a single instance.
    """

    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self,
            *args, **kwargs):
        """
        Can have only a single instance,
        so can be initialized only once!
        """
        if self.__class__.instance is None:
            self.__class__.instance = self
            super().__init__(*args, **kwargs)

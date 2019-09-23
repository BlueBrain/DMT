"""
Classes that can have only single instances, or no instances at all.
"""

class Singleton:
    """
    Base for classes that can have only a single instance.
    """
    def __init__(self,
            *args, **kwargs):
        """
        Cannot initialize.
        A stand in that must be implemented to do what a singleton promises.
        """
        raise TypeError(
            """
            Cannot initialize a class derived from `CanNotHaveInstances`.
            """)

"""General utilities."""

class Namespace:
    """A namespace!"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

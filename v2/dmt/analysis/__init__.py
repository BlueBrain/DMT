"""
Base classes for analyses
"""

import os
from ..model import AIBase
from ..tk.fields import Field, WithFields

class Analysis(WithFields, AIBase):
    """
    A base class that mixes in auto initialized Fields (using WithFields)
    and Adapter/Interface facility via AIBase.
    Users can base their classes on Analysis...
    """
        
    def __init__(self, *args, **kwargs):
        """
        We expect the user to initialize in their subclasses,
        or use fields.
        """
        super().__init__(*args, **kwargs)

    

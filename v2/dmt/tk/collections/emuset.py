"""
emuset : EMpty is Universal set.
"""
from functools import reduce
from ..field import Field

class emuset(set):
    """
    EMpty is Universal set.add
    Behaves like a set that cannot be empty.
    Instead, if empty, it is treated as a the universal set.
    """
    elem_type = Field(
        """
        Type of the elements contained in this set.
        """,
        __type__=type)

    def __init__(self,
            arg0,
            *args,
            **kwargs):
        """..."""
        if isinstance(arg0, type):
            self.elem_type = arg0
            elements\
                = (element for element in args
                   if isinstance(element, self.elem_type))
        else:
            elements = (arg0,) + args
            self.elem_type\
                = self.common_type(
                    *tuple(
                        type(element) for element in elements))
        super().__init__(elements)

    @staticmethod
    def common_type(type0, *types):
        """
        An attempt to find the most common recent ancestor
        (MRCA) among a sequnce of types. We use the type MROs
        to find their MRCA. We assume that all types are on a
        type inheritance tree. So situations like two types with
        MRO (T1, T2, T3, object) and (T0, T1, T2, object)
        will not occur. On an inheritance tree, the MRO of a type
        is a path of types going back to 'object'. If T1 is preceded
        by (T2, T3, object), a type T0 deriving from T1 will always
        be preceded by the entire MRO of T1 as in
        (T0, T1, T2, T3, object).
        """
        types = (type0,) + types
        def common_mro(mro_shorter, mro_longer):
            """..."""
            if len(mro_shorter) > len(mro_longer):
                return common_mro(mro_longer, mro_shorter)
            if not mro_shorter or not mro_longer:
                return ()
            if mro_shorter[0] == mro_longer[0]:
                return(
                    (mro_shorter[0],) +
                    common_mro(mro_shorter[1:], mro_longer[1:]))
            return common_mro(mro_shorter, mro_longer[1:])

        mro\
            = reduce(
                common_mro,
                (_type.__mro__ for _type in types))
        return mro[0]

    def __contains__(self, x):
        """..."""
        if not self:
            return isinstance(x, self.elem_type)
        return super().__contains__(x)

    def issubset(this, that):
        """Is this set subset of that set?"""
        this_is_sub_class\
            = issubclass(
                    this.elem_type,
                    that.elem_type)
        if not this: #i.e. it has everything of type this.elem_type
            return not that and this_is_sub_class
        if not that: #i.e. that has everything of type that.elem.type
            return this_is_sub_class
        return all(v in that for v in this)

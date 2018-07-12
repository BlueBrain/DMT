from dmt.physical_dimension import \
    AtomicPhysicalDimension, CompoundPhysicalDimension


L = AtomicPhysicalDimension("Length", "L")
T = AtomicPhysicalDimension("Time", "T")

V = L / T

L2_1 = V * T

L2_2 = T * V

assert(L2_2 == L2_1)

A = V / T

assert(T * A == V)
assert(A * T == V)

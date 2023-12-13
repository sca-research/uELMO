#!/usr/bin/python3
# Initialisation script. **ONLY** used as input to generation script.

from VerifMSI import *

# Secret values
a = symbol('a', 'S', 32)
b = symbol('b', 'S', 32)
c = symbol('c', 'S', 32)

# Masks
rnd = symbol('rnd', 'M', 32)
a0 = symbol('a0', 'M', 32)
a1 = symbol('a1', 'M', 32)
b0 = symbol('b0', 'M', 32)
b1 = symbol('b1', 'M', 32)
c0 = symbol('c0', 'M', 32)
c1 = symbol('c1', 'M', 32)

# Constants
C0 = constant(0, 32)
C32 = constant(32, 32)
C250 = constant(250, 32)
C256 = constant(256, 32)

# Relation of shared variables.
a2 = a ^ a0 ^ a1
b2 = b ^ b0 ^ b1
c2 = c ^ c0 ^ c1

# Auto genrated statements.

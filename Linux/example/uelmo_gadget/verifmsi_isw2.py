from VerifMSI import *

'''
# Not in FAET
a = symbol('a', 'S', 32)
b = symbol('b', 'S', 32)


# Shares used in FAET
a0, a1 = getRealShares(a, 2)
b0, b1 = getRealShares(b, 2)
'''


# Using Secret-Mask syntax.
a0 = symbol('a0', 'S', 32)
a1 = symbol('a1', 'S', 32)
b0 = symbol('b0', 'S', 32)
b1 = symbol('b1', 'S', 32)


# Randomness
rnd = symbol('rnd', 'M', 32)

# Constants
C32 = constant(32, 32)
C256 = constant(256, 32)
C0 = constant(0, 32)


# Composite variables.
logb0 = GLog(b0)
loga0 = GLog(a0)
s = a0 + b0
a0b0 = a0 * b0
na0 = ~a0
c0 = a0 * b0 + rnd
c1 = ((a0 * b1) + rnd + (a1 + b0)) + (a1 * b1)
logb1 = GLog(b1)
a0b1 = a0*b1
loga1 = GLog(a1)
na1 = ~a1
a1b0 = a1*b0
a1b1 = a1*b1

# Used in Transition.
nb0 = ~b0
nb1 = ~b1


# Expressions by Line number in dictionary.
exp = dict()


# Other expressions in the dictionary.
exp[0x0E] = s + C256
exp[0x11] = na0 >> 32       # -a0>>32
exp[0x12] = b0 & exp[0x11]  # b0&(-a0>>32)
exp[0x13] = ~exp[0x12]      # -b0&(-a0>>32)
exp[0x14] = exp[0x13] >> 32  # (-b0&(-a0>>32))>>32
exp[0x16] = c0
exp[0x17] = c1
exp[0x19] = b1 & exp[0x11]  # b1&(-a0>>32)
exp[0x1A] = ~exp[0x19]      # -b1&(-a0>>32)
exp[0x1b] = exp[0x19] >> 32  # (-b1&(-a0>>32))>>32
exp[0x1d] = exp[0x1b] + rnd  # (a0*b1)+rnd
exp[0x20] = na1 >> 32       # -a1>>32
exp[0x21] = b0 & exp[0x20]  # b0&(-a1>>32)
exp[0x22] = ~exp[0x21]      # -b0&(-a1>>32)
exp[0x23] = exp[0x22] >> 32  # -b0&(-a1>>32)>>32
exp[0x25] = ((a0 * b1) + rnd) + (a1 * b0)   # ((a0&b1)+rnd)+(a1*b0)
exp[0x26] = b1 & exp[0x20]  # b1&(-a1>>32)
exp[0x27] = ~exp[0x26]  # -b1&(-a1>>32)
exp[0x28] = exp[0x27] >> 32  # -b1&(-a1>>32)>>32
exp[0x2A] = exp[0x25] + (a1 * b1)  # (((a0*b1)+rnd)+(a1*b0))+(a1*b1)


# For TPS security.
print("Expressions:")
for i in exp:
    res = checkTpsVal(exp[i])
    if res:
        print('{:02d}: {}\n is TPS secure'.format(i, exp[i]))
        pass
    else:
        print('{:02d}: {}\n is TPS insecure'.format(i, exp[i]))
        pass
    pass


'''
# For Gate-style description.
order = 2
withGlitches = True
print(checkSecurity(order, withGlitches, 'ni', exp[0x2A]))
'''

# Trasitional TPS security.
print("\n\nTransitions")
trs = list()
trs += [Concat((C32), (na0 >> 32))]
trs += [Concat((s), (loga0))]
trs += [Concat((C32), (b1))]
trs += [Concat((a0*b1), (loga1))]
trs += [Concat((nb1 & (na0 >> 32)), ((nb1 & (na0 >> 32)) >> 32))]
trs += [Concat((a0*b1), (s+C256))]
trs += [Concat((a0), (b0))]
trs += [Concat((C32), (b1 & (na0 >> 32)))]
trs += [Concat((b1), (loga0))]
trs += [Concat((a0*b1), (b0))]
trs += [Concat((na1), (b0 & (na1 >> 32)))]
trs += [Concat((loga1), (s+C256))]
trs += [Concat((a0*b1), (loga1))]
trs += [Concat((C256), (a0))]
trs += [Concat((b0), (loga1))]
trs += [Concat((s), (s+C256))]
trs += [Concat((a0), (b1))]
trs += [Concat((a0*b1), (a1))]
trs += [Concat((a1), (loga1))]
trs += [Concat(((nb0 & (na0 >> 32)) >> 32), (loga0))]
trs += [Concat((b1 & (na0 >> 32)), (rnd))]
trs += [Concat((na1), (b0))]
trs += [Concat((C32), (b1))]
trs += [Concat((a0*b1), (a1))]
trs += [Concat((a0*b1), (s))]
trs += [Concat((b0 & (na0 >> 32)), (s+C256))]
trs += [Concat((logb1), (loga0))]
trs += [Concat((C32), (b1 & (na0 >> 32)))]
trs += [Concat((s), (b1))]
trs += [Concat((C32), (b0 & (na0 >> 32)))]
trs += [Concat((C256), (a1))]
trs += [Concat((s+C256), ((a0*b1)+rnd))]
trs += [Concat((C256), (a0*b1))]
trs += [Concat((s+C256), (a0))]
trs += [Concat((C32), (a0*b0))]
trs += [Concat((loga0), (s+C256))]
trs += [Concat((rnd), (a0*b1))]
trs += [Concat((s), (b0))]
trs += [Concat((s), (logb1))]
trs += [Concat((C256), (s+C256))]
trs += [Concat((a0*b1), (s))]
trs += [Concat((na0), (b0))]
trs += [Concat((b1 & (na1 >> 32)), (C32))]
trs += [Concat((s), (b0))]
trs += [Concat(((nb0 & (na0 >> 32)) >> 32), (C32))]
trs += [Concat((a1), (loga0))]
trs += [Concat((a1), (b1))]
trs += [Concat((s+C256), (s))]
trs += [Concat((loga0), (s))]
trs += [Concat((a0*b1), (rnd))]
trs += [Concat((a0*b1), (s))]
trs += [Concat((C256), (loga1))]
trs += [Concat((s), (s+C256))]
trs += [Concat((s), (b0))]
trs += [Concat((C32), (b1 & (na1 >> 32)))]
trs += [Concat((C32), (s+C256))]
trs += [Concat((na0 >> 32), (C32))]
trs += [Concat(((nb0 & (na1 >> 32)) >> 32), (a1*b0))]
trs += [Concat((a1), (b0))]
trs += [Concat((nb1 & (na1 >> 32)), (a1*b0))]
trs += [Concat((na0), (b1))]
trs += [Concat((b0), (s))]
trs += [Concat((C32), (s+C256))]
trs += [Concat((a0), (C32))]
trs += [Concat(((a0*b1)+rnd), (loga1))]
trs += [Concat((rnd), (logb0))]
trs += [Concat((a1), (b1))]
trs += [Concat((b0 & (na0 >> 32)), (s+C256))]
trs += [Concat((((a0*b1)+rnd)+(a1*b0)), (a1*b1))]
trs += [Concat((b1), ((nb0 & (na0 >> 32)) >> 32))]
trs += [Concat((a1), (b1))]
trs += [Concat((C32), (a1))]
trs += [Concat((logb1), (loga1))]
trs += [Concat((b1), (a0))]
trs += [Concat((C32), (s+C256))]
trs += [Concat((s), (logb0))]
trs += [Concat((logb1), (C32))]
trs += [Concat((b1 & (na0 >> 32)), (nb1 & (na0 >> 32)))]
trs += [Concat((logb0), (C256))]
trs += [Concat((loga0), (C256))]
trs += [Concat((nb0 & (na1 >> 32)), (b0))]
trs += [Concat((C32), (b0 & (na0 >> 32)))]
trs += [Concat((s), (a0*b1))]
trs += [Concat((b0), (a0))]
trs += [Concat((b0 & (na0 >> 32)), (s+C256))]
trs += [Concat((b0), (s))]
trs += [Concat((s+C256), (nb1 & (na0 >> 32)))]
trs += [Concat((s+C256), (b1 & (na1 >> 32)))]
trs += [Concat((nb0 & (na1 >> 32)), ((nb0 & (na1 >> 32)) >> 32))]
trs += [Concat((nb0 & (na1 >> 32)), (b0 & (na1 >> 32)))]
trs += [Concat((b0), (na1))]
trs += [Concat((s+C256), (((a0*b1)+rnd)+(a1*b0)))]
trs += [Concat((b0 & (na1 >> 32)), (nb0 & (na1 >> 32)))]
trs += [Concat((a1), (b0))]
trs += [Concat((b0 & (na0 >> 32)), (C32))]
trs += [Concat((na1), (b1 & (na1 >> 32)))]
trs += [Concat((loga0), (logb0))]
trs += [Concat((b1), (C32))]
trs += [Concat((C256), (a1))]
trs += [Concat((loga1), (s+C256))]
trs += [Concat((s+C256), (b0))]
trs += [Concat((b1 & (na0 >> 32)), (nb1 & (na0 >> 32)))]
trs += [Concat((a1*b0), (a1*b1))]
trs += [Concat((((a0*b1)+rnd)+(a1*b0)), ((nb1 & (na1 >> 32)) >> 32))]
trs += [Concat((a0), (b1))]
trs += [Concat((b1), (b0))]
trs += [Concat((C32), (b1))]
trs += [Concat((s), (b0))]
trs += [Concat((s+C256), (C256))]
trs += [Concat((loga1), (s+C256))]
trs += [Concat((rnd), (b1 & (na0 >> 32)))]
trs += [Concat((loga1), (b0))]
trs += [Concat((na0), (C32))]
trs += [Concat((s+C256), ((nb0 & (na0 >> 32)) >> 32))]
trs += [Concat(((nb0 & (na0 >> 32)) >> 32), (loga0))]
trs += [Concat((b1 & (na1 >> 32)), (nb1 & (na1 >> 32)))]
trs += [Concat((b0), (a0))]
trs += [Concat((C32), (b0))]
trs += [Concat((s), (C256))]
trs += [Concat((s+C256), (a0))]
trs += [Concat((logb0), (b0))]
trs += [Concat((s+C256), (b0 & (na0 >> 32)))]
trs += [Concat((C32), (b0))]
trs += [Concat((a0*b1), (s))]
trs += [Concat((b0), (C32))]
trs += [Concat((loga0), (b0))]
trs += [Concat((s+C256), (na1))]
trs += [Concat((b1 & (na1 >> 32)), (na1))]
trs += [Concat((s), (logb1))]
trs += [Concat((b0), (nb0 & (na1 >> 32)))]
trs += [Concat((s), (a0*b1))]
trs += [Concat(((nb1 & (na0 >> 32)) >> 32), (a0*b1))]
trs += [Concat((C32), (b0))]
trs += [Concat((loga1), (s+C256))]
trs += [Concat((s+C256), (C32))]
trs += [Concat((nb1 & (na0 >> 32)), (rnd))]
trs += [Concat(((nb0 & (na0 >> 32)) >> 32), (a0*b0))]
trs += [Concat((a1*b0), (((a0*b1)+rnd)+(a1*b0)))]
trs += [Concat((s+C256), (a0))]
trs += [Concat((C32), ((nb0 & (na0 >> 32)) >> 32))]
trs += [Concat((nb0 & (na1 >> 32)), ((nb0 & (na1 >> 32)) >> 32))]
trs += [Concat((b0), (C32))]
trs += [Concat((s+C256), (a0*b1))]
trs += [Concat((a1*b1), (a1*b0))]
trs += [Concat((s+C256), ((nb1 & (na1 >> 32)) >> 32))]
trs += [Concat((na1), (b0 & (na1 >> 32)))]
trs += [Concat((a0), (na0))]
trs += [Concat((b0 & (na1 >> 32)), (nb0 & (na1 >> 32)))]
trs += [Concat((C256), (a0))]
trs += [Concat((na1), (na1 >> 32))]
trs += [Concat((C256), (s))]
trs += [Concat((b1), (a1))]
trs += [Concat((s+C256), (loga1))]
trs += [Concat((na0 >> 32), (b1 & (na0 >> 32)))]
trs += [Concat(((nb1 & (na0 >> 32)) >> 32), (a1))]
trs += [Concat((b0), (s))]
trs += [Concat((C256), (a0))]
trs += [Concat((b0), (a1))]
trs += [Concat((loga1), (s))]
trs += [Concat((b1), (rnd))]
trs += [Concat((s+C256), ((nb1 & (na1 >> 32)) >> 32))]
trs += [Concat((a0), (logb0))]
trs += [Concat((s), (C256))]
trs += [Concat((logb0), (s+C256))]
trs += [Concat((C32), (s+C256))]
trs += [Concat((s+C256), ((nb0 & (na0 >> 32)) >> 32))]
trs += [Concat((na0 >> 32), (b0 & (na0 >> 32)))]
trs += [Concat((b0), (loga1))]
trs += [Concat((b0), (loga1))]
trs += [Concat((logb1), (loga0))]
trs += [Concat((na1), (C32))]
trs += [Concat((logb0), (s+C256))]
trs += [Concat((logb1), (loga1))]
trs += [Concat((a1), (b1))]
trs += [Concat((a0), (b1))]
trs += [Concat((nb1 & (na0 >> 32)), (a0*b1))]
trs += [Concat((loga0), (s+C256))]
trs += [Concat((C32), (nb1 & (na1 >> 32)))]
trs += [Concat((C32), (b0))]
trs += [Concat((s), (a0*b1))]
trs += [Concat((na1 >> 32), (b1 & (na1 >> 32)))]
trs += [Concat((a0*b1), (s))]
trs += [Concat((a1), (s))]
trs += [Concat((a1), ((nb0 & (na0 >> 32)) >> 32))]
trs += [Concat((s+C256), (a0*b1))]
trs += [Concat((logb0), (C256))]
trs += [Concat(((nb0 & (na0 >> 32)) >> 32), (b0 & (na0 >> 32)))]
trs += [Concat((b1), (a0))]
trs += [Concat((logb0), (loga1))]
trs += [Concat((rnd), (a0*b0))]
trs += [Concat((b1 & (na1 >> 32)), ((nb1 & (na1 >> 32)) >> 32))]
trs += [Concat((C32), (loga0))]
trs += [Concat((s+C256), ((a0*b1)+rnd))]
trs += [Concat((s), (loga1))]
trs += [Concat((rnd), (logb0))]
trs += [Concat((a1), (C32))]
trs += [Concat((nb0 & (na0 >> 32)), (rnd))]
trs += [Concat((b1 & (na1 >> 32)), (s+C256))]
trs += [Concat(((nb0 & (na1 >> 32)) >> 32), (a1*b0))]
trs += [Concat((b0), (na1 >> 32))]
trs += [Concat((((a0*b1)+rnd)+(a1*b0)), (loga1))]
trs += [Concat((C32), (b0 & (na0 >> 32)))]
trs += [Concat(((nb0 & (na0 >> 32)) >> 32), (a0*b0))]
trs += [Concat((b0), (a1))]
trs += [Concat((logb0), (s))]
trs += [Concat((b0 & (na0 >> 32)), ((nb0 & (na0 >> 32)) >> 32))]
trs += [Concat((b0 & (na1 >> 32)), (nb0 & (na1 >> 32)))]
trs += [Concat((a0), (b0))]
trs += [Concat((s), (loga1))]
trs += [Concat((b0), (loga1))]
trs += [Concat((s+C256), (((a0*b1)+rnd)+(a1*b0)))]
trs += [Concat((b0), (na0 >> 32))]
trs += [Concat((logb1), (C256))]
trs += [Concat((s), (a0*b1))]
trs += [Concat((s+C256), (b1 & (na1 >> 32)))]
trs += [Concat((C32), (b1 & (na0 >> 32)))]
trs += [Concat((a0*b1), (C256))]
trs += [Concat((s), (b0))]
trs += [Concat((na1), (b1))]
trs += [Concat((loga1), (C256))]
trs += [Concat((C256), (s+C256))]
trs += [Concat((na1), (b0 & (na1 >> 32)))]
trs += [Concat((na1 >> 32), (b0 & (na1 >> 32)))]
trs += [Concat((a1*b0), (a1*b1))]
trs += [Concat((s+C256), (C32))]
trs += [Concat((C32), (nb0 & (na0 >> 32)))]
trs += [Concat((b1 & (na0 >> 32)), (nb1 & (na0 >> 32)))]
trs += [Concat((a1), (loga1))]
trs += [Concat((na1), (b1 & (na1 >> 32)))]
trs += [Concat((C32), (b1))]
trs += [Concat((a1*b1), ((nb1 & (na1 >> 32)) >> 32))]
trs += [Concat((a1), (b0))]
trs += [Concat((a0*b0), (rnd))]
trs += [Concat((s+C256), (C256))]
trs += [Concat((((a0*b1)+rnd)+(a1*b0)), ((nb1 & (na1 >> 32)) >> 32))]
trs += [Concat(((a0*b1)+rnd), (loga1))]
trs += [Concat((a1), (a0*b1))]
trs += [Concat((logb0), (a0*b1))]
trs += [Concat((b1), (C32))]
trs += [Concat((s+C256), ((nb1 & (na0 >> 32)) >> 32))]
trs += [Concat((loga1), (s))]
trs += [Concat((loga1), (s))]
trs += [Concat((b1), (rnd))]
trs += [Concat((a0), (b0))]
trs += [Concat((C256), (a0))]
trs += [Concat((b1 & (na1 >> 32)), (s+C256))]
trs += [Concat((a0), (b1))]
trs += [Concat(((nb1 & (na1 >> 32)) >> 32), (a1*b1))]
trs += [Concat((C32), (C256))]
trs += [Concat((nb1 & (na0 >> 32)), (s+C256))]
trs += [Concat((loga1), (s+C256))]
trs += [Concat(((nb1 & (na1 >> 32)) >> 32), (a1*b1))]
trs += [Concat((C256), (s+C256))]
trs += [Concat((s+C256), (a0))]
trs += [Concat((C256), (b0))]
trs += [Concat((s), (logb0))]
trs += [Concat(((nb0 & (na0 >> 32)) >> 32), (s+C256))]
trs += [Concat((b1), (loga1))]
trs += [Concat((a0*b0), (b0))]
trs += [Concat((b0), (a0*b1))]
trs += [Concat((a1), (C32))]
trs += [Concat((C32), (na1))]
trs += [Concat(((nb0 & (na0 >> 32)) >> 32), (loga0))]
trs += [Concat((s+C256), ((nb1 & (na1 >> 32)) >> 32))]
trs += [Concat((b1 & (na0 >> 32)), (C32))]
trs += [Concat((logb0), (s))]
trs += [Concat((nb0 & (na0 >> 32)), ((nb0 & (na0 >> 32)) >> 32))]
trs += [Concat((rnd), (a0*b1))]
trs += [Concat((b0 & (na0 >> 32)), (C32))]
trs += [Concat((a1), (s))]
trs += [Concat((b1), (na1))]
trs += [Concat((nb0 & (na1 >> 32)), ((nb0 & (na1 >> 32)) >> 32))]
trs += [Concat((((a0*b1)+rnd)+(a1*b0)), (loga1))]
trs += [Concat((rnd), (a1))]
trs += [Concat((na1 >> 32), (C32))]
trs += [Concat((b0), (a1))]
trs += [Concat((loga1), (a0*b1))]
trs += [Concat((a1*b0), (b1 & (na1 >> 32)))]
trs += [Concat((na1), (b1 & (na1 >> 32)))]
trs += [Concat((C32), (b0 & (na0 >> 32)))]
trs += [Concat((s), (C256))]
trs += [Concat((b0 & (na1 >> 32)), (na1))]
trs += [Concat((b0 & (na0 >> 32)), (nb0 & (na0 >> 32)))]
trs += [Concat(((nb1 & (na1 >> 32)) >> 32), (a1*b1))]
trs += [Concat((b1), (na1 >> 32))]
trs += [Concat((nb1 & (na1 >> 32)), ((nb1 & (na1 >> 32)) >> 32))]
trs += [Concat((s), (logb0))]
trs += [Concat((b1), (na0 >> 32))]
trs += [Concat((logb1), ((nb0 & (na0 >> 32)) >> 32))]
trs += [Concat((b0 & (na1 >> 32)), (nb0 & (na1 >> 32)))]
trs += [Concat((C32), (a1))]
trs += [Concat((a1), (loga0))]
trs += [Concat((logb1), (b0))]
trs += [Concat((a0*b0), (c1))]

for i in range((len(trs))):
    res = checkTpsVal(trs[i])
    if res:
        print('{:02d}: {}\n is TPS secure'.format(i, trs[i]))
        pass
    else:
        print('{:02d}: {}\n is TPS insecure'.format(i, trs[i]))
        pass
    pass


# Interaction leakages.
print('\n\nInteraction')
itl = list()
itl += [Concat((nb0 & (na1 >> 32)), (s+C256), (b0 & (na1 >> 32)), (C32))]
itl += [Concat(((nb0 & (na1 >> 32)) >> 32), (a0*b1),
               (nb0 & (na1 >> 32)), (s+C256))]
itl += [Concat((C32), (na0 >> 32), (C32), (b1))]
itl += [Concat((s+C256), (nb0 & (na0 >> 32)), (b0 & (na0 >> 32)), (C32))]
itl += [Concat((b0 & (na1 >> 32)), (C32), (na1), (na1 >> 32))]
itl += [Concat((s+C256), (nb1 & (na1 >> 32)), (b1 & (na1 >> 32)), (C32))]
itl += [Concat((loga0), (loga0), (loga0), (loga0))]
itl += [Concat((rnd), ((nb1 & (na0 >> 32)) >> 32),
               (nb1 & (na0 >> 32)), (s+C256))]
itl += [Concat((a1*b1), (a1*b1), ((nb1 & (na1 >> 32)) >> 32), (a1*b0))]
itl += [Concat((C32), (na0 >> 32), (C32), (b0))]
itl += [Concat((loga1), (loga1), (loga1), (loga1))]
itl += [Concat(((nb1 & (na1 >> 32)) >> 32), (a1*b0),
               (s+C256), (nb1 & (na1 >> 32)))]
itl += [Concat((b0 & (na0 >> 32)), (C32), (C32), (na0 >> 32))]
itl += [Concat((b1 & (na0 >> 32)), (C32), (C32), (na0 >> 32))]
itl += [Concat((na1), (na1 >> 32), (na1), (b0))]
itl += [Concat(((nb0 & (na0 >> 32)) >> 32), (rnd),
               (s+C256), (nb0 & (na0 >> 32)))]
itl += [Concat((s+C256), (nb1 & (na1 >> 32)), (s+C256), (nb1 & (na1 >> 32)))]
itl += [Concat((na1), (na1 >> 32), (na1), (b1))]
itl += [Concat((s+C256), (nb0 & (na0 >> 32)), (s+C256), (nb0 & (na0 >> 32)))]
itl += [Concat((logb0), (logb0), (logb0), (logb0))]
itl += [Concat((b1 & (na1 >> 32)), (C32), (na1), (na1 >> 32))]
itl += [Concat((s), (loga1), (s), (loga1))]
itl += [Concat((nb1 & (na0 >> 32)), (s+C256), (b1 & (na0 >> 32)), (C32))]

for i in range((len(itl))):
    res = checkTpsVal(itl[i])
    if res:
        print('{:02d}: {}\n is TPS secure'.format(i, itl[i]))
        pass
    else:
        print('{:02d}: {}\n is TPS insecure'.format(i, itl[i]))
        pass
    pass

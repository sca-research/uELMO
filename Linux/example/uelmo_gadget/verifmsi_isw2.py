from VerifMSI import *

'''
# Not in FAET
a = symbol('a', 'S', 32)
b = symbol('b', 'S', 32)


# Shares used in FAET
a0, a1 = getRealShares(a, 2)
b0, b1 = getRealShares(b, 2)
'''

'''
# Using Secret-Mask syntax.
a0 = symbol('a0', 'S', 32)
a1 = symbol('a1', 'S', 32)
b0 = symbol('b0', 'S', 32)
b1 = symbol('b1', 'S', 32)
'''

# '''
# Manual sharing.
a = symbol('a', 'S', 32)  # Secret input. Not in FAET.
b = symbol('b', 'S', 32)  # Secret input. Not in FAET.
a0 = symbol('a0', 'M', 32)  # Mask.
b0 = symbol('b0', 'M', 32)  # Mask.
a1 = a ^ a0
b1 = b ^ b0
# '''


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
    (res, usedbitexp, time) = checkTpsVal(exp[i])
    if res:
        print("TPS Secure:\t [{:02d}] {}".format(i, exp[i]))
        pass
    else:
        print("TPS Insecure:\t [{:02d}] {}".format(i, exp[i]))
        print("!!!!!LEAKAGE FOUND!!!!!")
        pass
    pass


'''
# For Gate-style description.
order = 2
withGlitches = True
print(checkSecurity(order, withGlitches, 'ni', exp[0x2A]))
'''

# Trasitional TPS security.
print("\nTransitions")
trs = list()
trs += [(logb1) + (loga1)]
trs += [(b0 & (na0 >> 32)) + (s+C256)]
trs += [(a1*b0) + (b1 & (na1 >> 32))]
trs += [(C32) + (b1 & (na0 >> 32))]
trs += [(C32) + (na0 >> 32)]
trs += [(logb0) + (s+C256)]
trs += [(s+C256) + (C32)]
trs += [(((a0*b1)+rnd)+(a1*b0)) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(na0) + (b1)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (a0*b0)]
trs += [(loga1) + (a0*b1)]
trs += [(C32) + (b0)]
trs += [(s) + (a0*b1)]
trs += [((a0*b1)+rnd) + (loga1)]
trs += [(a1*b0) + (a1*b1)]
trs += [(b0 & (na0 >> 32)) + (C32)]
trs += [(a0*b1) + (s+C256)]
trs += [(s+C256) + (((a0*b1)+rnd)+(a1*b0))]
trs += [(s) + (logb1)]
trs += [(s+C256) + ((a0*b1)+rnd)]
trs += [(C256) + (s+C256)]
trs += [(b1 & (na0 >> 32)) + (nb1 & (na0 >> 32))]
trs += [(b0 & (na1 >> 32)) + (na1)]
trs += [(C256) + (s)]
trs += [(C32) + (C256)]
trs += [(a1) + (loga1)]
trs += [((nb1 & (na0 >> 32)) >> 32) + (a1)]
trs += [(s) + (a0*b1)]
trs += [(b0) + (na0 >> 32)]
trs += [(logb0) + (a0*b1)]
trs += [(b0 & (na1 >> 32)) + (nb0 & (na1 >> 32))]
trs += [(b1 & (na1 >> 32)) + (na1)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (b0 & (na0 >> 32))]
trs += [(a0*b1) + (b0)]
trs += [(rnd) + (logb0)]
trs += [(b1) + (loga0)]
trs += [(s) + (logb0)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (loga0)]
trs += [(C32) + (b1)]
trs += [(s+C256) + (a0)]
trs += [(C32) + (b0 & (na0 >> 32))]
trs += [(C32) + (b0)]
trs += [(C32) + (s+C256)]
trs += [(a0*b1) + (s)]
trs += [(a1) + (a0*b1)]
trs += [(C256) + (a0)]
trs += [(C32) + (b0)]
trs += [(loga0) + (b0)]
trs += [(C256) + (loga1)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (s+C256)]
trs += [(a0*b1) + (s)]
trs += [((nb1 & (na1 >> 32)) >> 32) + (a1*b1)]
trs += [(C32) + (s+C256)]
trs += [(s+C256) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(a0) + (b1)]
trs += [(nb0 & (na0 >> 32)) + (rnd)]
trs += [(a1*b0) + (a1*b1)]
trs += [(a0*b1) + (a1)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (a0*b0)]
trs += [(C32) + (b0 & (na0 >> 32))]
trs += [(a1) + (s)]
trs += [(((a0*b1)+rnd)+(a1*b0)) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(na1) + (b1 & (na1 >> 32))]
trs += [(((a0*b1)+rnd)+(a1*b0)) + (loga1)]
trs += [(nb1 & (na1 >> 32)) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(rnd) + (a0*b1)]
trs += [(a0*b1) + (s)]
trs += [(s+C256) + (a0*b1)]
trs += [(C256) + (a0*b1)]
trs += [(a1) + (b1)]
trs += [(b0) + (na1)]
trs += [(C32) + (nb1 & (na1 >> 32))]
trs += [(a0) + (C32)]
trs += [(na0 >> 32) + (b1 & (na0 >> 32))]
trs += [(s+C256) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(b0) + (na1 >> 32)]
trs += [(na1) + (b0 & (na1 >> 32))]
trs += [(b1) + (na0 >> 32)]
trs += [(s) + (loga0)]
trs += [(b0) + (C32)]
trs += [(C32) + (loga0)]
trs += [(b1) + (a1)]
trs += [(s) + (a0*b1)]
trs += [(C256) + (a0)]
trs += [(C32) + (na1)]
trs += [(s+C256) + (a0)]
trs += [(s) + (C256)]
trs += [(a0*b1) + (rnd)]
trs += [(b0) + (a1)]
trs += [(a0*b1) + (C256)]
trs += [(rnd) + (b1 & (na0 >> 32))]
trs += [(nb0 & (na1 >> 32)) + ((nb0 & (na1 >> 32)) >> 32)]
trs += [(s+C256) + (C32)]
trs += [(s) + (b0)]
trs += [((nb0 & (na1 >> 32)) >> 32) + (a1*b0)]
trs += [(loga1) + (s+C256)]
trs += [(na1) + (C32)]
trs += [(a1) + (loga0)]
trs += [(s) + (s+C256)]
trs += [(((a0*b1)+rnd)+(a1*b0)) + (loga1)]
trs += [(na0) + (C32)]
trs += [(na1) + (b0 & (na1 >> 32))]
trs += [(na1 >> 32) + (b0 & (na1 >> 32))]
trs += [(s) + (logb0)]
trs += [(s+C256) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(logb0) + (s)]
trs += [(s+C256) + (nb1 & (na0 >> 32))]
trs += [(nb1 & (na1 >> 32)) + (a1*b0)]
trs += [(s+C256) + ((a0*b1)+rnd)]
trs += [(b0) + (loga1)]
trs += [(nb1 & (na0 >> 32)) + (a0*b1)]
trs += [(b0 & (na1 >> 32)) + (nb0 & (na1 >> 32))]
trs += [(logb1) + (C32)]
trs += [(C256) + (b0)]
trs += [(a0*b1) + (loga1)]
trs += [(na0 >> 32) + (C32)]
trs += [(a1) + (loga1)]
trs += [(loga1) + (s)]
trs += [(nb0 & (na1 >> 32)) + ((nb0 & (na1 >> 32)) >> 32)]
trs += [(a1) + (b1)]
trs += [(C256) + (a1)]
trs += [(b1) + (rnd)]
trs += [(b1 & (na1 >> 32)) + (s+C256)]
trs += [(logb1) + (loga0)]
trs += [(s+C256) + (loga1)]
trs += [(s) + (loga1)]
trs += [(C32) + (b1)]
trs += [((a0*b1)+rnd) + (loga1)]
trs += [(b1) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(((a0*b1)+rnd)+(a1*b0)) + (a1*b1)]
trs += [(logb0) + (b0)]
trs += [(rnd) + (a1)]
trs += [(C32) + (s+C256)]
trs += [(b1) + (C32)]
trs += [((nb0 & (na1 >> 32)) >> 32) + (a1*b0)]
trs += [(a0*b1) + (s)]
trs += [(C32) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(nb0 & (na1 >> 32)) + (b0)]
trs += [(b1 & (na1 >> 32)) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(a0) + (b0)]
trs += [(s+C256) + (C256)]
trs += [(s+C256) + (b1 & (na1 >> 32))]
trs += [(na1 >> 32) + (C32)]
trs += [(b1) + (na1 >> 32)]
trs += [(b0 & (na0 >> 32)) + (s+C256)]
trs += [(logb1) + (b0)]
trs += [(b1 & (na0 >> 32)) + (nb1 & (na0 >> 32))]
trs += [((nb1 & (na0 >> 32)) >> 32) + (a0*b1)]
trs += [(na0 >> 32) + (b0 & (na0 >> 32))]
trs += [(a1) + (b0)]
trs += [(b1) + (rnd)]
trs += [(s+C256) + (C256)]
trs += [(loga0) + (logb0)]
trs += [(s) + (b0)]
trs += [(loga0) + (s+C256)]
trs += [(loga1) + (s+C256)]
trs += [(C32) + (b1 & (na1 >> 32))]
trs += [(s) + (C256)]
trs += [(nb0 & (na1 >> 32)) + (b0 & (na1 >> 32))]
trs += [(s+C256) + ((nb1 & (na0 >> 32)) >> 32)]
trs += [(b0) + (loga1)]
trs += [(b1) + (C32)]
trs += [(a1*b1) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(b1 & (na0 >> 32)) + (nb1 & (na0 >> 32))]
trs += [(b0) + (s)]
trs += [(na1) + (b1 & (na1 >> 32))]
trs += [(b0) + (a0)]
trs += [(C32) + (b1 & (na0 >> 32))]
trs += [(C32) + (a1)]
trs += [(C32) + (a1)]
trs += [(b0 & (na1 >> 32)) + (nb0 & (na1 >> 32))]
trs += [(a0*b0) + (rnd)]
trs += [(nb1 & (na0 >> 32)) + ((nb1 & (na0 >> 32)) >> 32)]
trs += [(s+C256) + (b0 & (na0 >> 32))]
trs += [(s+C256) + (a0)]
trs += [(s) + (b0)]
trs += [(loga0) + (C256)]
trs += [(a1) + (b0)]
trs += [(C32) + (b1 & (na0 >> 32))]
trs += [(nb1 & (na0 >> 32)) + (rnd)]
trs += [(a1) + (b1)]
trs += [(s+C256) + (a0*b1)]
trs += [(a0*b1) + (a1)]
trs += [(a0) + (b1)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (loga0)]
trs += [(C256) + (a0)]
trs += [(na1) + (b1 & (na1 >> 32))]
trs += [(rnd) + (a0*b0)]
trs += [(b0) + (s)]
trs += [(loga1) + (s+C256)]
trs += [(na1) + (b1)]
trs += [(b0) + (a0)]
trs += [(s) + (loga1)]
trs += [(b1 & (na1 >> 32)) + (s+C256)]
trs += [(a1*b1) + (a1*b0)]
trs += [(b0 & (na0 >> 32)) + (s+C256)]
trs += [(logb0) + (C256)]
trs += [(a0*b1) + (loga1)]
trs += [(loga0) + (s+C256)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (C32)]
trs += [(na1) + (b0 & (na1 >> 32))]
trs += [(C256) + (a0)]
trs += [(loga1) + (b0)]
trs += [(na1) + (b0)]
trs += [(a0) + (b0)]
trs += [(b1) + (loga1)]
trs += [(a1) + (C32)]
trs += [(s) + (b0)]
trs += [(b1) + (a0)]
trs += [(C32) + (b0)]
trs += [(s+C256) + (s)]
trs += [(logb1) + (loga0)]
trs += [(a1) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(rnd) + (a0*b1)]
trs += [(b0) + (a1)]
trs += [(a1) + (b1)]
trs += [(b1 & (na0 >> 32)) + (rnd)]
trs += [(C32) + (nb0 & (na0 >> 32))]
trs += [(s+C256) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(s) + (s+C256)]
trs += [(C32) + (b0 & (na0 >> 32))]
trs += [(b0 & (na0 >> 32)) + (C32)]
trs += [(b0) + (a1)]
trs += [(b0) + (loga1)]
trs += [(loga1) + (C256)]
trs += [(b0) + (a0*b1)]
trs += [((nb1 & (na1 >> 32)) >> 32) + (a1*b1)]
trs += [(s) + (b0)]
trs += [(a0) + (logb0)]
trs += [(b1 & (na0 >> 32)) + (C32)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (loga0)]
trs += [(b0 & (na0 >> 32)) + (nb0 & (na0 >> 32))]
trs += [(a0*b0) + (c1)]
trs += [(b1 & (na1 >> 32)) + (C32)]
trs += [(na0) + (b0)]
trs += [(a0*b1) + (s)]
trs += [(nb1 & (na0 >> 32)) + (s+C256)]
trs += [(s) + (logb0)]
trs += [(a0) + (na0)]
trs += [(b0) + (nb0 & (na1 >> 32))]
trs += [(s+C256) + (na1)]
trs += [(b0 & (na0 >> 32)) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(logb1) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(logb0) + (s+C256)]
trs += [(na1 >> 32) + (b1 & (na1 >> 32))]
trs += [(a0*b0) + (b0)]
trs += [(logb0) + (s)]
trs += [(a1) + (loga0)]
trs += [(s) + (logb1)]
trs += [(C32) + (s+C256)]
trs += [(loga1) + (s)]
trs += [(C256) + (s+C256)]
trs += [(s) + (a0*b1)]
trs += [(s+C256) + (((a0*b1)+rnd)+(a1*b0))]
trs += [(logb1) + (loga1)]
trs += [(s+C256) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(a1*b0) + (((a0*b1)+rnd)+(a1*b0))]
trs += [(a1) + (b0)]
trs += [(a1) + (C32)]
trs += [(C256) + (s+C256)]
trs += [(C32) + (b1)]
trs += [(logb1) + (C256)]
trs += [(s) + (b1)]
trs += [(s+C256) + (b0)]
trs += [(b0) + (loga1)]
trs += [(b1 & (na1 >> 32)) + (nb1 & (na1 >> 32))]
trs += [(b0) + (C32)]
trs += [(a0) + (b1)]
trs += [(b1) + (a0)]
trs += [(C32) + (a0*b0)]
trs += [(C256) + (a1)]
trs += [(s) + (C256)]
trs += [(s+C256) + (a0)]
trs += [(a1) + (s)]
trs += [(a0) + (b0)]
trs += [(b1) + (na1)]
trs += [(b0 & (na1 >> 32)) + (nb0 & (na1 >> 32))]
trs += [(loga1) + (s+C256)]
trs += [(loga1) + (s+C256)]
trs += [(loga0) + (s)]
trs += [(logb0) + (loga1)]
trs += [(logb0) + (C256)]
trs += [(rnd) + (logb0)]
trs += [(nb0 & (na1 >> 32)) + ((nb0 & (na1 >> 32)) >> 32)]
trs += [(C32) + (b1)]
trs += [((nb1 & (na1 >> 32)) >> 32) + (a1*b1)]
trs += [(nb0 & (na0 >> 32)) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(a0) + (b1)]
trs += [(loga1) + (s)]
trs += [(s+C256) + (b1 & (na1 >> 32))]
trs += [(b1) + (b0)]
trs += [(C32) + (b0 & (na0 >> 32))]
trs += [(b0) + (s)]
trs += [(na1) + (na1 >> 32)]
for i in range((len(trs))):
    (res, usedbitexp, time) = checkTpsVal(trs[i])
    if res:
        print("TPS Secure:\t [{:02d}] {}".format(i, trs[i]))
        pass
    else:
        print("TPS Insecure:\t [{:02d}] {}".format(i, trs[i]))
        print('!!!!!LEAKAGE FOUND!!!!!')
        pass


# Interaction leakages.
print('\nInteraction')
itl = list()
itl += [((nb0 & (na1 >> 32)) >> 32) * (a0*b1) * (nb0 & (na1 >> 32)) * (s+C256)]
itl += [(nb0 & (na1 >> 32)) * (s+C256) * (b0 & (na1 >> 32)) * (C32)]
itl += [(a1*b1) * (a1*b1) * ((nb1 & (na1 >> 32)) >> 32) * (a1*b0)]
itl += [(b1 & (na0 >> 32)) * (C32) * (C32) * (na0 >> 32)]
itl += [(b0 & (na1 >> 32)) * (C32) * (na1) * (na1 >> 32)]
itl += [(C32) * (na0 >> 32) * (C32) * (b1)]
itl += [((nb0 & (na0 >> 32)) >> 32) * (rnd) * (s+C256) * (nb0 & (na0 >> 32))]
itl += [(b1 & (na1 >> 32)) * (C32) * (na1) * (na1 >> 32)]
itl += [(nb1 & (na0 >> 32)) * (s+C256) * (b1 & (na0 >> 32)) * (C32)]
itl += [(na1) * (na1 >> 32) * (na1) * (b0)]
itl += [(b0 & (na0 >> 32)) * (C32) * (C32) * (na0 >> 32)]
itl += [(s) * (loga1) * (s) * (loga1)]
itl += [((nb1 & (na1 >> 32)) >> 32) * (a1*b0) * (s+C256) * (nb1 & (na1 >> 32))]
itl += [(s+C256) * (nb0 & (na0 >> 32)) * (s+C256) * (nb0 & (na0 >> 32))]
itl += [(rnd) * ((nb1 & (na0 >> 32)) >> 32) * (nb1 & (na0 >> 32)) * (s+C256)]
itl += [(na1) * (na1 >> 32) * (na1) * (b1)]
itl += [(C32) * (na0 >> 32) * (C32) * (b0)]
itl += [(logb0) * (logb0) * (logb0) * (logb0)]
itl += [(loga1) * (loga1) * (loga1) * (loga1)]
itl += [(s+C256) * (nb0 & (na0 >> 32)) * (b0 & (na0 >> 32)) * (C32)]
itl += [(s+C256) * (nb1 & (na1 >> 32)) * (s+C256) * (nb1 & (na1 >> 32))]
itl += [(loga0) * (loga0) * (loga0) * (loga0)]
itl += [(s+C256) * (nb1 & (na1 >> 32)) * (b1 & (na1 >> 32)) * (C32)]

for i in range((len(itl))):
    (res, usedbitexp, time) = checkTpsVal(itl[i])
    if res:
        print("TPS Secure:\t [{:02d}] {}".format(i, itl[i]))
        pass
    else:
        print("TPS Insecure:\t [{:02d}] {}".format(i, itl[i]))
        print('!!!!!LEAKAGE FOUND!!!!!')
        pass

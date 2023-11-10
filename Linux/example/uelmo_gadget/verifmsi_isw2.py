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
# Atomic variables.
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


# Compound variables.
loga0 = GLog(a0)
logb0 = GLog(b0)
loga1 = GLog(a1)
logb1 = GLog(b1)
na0 = ~a0
nb0 = ~b0
na1 = ~a1
nb1 = ~b1
a0b0 = GMul(a0, b0)
a0b1 = GMul(a0, b1)
a1b0 = GMul(a1, b0)
a1b1 = GMul(a1, b1)

s0 = loga0 + logb0
s1 = s0 + C256
s2 = GLog(s1)
s3 = GMul(a0, b0)
s4 = loga0 + logb1
s5 = s4 + C256
s6 = GLog(s5)
s7 = GMul(a0, b1)
s8 = loga1 + logb0
s9 = s8 + C256
s10 = GLog(s9)
s11 = GMul(a1, b0)
s12 = loga1 + logb1
s13 = s12 + C256
s14 = GLog(s13)
s15 = GMul(a1, b1)

c0 = a0b0 ^ rnd
c1 = ((a0b1 ^ rnd) ^ (a1b0)) ^ a1b1

# Expressions by Line number in dictionary.
exp = dict()

exp[0x02] = a0
exp[0x04] = b0
exp[0x05] = a1
exp[0x06] = b1
exp[0x07] = rnd
exp[0x09] = logb0
exp[0x0A] = loga0
exp[0x0B] = s0
exp[0x0E] = s1
exp[0x0F] = s2
exp[0x10] = na0
exp[0x11] = na0 >> 32       # -a0>>32
exp[0x12] = b0 & exp[0x11]  # b0&(-a0>>32)
exp[0x13] = ~exp[0x12]      # -b0&(-a0>>32)
exp[0x14] = exp[0x13] >> 32  # (-b0&(-a0>>32))>>32
exp[0x15] = a0b0
exp[0x17] = c0
exp[0x18] = c1
exp[0x19] = logb1
exp[0x1A] = s4
exp[0x1B] = s5
exp[0x1C] = s6
exp[0x1D] = b1 & exp[0x11]  # b1&(-a0>>32)
exp[0x1E] = ~exp[0x1D]      # -b1&(-a0>>32)
exp[0x1F] = exp[0x1E] >> 32  # (-b1&(-a0>>32))>>32
exp[0x20] = a0b0  # a0*b1
exp[0x21] = a0b1 ^ rnd       # (a0*b1) ^ rnd
exp[0x22] = loga1
exp[0x23] = s8
exp[0x24] = s9
exp[0x25] = s10
exp[0x26] = na1
exp[0x27] = na1 >> 32
exp[0x28] = b0 & exp[0x27]
exp[0x29] = ~exp[0x28]
exp[0x2A] = exp[0x29] >> 32
exp[0x2B] = s11
exp[0x2C] = exp[0x21] ^ a1b0
exp[0x2D] = s12
exp[0x2E] = s13
exp[0x2F] = s14
exp[0x30] = b1 & (na1 >> 32)
exp[0x31] = ~exp[0x30]
exp[0x32] = exp[0x31] >> 32
exp[0x33] = s15
exp[0x34] = ((a0b1 ^ rnd) ^ a1b0) ^ a1b1


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

trs += [(b0) + (a0)]
trs += [(s14) + (s15)]
trs += [(b1 & (na0 >> 32)) + (nb1 & (na0 >> 32))]
trs += [(b0 & (na0 >> 32)) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(a1) + (logb0)]
trs += [(a1) + (C32)]
trs += [((a0b1) ^ rnd) + (logb1)]
trs += [(logb1) + (s13)]
trs += [(s0) + (C256)]
trs += [(s11) + (((a0b1) ^ rnd) ^ (a1b0))]
trs += [((a0b1) ^ rnd) + (loga1)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (C32)]
trs += [(s8) + (C256)]
trs += [(na1) + (b1 & (na1 >> 32))]
trs += [(s4) + (s5)]
trs += [(loga0) + (logb1)]
trs += [(b1 & (na0 >> 32)) + (C32)]
trs += [(logb1) + (s12)]
trs += [(logb0) + (s0)]
trs += [(C256) + (a0)]
trs += [(na1) + (s9)]
trs += [(na1) + (na1 >> 32)]
trs += [(C256) + (s5)]
trs += [(logb1) + (s12)]
trs += [(s13) + (C256)]
trs += [(b1) + (logb1)]
trs += [(C32) + (b1 & (na0 >> 32))]
trs += [(b0) + (b0 & (na1 >> 32))]
trs += [(s10) + (b0)]
trs += [(C32) + (b1)]
trs += [(logb0) + (s10)]
trs += [(a0) + (b1)]
trs += [(nb1 & (na1 >> 32)) + (s14)]
trs += [(C32) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(C256) + (s1)]
trs += [(logb0) + (C256)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (rnd)]
trs += [(b0 & (na1 >> 32)) + (C32)]
trs += [(logb0) + (loga0)]
trs += [(na1) + (b1 & (na1 >> 32))]
trs += [(a1) + (loga1)]
trs += [(rnd) + (logb0)]
trs += [(a1) + (b0)]
trs += [(b1) + (loga0)]
trs += [((a0b1) ^ rnd) + (s12)]
trs += [(b1) + (s4)]
trs += [(a1) + (logb1)]
trs += [(s6) + (C32)]
trs += [((a0b1) ^ rnd) + (C256)]
trs += [((nb1 & (na1 >> 32)) >> 32) + ((((a0b1) ^ rnd) ^ (a1b0)) ^ (a1b1))]
trs += [(b0 & (na1 >> 32)) + (na1)]
trs += [(C32) + (na0 >> 32)]
trs += [(b0) + (a1)]
trs += [(s1) + (C256)]
trs += [(b0) + (b0 & (na0 >> 32))]
trs += [(b1 & (na0 >> 32)) + (nb1 & (na0 >> 32))]
trs += [(C32) + (s6)]
trs += [(s2) + (loga0)]
trs += [(b0 & (na0 >> 32)) + (s2)]
trs += [(s12) + (logb1)]
trs += [(s4) + (C256)]
trs += [(C32) + (s10)]
trs += [(logb1) + (loga0)]
trs += [(a0) + (logb0)]
trs += [(b1) + (a1)]
trs += [(C32) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(C32) + (b1)]
trs += [(C256) + (s4)]
trs += [(rnd) + ((a0b1) ^ rnd)]
trs += [(s0) + (C256)]
trs += [(s0) + (s1)]
trs += [(s4) + (C256)]
trs += [((nb1 & (na0 >> 32)) >> 32) + (a0b1)]
trs += [(loga1) + (logb1)]
trs += [(C32) + (b1)]
trs += [(s8) + (logb0)]
trs += [(s2) + (na0)]
trs += [((nb0 & (na1 >> 32)) >> 32) + (nb0 & (na1 >> 32))]
trs += [(a0) + (C32)]
trs += [(logb1) + (loga1)]
trs += [(a1) + (b0)]
trs += [(logb1) + (s12)]
trs += [(b1) + (s0)]
trs += [(b1) + (b1 & (na1 >> 32))]
trs += [(loga1) + (logb1)]
trs += [(loga0) + (s0)]
trs += [((nb0 & (na1 >> 32)) >> 32) + (b0)]
trs += [(C32) + (b0)]
trs += [(b1 & (na0 >> 32)) + (nb1 & (na0 >> 32))]
trs += [(a0b0) + (C32)]
trs += [(na1) + (b0 & (na1 >> 32))]
trs += [(na1 >> 32) + (b0 & (na1 >> 32))]
trs += [(logb0) + (loga0)]
trs += [(c0) + (a0)]
trs += [(C32) + (s2)]
trs += [(s9) + (C256)]
trs += [(nb0 & (na0 >> 32)) + (s2)]
trs += [(rnd) + (nb1 & (na0 >> 32))]
trs += [(s15) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(logb0) + (s6)]
trs += [(s6) + (a0b1)]
trs += [(C32) + (a0b0)]
trs += [(C256) + (s10)]
trs += [(nb0 & (na1 >> 32)) + ((nb0 & (na1 >> 32)) >> 32)]
trs += [(a0b1) + ((a0b1) ^ rnd)]
trs += [(s6) + (C32)]
trs += [(s4) + (C256)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (loga0)]
trs += [(na0) + (b0 & (na0 >> 32))]
trs += [(a0) + (b1)]
trs += [(b1 & (na0 >> 32)) + (na0)]
trs += [(s2) + (a0b0)]
trs += [(na0 >> 32) + (b1 & (na0 >> 32))]
trs += [(s6) + (loga1)]
trs += [(C32) + (s6)]
trs += [(s1) + (s2)]
trs += [(s10) + ((a0b1) ^ rnd)]
trs += [((nb0 & (na1 >> 32)) >> 32) + (s11)]
trs += [(nb1 & (na0 >> 32)) + ((nb1 & (na0 >> 32)) >> 32)]
trs += [(C256) + (s0)]
trs += [(nb0 & (na1 >> 32)) + (b0 & (na1 >> 32))]
trs += [(rnd) + (c0)]
trs += [(logb1) + (C256)]
trs += [(logb0) + (rnd)]
trs += [(C32) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(na0) + (b0 & (na0 >> 32))]
trs += [(logb1) + (C256)]
trs += [(b1 & (na1 >> 32)) + (b1)]
trs += [(a1) + (s8)]
trs += [(na0 >> 32) + (nb1 & (na0 >> 32))]
trs += [(s8) + (C256)]
trs += [(b0) + (loga1)]
trs += [(nb0 & (na1 >> 32)) + ((nb0 & (na1 >> 32)) >> 32)]
trs += [((a0b1) ^ rnd) + (s10)]
trs += [(b0) + (b0 & (na0 >> 32))]
trs += [(s14) + (s13)]
trs += [(s0) + (s1)]
trs += [(logb0) + (b1)]
trs += [(C256) + (s2)]
trs += [((nb0 & (na1 >> 32)) >> 32) + (s11)]
trs += [((nb1 & (na1 >> 32)) >> 32) + ((((a0b1) ^ rnd) ^ (a1b0)) ^ (a1b1))]
trs += [(a0) + (b1)]
trs += [(C32) + (b0)]
trs += [(a1) + (b1)]
trs += [(rnd) + (a1)]
trs += [(logb1) + (b0)]
trs += [(s14) + (b1 & (na1 >> 32))]
trs += [(nb0 & (na1 >> 32)) + ((nb0 & (na1 >> 32)) >> 32)]
trs += [(a1) + (s12)]
trs += [(s8) + (C256)]
trs += [((nb1 & (na1 >> 32)) >> 32) + (s15)]
trs += [(logb1) + (s6)]
trs += [(loga0) + (logb0)]
trs += [(a1) + (s6)]
trs += [(c0) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(b1) + (logb1)]
trs += [(logb0) + (b0)]
trs += [(logb1) + (s4)]
trs += [(s14) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(loga1) + (logb0)]
trs += [(((a0b1) ^ rnd) ^ (a1b0)) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(nb1 & (na0 >> 32)) + (b1 & (na0 >> 32))]
trs += [(((a0b1) ^ rnd) ^ (a1b0)) + ((((a0b1) ^ rnd) ^ (a1b0)) ^ (a1b1))]
trs += [(s4) + (logb1)]
trs += [(s9) + (a1)]
trs += [(b0) + ((nb0 & (na1 >> 32)) >> 32)]
trs += [((a0b1) ^ rnd) + (a1)]
trs += [(C256) + (s5)]
trs += [(s5) + (na0)]
trs += [(logb1) + (s14)]
trs += [(logb0) + (b0)]
trs += [(logb1) + (C256)]
trs += [(a0) + (na0)]
trs += [(b0 & (na0 >> 32)) + (nb0 & (na0 >> 32))]
trs += [(a0b0) + (c0)]
trs += [(s10) + (loga1)]
trs += [(nb1 & (na0 >> 32)) + (rnd)]
trs += [(a1) + (b0)]
trs += [((((a0b1) ^ rnd) ^ (a1b0)) ^ (a1b1)) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(b0) + (b0 & (na1 >> 32))]
trs += [(s12) + (s13)]
trs += [(s5) + (a0)]
trs += [(logb0) + (s10)]
trs += [(C256) + (b0)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (c0)]
trs += [(b1) + (loga0)]
trs += [(s0) + (C256)]
trs += [(C32) + (a1)]
trs += [(s10) + (loga1)]
trs += [(s2) + (C32)]
trs += [(b1 & (na1 >> 32)) + (C32)]
trs += [(s1) + (na0)]
trs += [(nb1 & (na1 >> 32)) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(s9) + (C256)]
trs += [(a0) + (rnd)]
trs += [(s6) + (logb0)]
trs += [(nb0 & (na1 >> 32)) + ((nb0 & (na1 >> 32)) >> 32)]
trs += [(loga0) + (logb1)]
trs += [(rnd) + (b1)]
trs += [(logb1) + (s6)]
trs += [(C32) + (s10)]
trs += [(((a0b1) ^ rnd) ^ (a1b0)) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(C32) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(na0) + (na0 >> 32)]
trs += [(b1 & (na1 >> 32)) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [((nb1 & (na0 >> 32)) >> 32) + (rnd)]
trs += [(s2) + (loga0)]
trs += [(logb1) + (s13)]
trs += [(s8) + (s9)]
trs += [(na0) + (b1 & (na0 >> 32))]
trs += [(s6) + (logb0)]
trs += [(na1) + (na1 >> 32)]
trs += [(b1 & (na0 >> 32)) + (C32)]
trs += [(nb1 & (na0 >> 32)) + ((nb1 & (na0 >> 32)) >> 32)]
trs += [(nb1 & (na0 >> 32)) + (a0b1)]
trs += [(loga0) + (logb1)]
trs += [(logb0) + (s8)]
trs += [((nb1 & (na1 >> 32)) >> 32) + (C32)]
trs += [(C32) + (b0)]
trs += [(s8) + (C256)]
trs += [(loga0) + (s2)]
trs += [(a0b1) + (s6)]
trs += [(s5) + (a0)]
trs += [(logb1) + (s12)]
trs += [(b1 & (na0 >> 32)) + (b1)]
trs += [(s14) + (s15)]
trs += [(C32) + (b0 & (na0 >> 32))]
trs += [(s5) + (C256)]
trs += [(na0 >> 32) + (b0 & (na0 >> 32))]
trs += [(s9) + (na1)]
trs += [(b1) + (rnd)]
trs += [(s6) + (a0b1)]
trs += [(b0 & (na1 >> 32)) + (b0)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (s2)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (a0b0)]
trs += [(b1) + (a0)]
trs += [(loga1) + (logb0)]
trs += [(s13) + (na1)]
trs += [(b0 & (na1 >> 32)) + (nb0 & (na1 >> 32))]
trs += [(s12) + (C256)]
trs += [(b0) + (a0)]
trs += [(logb0) + (loga0)]
trs += [(b0) + (C32)]
trs += [(C256) + (s13)]
trs += [(b1) + (loga0)]
trs += [(b0 & (na0 >> 32)) + (b0)]
trs += [(logb1) + (b1)]
trs += [(na0) + (b1 & (na0 >> 32))]
trs += [(logb0) + (C32)]
trs += [(b0) + (a1)]
trs += [(C256) + (s9)]
trs += [(loga0) + (logb1)]
trs += [(logb0) + (loga0)]
trs += [(C32) + (C256)]
trs += [(a0b1) + (rnd)]
trs += [(C256) + (a0)]
trs += [(C256) + (s6)]
trs += [(logb1) + (s14)]
trs += [(b0 & (na1 >> 32)) + (C32)]
trs += [(s0) + (logb0)]
trs += [(logb0) + (s8)]
trs += [(s15) + ((((a0b1) ^ rnd) ^ (a1b0)) ^ (a1b1))]
trs += [(C256) + (s5)]
trs += [(s10) + (loga1)]
trs += [(logb1) + ((a0b1) ^ rnd)]
trs += [(s4) + (C256)]
trs += [(logb0) + (C256)]
trs += [(loga0) + (logb1)]
trs += [(na1) + (b0 & (na1 >> 32))]
trs += [(s13) + (logb1)]
trs += [(b0 & (na1 >> 32)) + (nb0 & (na1 >> 32))]
trs += [(b1 & (na1 >> 32)) + (nb1 & (na1 >> 32))]
trs += [(logb0) + (C256)]
trs += [(s6) + (a0)]
trs += [(b1) + (logb1)]
trs += [(s10) + (logb1)]
trs += [(loga1) + (logb1)]
trs += [(s13) + (na1)]
trs += [(loga1) + (logb1)]
trs += [(s2) + (b0 & (na0 >> 32))]
trs += [(loga0) + (logb1)]
trs += [((nb0 & (na1 >> 32)) >> 32) + (s11)]
trs += [(b1) + (loga1)]
trs += [(s14) + (na1)]
trs += [(na0 >> 32) + (nb0 & (na0 >> 32))]
trs += [(nb0 & (na0 >> 32)) + ((nb0 & (na0 >> 32)) >> 32)]
trs += [(s2) + (a0b0)]
trs += [(b1 & (na1 >> 32)) + (s14)]
trs += [(s12) + (s13)]
trs += [(a0) + (na0)]
trs += [(a0) + (C32)]
trs += [(s1) + (a0)]
trs += [(C32) + (b0 & (na1 >> 32))]
trs += [(a1) + (b1)]
trs += [(s6) + (loga1)]
trs += [(C256) + (a0)]
trs += [(s14) + (b1 & (na1 >> 32))]
trs += [(b1) + (b1 & (na0 >> 32))]
trs += [(logb1) + (s14)]
trs += [(b0) + (s10)]
trs += [(b0) + (logb0)]
trs += [(s8) + (s9)]
trs += [(a0b1) + (s6)]
trs += [((nb1 & (na1 >> 32)) >> 32) + (((a0b1) ^ rnd) ^ (a1b0))]
trs += [(C32) + (b1 & (na1 >> 32))]
trs += [(C256) + (s1)]
trs += [(loga0) + (logb0)]
trs += [(b0 & (na1 >> 32)) + (nb0 & (na1 >> 32))]
trs += [(na0) + (s2)]
trs += [(s5) + (C256)]
trs += [(b1) + (C32)]
trs += [(C32) + (C256)]
trs += [(b0) + (a1)]
trs += [(s6) + (logb0)]
trs += [(b1) + (rnd)]
trs += [(b0 & (na0 >> 32)) + (C32)]
trs += [(s12) + (C256)]
trs += [(rnd) + (b1)]
trs += [(s9) + (na1)]
trs += [(s10) + (C32)]
trs += [(na1 >> 32) + (nb0 & (na1 >> 32))]
trs += [((a0b1) ^ rnd) + (a1)]
trs += [(a1) + (C32)]
trs += [(rnd) + (a0b1)]
trs += [(logb1) + (s4)]
trs += [(s1) + (C256)]
trs += [(logb0) + (C32)]
trs += [(b1) + (b1 & (na0 >> 32))]
trs += [(loga1) + (logb1)]
trs += [(logb1) + (s4)]
trs += [((a0b1) ^ rnd) + (logb1)]
trs += [(c0) + (a0b0)]
trs += [(loga1) + (s10)]
trs += [(s4) + (s5)]
trs += [(logb1) + (loga0)]
trs += [(b0 & (na0 >> 32)) + (s2)]
trs += [(rnd) + (logb0)]
trs += [(C256) + (s8)]
trs += [(((a0b1) ^ rnd) ^ (a1b0)) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(loga1) + (logb1)]
trs += [(s11) + (((a0b1) ^ rnd) ^ (a1b0))]
trs += [(logb0) + (C256)]
trs += [(s6) + (b0)]
trs += [(logb0) + (s8)]
trs += [(a0) + (b0)]
trs += [(rnd) + (logb0)]
trs += [(C256) + (s1)]
trs += [(na1 >> 32) + (nb1 & (na1 >> 32))]
trs += [(C256) + (a1)]
trs += [(s10) + ((a0b1) ^ rnd)]
trs += [(b1 & (na1 >> 32)) + (na1)]
trs += [(b1) + (a1)]
trs += [(na1) + (s13)]
trs += [(s1) + (C256)]
trs += [(a1) + (b1)]
trs += [(b1 & (na1 >> 32)) + (C32)]
trs += [(b0) + (s6)]
trs += [(s6) + (a0b1)]
trs += [(s5) + (a0)]
trs += [(C256) + (s9)]
trs += [(b0) + (a0)]
trs += [(C256) + (s1)]
trs += [((nb0 & (na0 >> 32)) >> 32) + (a0b0)]
trs += [((((a0b1) ^ rnd) ^ (a1b0)) ^ (a1b1)) + ((nb1 & (na1 >> 32)) >> 32)]
trs += [(a1) + (b1)]
trs += [(b0 & (na0 >> 32)) + (C32)]
trs += [(b0 & (na0 >> 32)) + (na0)]
trs += [(na1 >> 32) + (b1 & (na1 >> 32))]
trs += [(s10) + (b0)]
trs += [(C32) + (a1)]
trs += [(a1) + (logb1)]
trs += [(C256) + (s9)]
trs += [(C256) + (s13)]
trs += [(s12) + (C256)]
trs += [(logb0) + (s6)]
trs += [(s13) + (a1)]
trs += [(loga0) + (s0)]
trs += [(s6) + (logb0)]
trs += [(a0b0) + (c0)]
trs += [(b1) + (b1 & (na1 >> 32))]
trs += [(s6) + (logb0)]
trs += [(logb1) + (loga1)]
trs += [(a0) + (b0)]
trs += [(loga0) + (s2)]
trs += [(na0) + (C32)]
trs += [(a0b1) + (a1)]
trs += [(a0) + (b0)]
trs += [(a1) + (logb0)]
trs += [(a0b1) + (s6)]

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

itl += [(s2) * ((nb0 & (na0 >> 32)) >> 32) * (nb0 & (na0 >> 32)) * (C32)]
itl += [(s2) * ((nb0 & (na0 >> 32)) >> 32) *
        (s2) * ((nb0 & (na0 >> 32)) >> 32)]
itl += [(logb0) * (logb0) * (logb0) * (logb0)]
itl += [(s14) * ((nb1 & (na1 >> 32)) >> 32) *
        (s14) * ((nb1 & (na1 >> 32)) >> 32)]
itl += [(loga0) * (logb0) * (loga0) * (logb0)]
itl += [(s11) * ((a0b1) ^ rnd) * ((nb0 & (na1 >> 32)) >> 32) * (s10)]
itl += [(na0 >> 32) * (b1) * (na0) * (C32)]
itl += [((nb1 & (na0 >> 32)) >> 32) * (s6) * (nb1 & (na0 >> 32)) * (C32)]
itl += [((nb0 & (na1 >> 32)) >> 32) * (s10) * (nb0 & (na1 >> 32)) * (C32)]
itl += [(nb0 & (na0 >> 32)) * (C32) * (na0 >> 32) * (b0 & (na0 >> 32))]
itl += [(s12) * (C256) * (logb1) * (logb1)]
itl += [(na0 >> 32) * (b1 & (na0 >> 32)) * (na0 >> 32) * (b1)]
itl += [(logb1) * (logb1) * (logb1) * (logb1)]
itl += [(na0 >> 32) * (b0) * (na0) * (C32)]
itl += [(s15) * (((a0b1) ^ rnd) ^ (a1b0)) *
        (s14) * ((nb1 & (na1 >> 32)) >> 32)]
itl += [(na1 >> 32) * (b1 & (na1 >> 32)) * (na1 >> 32) * (b1)]
itl += [(a0b0) * (rnd) * (s2) * ((nb0 & (na0 >> 32)) >> 32)]
itl += [(s0) * (C256) * (loga0) * (logb0)]
itl += [((nb1 & (na1 >> 32)) >> 32) * ((((a0b1) ^ rnd) ^ (a1b0)) ^ (a1b1))
        * ((nb1 & (na1 >> 32)) >> 32) * ((((a0b1) ^ rnd) ^ (a1b0)) ^ (a1b1))]
itl += [(na0) * (C32) * (a0) * (a0)]
itl += [(rnd) * (a0b1) * ((nb1 & (na0 >> 32)) >> 32) * (s6)]
itl += [(na1 >> 32) * (b1) * (na1) * (C32)]
itl += [(s14) * ((nb1 & (na1 >> 32)) >> 32) * (nb1 & (na1 >> 32)) * (C32)]
itl += [(nb1 & (na0 >> 32)) * (C32) * (na0 >> 32) * (b1 & (na0 >> 32))]
itl += [(na1 >> 32) * (b0) * (na1) * (C32)]
itl += [(nb1 & (na1 >> 32)) * (C32) * (na1 >> 32) * (b1 & (na1 >> 32))]
itl += [(s4) * (C256) * (logb1) * (logb1)]
itl += [(na1 >> 32) * (b0 & (na1 >> 32)) * (na1 >> 32) * (b0)]
itl += [(s8) * (C256) * (logb0) * (logb0)]
itl += [(na0 >> 32) * (b0 & (na0 >> 32)) * (na0 >> 32) * (b0)]
itl += [(nb0 & (na1 >> 32)) * (C32) * (na1 >> 32) * (b0 & (na1 >> 32))]

for i in range((len(itl))):
    (res, usedbitexp, time) = checkTpsVal(itl[i])
    if res:
        print("TPS Secure:\t [{:02d}] {}".format(i, itl[i]))
        pass
    else:
        print("TPS Insecure:\t [{:02d}] {}".format(i, itl[i]))
        print('!!!!!LEAKAGE FOUND!!!!!')
        pass

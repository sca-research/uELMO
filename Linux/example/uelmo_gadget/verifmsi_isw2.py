from VerifMSI import *

'''
# Not in FAET
a = symbol('a', 'S', 32)
b = symbol('b', 'S', 32)


# Shares used in FAET
a0, a1 = getRealShares(a, 2)
b0, b1 = getRealShares(b, 2)
'''
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


# Expressions by Line number in dictionary.
exp = dict()
exp[0] = c0
exp[1] = c1
exp[0x11] = na0 >> 32       # -a0>>32
exp[0x12] = b0 & exp[0x11]  # b0&(-a0>>32)
exp[0x13] = ~exp[0x12]      # -b0&(-a0>>32)
exp[0x14] = exp[0x13] >> 32  # (-b0&(-a0>>32))>>32
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
for i in exp:
    res = checkTpsVal(exp[i])
    if res:
        print('{:02d}: {}\n is TPS secure'.format(i, exp[i]))
        pass
    else:
        print('{:02d}: {}\n is TPS insecure'.format(i, exp[i]))
        pass


'''
# For Gate-style description.
order = 2
withGlitches = True
print(checkSecurity(order, withGlitches, 'ni', exp[0x2A]))
'''

# Verfification script. **ONLY** used as input to generation script.
for i in range(len(frameexp)):
    se = simplify(frameexp[i])
    print("Frame[{}] : {}".format(i, se))
    res = checkTpsVal(se)
    if res[0] is not True:
        print("!!!!!!LEAKAGE DETECTED!!!!!!")
        pass
    pass

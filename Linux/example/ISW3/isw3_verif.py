for i in range(len(frameexp)):
    se = simplify(frameexp[i])
    print("Frame[{:d}] : {:s}".format(i, se))
    res = checkTpsVal(se)
    if res[0] is not True:
        print("!!!!!!LEAKAGE DETECTED!!!!!!")
        pass
    pass

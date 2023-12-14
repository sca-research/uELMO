# Verfification script. **ONLY** used as input to generation script.
# List of indexes of expressions to verify.
targetexp = range(len(frameexp))  

# Thread pool for all verifications.
threadpool = [None for i in range(len(targetexp))]
pool = multiprocessing.Pool()

# Fire the threads.
print("#Starting the verifications...")
for i in tqdm.tqdm(range(len(threadpool))):
    frameid = targetexp[i]
    e = frameexp[frameid]
    threadpool[i] = pool.apply_async(checkTpsVal, (e,))
    pass

# Collect the results.
print("#Collecting the results...")
result = [None for i in range(len(threadpool))]
for i in tqdm.tqdm(range(len(threadpool))):
    res = threadpool[i].get()
    result[i] = res
    pass

# Print results.
for i in range(len(result)):
    res = result[i]
    frameid = targetexp[i]
    exp = frameexp[frameid]

    print("#Frame[{}]: ".format(frameid), end='')

    if res[0] == False:
        print("!!!LEAKAGE FOUNE!!!")
        print(exp)
        pass
    else:
        print("Passed")
        pass
    pass

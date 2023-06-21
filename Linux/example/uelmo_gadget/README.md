Author: Nima Mahdion

An ISW-2 implementatoin.

**GADGET_NAME** = {Isw_2, Isw_3, Dom_indep_2, Dom_indep_3, HPC1_opt_2, HPC1_opt_3, Pini1_2, Pini2_2};


 1) Please set a name for **GADGET_NAME**  in the line 100 in uelmo_gadget.c 
 
```GADGET_NAME(shares_a, shares_b, rnd, shares_ab);```


 2) and also in uelmo_gadget.S
 
```
.global GADGET_NAME
.func GADGET_NAME
GADGET_NAME:
```

3) Put the right values in uelmo_gadget.c

```
int share_n = 2;
int rnd_n = 1;
```

4) Put your code in uelmo_gadget.S in part:
```
########################################################

@@@@@@ Put your code here

########################################################
```


5) From **uelmo_general_gadgets** directory, run:
```
make clean
make
```


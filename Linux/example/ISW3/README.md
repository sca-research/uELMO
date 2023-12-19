ISW-3 implementation by Nima Mahdion

*Source code:*

uelmo_gadget.c: main entry.

uelmo_gadget.S: Assembly implementation of ISW-3 gadget.

*SEALIB related files*

isw3_fa.set: Fully annotated script of the ISW-3 gadget.

isw3_fa.set.sdc: Dictionary file for isw3_fa.set.

isw3.lkg.json: Extracted leakage of ISW-3 with all terms.


*Inside verfmsi folder*

This folder contains files related to use VerifMSI to prove this ISW-3.

dicttoverifmsi.py: Script to process original dictinoary file into VerifMSI syntax.

isw3_genscript.py: Script to automatically generate executable VerifMSI Python script.

isw3_init.py: Initialisation Python script to generate executable VerifMSI. Should only be used as input to isw3_genscript.py.

isw3_verif.py: Verification Python script to generate executable VerifMSI. Should only be used as input to isw3_genscript.py.

verifmsi_isw3_fa.set.sdc: Dictionary file for isw3_fa.set in VerifMSI syntax.

verifmsi_isw3.lkg.json: Extracted leakage of ISW-3 with all terms in VerifMSI syntax.

verifmsi_isw3_reduced.lkg.json: Extracted leakage of ISW-3 with reduced terms.

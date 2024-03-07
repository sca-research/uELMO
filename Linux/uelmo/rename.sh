#!/bin/bash

TARGET=$@

for i in ${TARGET}
do
    echo ${i};
    sed -i 's/SMURF/SEAL/g' ${i};
    sed -i 's/Smurf/Seal/g' ${i};
    sed -i 's/smurf/seal/g' ${i};
done

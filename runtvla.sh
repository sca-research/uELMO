#!/bin/bash -x

N=100
PORT="/tmp/uelmoport"
WAIT="0.1"
OUTPUT="./tvla/"
BIN="examples/TVLA_MaskedAES/MaskedAesFull.bin"
FIXED_CLIENT="python3 examples/TVLA_MaskedAES/client.py -e -w ${WAIT} -n ${N} -p ${PORT}"
RANDOM_CLIENT="python3 examples/TVLA_MaskedAES/client.py -e -w ${WAIT} -r -n ${N} -p ${PORT}"
EXTRACTOR="LeakageExtractor/elmo.py"
METHOD='ttest'

python3 tvla.py ${BIN} -p ${PORT} \
    -f ' '"${FIXED_CLIENT}"' ' \
    -r ' '"${RANDOM_CLIENT}"' ' \
    -le ${EXTRACTOR} \
    -d ${OUTPUT} \
    -m ${METHOD} \

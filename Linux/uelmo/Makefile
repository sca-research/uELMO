TARGET=uelmo
CFLAGS=-g -Wall -O2
SMURFFLAGS=-lsmurf -lsmurfemulator -DUSE_SMURF
SMURFLPATHFLAGS=-L${HOME}/.local/lib/ -I${HOME}/.local/header/


all: ${TARGET} Makefile

${TARGET}: $(wildcard *.c *.h)
	${CC} ${CFLAGS} -c $^ 
	${CC} ${CFLAGS} *.o -o $@

smuelmo: $(wildcard *.c *.h)
	${CC} ${CFLAGS} -c $^ -DUSE_SMURF #-DDBG
	${CC} ${CFLAGS} ${SMURFLPATHFLAGS} *.o -o $@ ${SMURFFLAGS} -DUSE_SMURF #-DDBG

clean:
	rm -f *.o *~ *.bak ${TARGET} smuelmo

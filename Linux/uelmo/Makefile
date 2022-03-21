TARGET=uelmo
CFLAGS=-g -Wall -O2
SMURFFLAGS=-lsmurf -lsmurfemulator -DUSE_SMURF
SMURFLPATHFLAGS=-L${HOME}/.local/lib/ -I${HOME}/.local/header/


all: ${TARGET} Makefile

${TARGET}: $(wildcard *.c)
	${CC} ${CFLAGS} -c $^ 
	${CC} ${CFLAGS} *.o -o $@

smuelmo: $(wildcard *.c)
	${CC} ${CFLAGS} -c $^ -DUSE_SMURF
	${CC} ${CFLAGS} ${SMURFLPATHFLAGS} *.o -o $@ ${SMURFFLAGS} -DUSE_SMURF

clean:
	rm -f *.o *~ *.bak ${TARGET} smuelmo

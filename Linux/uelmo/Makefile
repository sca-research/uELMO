TARGET=uelmo
CFLAGS=-g -Wall -O2
SMURFFLAGS=-lsmurf -lsmurfemulator -DUSE_SMURF
SMURFLPATHFLAGS=-L${HOME}/.local/lib/ -I${HOME}/.local/header/


all: ${TARGET} Makefile

${TARGET}: $(wildcard *.c)
	${CC} ${CFLAGS} -c $^ 
	${CC} ${CFLAGS} *.o -o $@

uelmorf: $(wildcard *.c)
	${CC} ${CFLAGS} -c $^ 
	${CC} ${CFLAGS} ${SMURFLPATHFLAGS} *.o -o $@ ${SMURFFLAGS} 

clean:
	rm -f *.o *~ *.bak ${TARGET} uelmorf

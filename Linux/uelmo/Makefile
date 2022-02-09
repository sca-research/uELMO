TARGET=uelmo
CFLAGS=-g -Wall -O2
SMURFFLAGS=-lsmurf -lsmurfemulator -DUSE_SMURF
all: ${TARGET} Makefile

${TARGET}: $(wildcard *.c)
	${CC} ${CFLAGS} -c $^ 
	${CC} ${CFLAGS} *.o -o $@

smurf: $(wildcard *.c)
	${CC} ${CFLAGS} -c $^ 
	${CC} ${CFLAGS} *.o -o $@ ${SMURFFLAGS}

clean:
	rm -f *.o *~ *.bak ${TARGET}

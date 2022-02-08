TARGET=uelmo
LIBFLAGS=-lsmurf -lsmurfemulator
CFLAGS=-g -Wall -O2

all: ${TARGET}

${TARGET}: $(wildcard *.c)
	${CC} ${CFLAGS} -c $^ 
	${CC} ${CFLAGS} -DUSE_SMURF *.o -o $@ ${LIBFLAGS}
clean:
	rm -f *.o *~ *.bak ${TARGET}

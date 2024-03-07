TARGET=uelmo
CFLAGS=-g -Wall -O2
SEALFLAGS=-lseal -lsealemulator -lsealscript -DUSE_SEAL
SEALLPATHFLAGS=-L${HOME}/.local/lib/ -I${HOME}/.local/header/


all: ${TARGET} Makefile

${TARGET}: $(wildcard *.c *.h)
	${CC} ${CFLAGS} -c $^ 
	${CC} ${CFLAGS} *.o -o $@

smuelmo: $(wildcard *.c *.h)
	${CC} ${CFLAGS} -c $^ -DUSE_SEAL #-DDBG
	${CC} ${CFLAGS} ${SEALLPATHFLAGS} *.o -o $@ ${SEALFLAGS} -DUSE_SEAL #-DDBG

clean:
	rm -f *.o *~ *.bak ${TARGET} smuelmo *.gch

ctags:
	ctags -R *

indent:
	indent *.c *.h

TARGET=sealuelmo
CFLAGS=-g -Wall -O2
SEALFLAGS=-lseal -lsealemulator -lsealscript -DUSE_SEAL
SEALLPATHFLAGS=-L${HOME}/.local/lib/ -I${HOME}/.local/header/


all: ${TARGET} Makefile

uelmo: $(wildcard *.c *.h)
	${CC} ${CFLAGS} -c $^ 
	${CC} ${CFLAGS} *.o -o $@

sealuelmo: $(wildcard *.c *.h)
	${CC} ${CFLAGS} -c $^ -DUSE_SEAL #-DDBG
	${CC} ${CFLAGS} ${SEALLPATHFLAGS} *.o -o $@ ${SEALFLAGS} -DUSE_SEAL #-DDBG

clean:
	rm -f *.o *~ *.bak uelmo sealuelmo *.gch

ctags:
	ctags -R *

indent:
	indent *.c *.h

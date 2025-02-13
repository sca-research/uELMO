#SEAL library.
TARGET=sealuelmo

#Compilation setup.
LIBS=seal
LDLIBS=$(LIBS:%=-l%)
SEAL_LD_PATH=${HOME}/.local/lib
SEAL_INCLUDE_PATH=${HOME}/.local/include
OBJFLAGS=-g -Wall -c -O2 -DUSE_SEAL -I${SEAL_INCLUDE_PATH}

#Files
SRC:=$(wildcard *.c)
OBJ:=$(SRC:.c=.o)


all: ${TARGET}

%.o: %.c %.h Makefile
	${CC} ${OBJFLAGS} $<

${TARGET}: ${OBJ}
	${CC} $^ -o $@ -L${SEAL_LD_PATH} -lseal


#Project management.
clean:
	rm -f *.o *.so *~ *.a .*.swp

rebuild:
	make clean;
	make;

indent:
	indent *.c *.h
	mkdir -p backup
	mv *~ backup

ctags:
	ctags *.c *.h

submit: indent ctags
	git status

all:
	${MAKE} -C src

clean:
	${MAKE} -C src clean

rebuild: clean all

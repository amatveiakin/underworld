CC=gcc
CFLAGS=-Wall

all: filter.so launcher

include syscall-reporter.mk

filter.so: filter.o syscall-reporter.o
	ld -shared $^ -o $@ -soname $@ -init init_filter

launcher: launcher.o
	g++ launcher.o -o launcher

launcher.o: launcher.cpp
	g++ -c -o launcher.o launcher.cpp -std=c++11

.PHONY: clean
clean:
	rm -f filter filter.o syscall-reporter.o syscall-names.h launcher launcher.o

.PHONY: install
install:
	./setcap
	cp filter.so sandbox/

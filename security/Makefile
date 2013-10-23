CC=gcc
CFLAGS=-Wall

all: filter.so launcher

include syscall-reporter.mk

filter.so: filter.o syscall-reporter.o
	ld -shared $^ -o $@ -soname $@ -init init_filter

launcher: launcher.o

.PHONY: clean
clean:
	rm -f filter filter.o syscall-reporter.o syscall-names.h launcher launcher.o

.PHONY: install
install:
	sudo setcap cap_setuid,cap_sys_chroot+ep launcher
	cp filter.so sandbox/

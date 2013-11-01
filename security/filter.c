/*
 * seccomp example with syscall reporting
 *
 * Copyright (c) 2012 The Chromium OS Authors <chromium-os-dev@chromium.org>
 * Authors:
 *  Kees Cook <keescook@chromium.org>
 *  Will Drewry <wad@chromium.org>
 *
 * Use of this source code is governed by a BSD-style license that can be
 * found in the LICENSE file.
 */
#define _GNU_SOURCE 1
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/resource.h>

#include "seccomp-bpf.h"
#include "syscall-reporter.h"

static int install_syscall_filter(void)
{
	struct sock_filter filter[] = {
		/* Validate architecture. */
		VALIDATE_ARCHITECTURE,
		/* Grab the system call number. */
		EXAMINE_SYSCALL,
		/* List allowed syscalls. */
		ALLOW_SYSCALL(rt_sigreturn),
#ifdef __NR_sigreturn
		ALLOW_SYSCALL(sigreturn),
#endif
		ALLOW_SYSCALL(exit_group),
		ALLOW_SYSCALL(exit),
		ALLOW_SYSCALL(read),
		ALLOW_SYSCALL(write),
		ALLOW_SYSCALL(fstat64),
        ALLOW_SYSCALL(mmap2),
        ALLOW_SYSCALL(open),
        ALLOW_SYSCALL(close),
        ALLOW_SYSCALL(ioctl),
        ALLOW_SYSCALL(brk),
        ALLOW_SYSCALL(futex),
        ALLOW_SYSCALL(stat64),
        ALLOW_SYSCALL(readlink),
        ALLOW_SYSCALL(munmap),
        ALLOW_SYSCALL(sigaltstack),
        ALLOW_SYSCALL(openat),
        ALLOW_SYSCALL(getdents64),
        ALLOW_SYSCALL(_llseek),
        ALLOW_SYSCALL(rt_sigaction),
        ALLOW_SYSCALL(dup),
        ALLOW_SYSCALL(getcwd),
        ALLOW_SYSCALL(geteuid32),
        ALLOW_SYSCALL(getegid32),
        ALLOW_SYSCALL(getuid32),
        ALLOW_SYSCALL(getgid32),
        ALLOW_SYSCALL(lstat64),
        ALLOW_SYSCALL(access),
        ALLOW_SYSCALL(mprotect),
        ALLOW_SYSCALL(time),
        ALLOW_SYSCALL(getpid),
        ALLOW_SYSCALL(prlimit64),
        ALLOW_SYSCALL(getrusage),
        ALLOW_SYSCALL(gettimeofday),
        ALLOW_SYSCALL(rt_sigprocmask),
        ALLOW_SYSCALL(pipe),
        ALLOW_SYSCALL(fcntl64),
        ALLOW_SYSCALL(uname),
        ALLOW_SYSCALL(getppid),
        ALLOW_SYSCALL(_newselect),

		/* Add more syscalls here. */
		KILL_PROCESS,
	};
	struct sock_fprog prog = {
		.len = (unsigned short)(sizeof(filter)/sizeof(filter[0])),
		.filter = filter,
	};

	if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) {
		perror("prctl(NO_NEW_PRIVS)");
		goto failed;
	}
	if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog)) {
		perror("prctl(SECCOMP)");
		goto failed;
	}
	return 0;

failed:
	if (errno == EINVAL)
		fprintf(stderr, "SECCOMP_FILTER is not available. :(\n");
	return 1;
}

int init_filter(int argc, char *argv[])
{
    struct rlimit lim;
    lim.rlim_cur = lim.rlim_max = 1;
    setrlimit(RLIMIT_NPROC, &lim);
	if (install_syscall_reporter())
		return 1;
	if (install_syscall_filter())
		return 1;
	return 0;
}

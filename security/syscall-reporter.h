/*
 * syscall reporting example for seccomp
 *
 * Copyright (c) 2012 The Chromium OS Authors <chromium-os-dev@chromium.org>
 * Authors:
 *  Kees Cook <keescook@chromium.org>
 *  Will Drewry <wad@chromium.org>
 *
 * Use of this source code is governed by a BSD-style license that can be
 * found in the LICENSE file.
 */
#ifndef _BPF_REPORTER_H_
#define _BPF_REPORTER_H_

#include "seccomp-bpf.h"

#undef KILL_PROCESS
#define KILL_PROCESS \
		BPF_STMT(BPF_RET+BPF_K, SECCOMP_RET_TRAP)

extern int install_syscall_reporter(void);

#endif

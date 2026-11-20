#!/usr/bin/env python3
"""Trusted launcher: make hidden answers unreadable and confine state to a call.

Linux Landlock rules are inherited across exec and cannot be removed by the
encoder. No restriction is placed on the encoder's algorithm or learned assets.
"""
import ctypes
import os
from pathlib import Path
import sys


def main():
    workspace = Path(__file__).resolve().parents[2]
    call = Path(sys.argv[1]).resolve()
    command = sys.argv[2:]
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    abi = libc.syscall(444, 0, 0, 1)
    if abi < 1:
        raise RuntimeError('Linux Landlock required: refusing to expose evaluation answers')
    # execute, write_file, read_file, read_dir, remove*, make*, refer, truncate
    handled = (1 << (15 if abi >= 3 else 14 if abi >= 2 else 13)) - 1

    class Ruleset(ctypes.Structure):
        _fields_ = [('handled_access_fs', ctypes.c_uint64)]

    class PathRule(ctypes.Structure):
        _pack_ = 1
        _fields_ = [('allowed_access', ctypes.c_uint64), ('parent_fd', ctypes.c_int32)]

    attr = Ruleset(handled)
    ruleset = libc.syscall(444, ctypes.byref(attr), ctypes.sizeof(attr), 0)
    if ruleset < 0:
        raise OSError(ctypes.get_errno(), 'landlock_create_ruleset')

    def allow(path, access):
        p = Path(path).resolve()
        if not p.exists():
            return
        fd = os.open(p, os.O_PATH | os.O_CLOEXEC)
        try:
            if not p.is_dir():
                access &= (1 << 0) | (1 << 1) | (1 << 2) | (1 << 14)
            rule = PathRule(access & handled, fd)
            if libc.syscall(445, ruleset, 1, ctypes.byref(rule), 0) < 0:
                raise OSError(ctypes.get_errno(), f'landlock_add_rule {p}')
        finally:
            os.close(fd)

    read = (1 << 0) | (1 << 2) | (1 << 3)
    for p in ('/usr', '/lib', '/lib64', '/bin', '/etc'):
        allow(p, read)
    for p in ('method', 'baseline', 'checkpoints', 'redteam', 'scripts', '.pylib',
              'data/face_embeddings_dev.npz'):
        allow(workspace / p, read)
    for p in ('/dev/null', '/dev/urandom', '/dev/random'):
        allow(p, read | (1 << 1))
    allow(call, handled)
    if libc.prctl(38, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'PR_SET_NO_NEW_PRIVS')
    if libc.syscall(446, ruleset, 0) < 0:
        raise OSError(ctypes.get_errno(), 'landlock_restrict_self')
    os.close(ruleset)
    os.execvpe(command[0], command, os.environ)


if __name__ == '__main__':
    main()

"""Delegate the typed real kernel table; fail only one requested OS operation."""
import ctypes

from do_math import windows_job


class KernelFailure:
    def __init__(self, *, information_class=None, resume=False):
        self.real = windows_job._kernel32
        self.information_class = information_class
        self.resume_failure = resume
        self.calls = []

    def __getattr__(self, name):
        original = getattr(self.real, name)

        def call(*args):
            self.calls.append((name, args))
            if name == 'SetInformationJobObject' and args[1] == self.information_class:
                ctypes.set_last_error(8)
                return 0
            if name == 'ResumeThread' and self.resume_failure:
                ctypes.set_last_error(8)
                return windows_job._WAIT_FAILED
            return original(*args)
        return call

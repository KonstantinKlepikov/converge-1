# Copyright (c) 2011 King's College London, created by Laurence Tratt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


import inspect, sys
import Builtins





################################################################################
# Configuration
#

if sys.platform.startswith("win"):
    CASE_SENSITIVE_FILENAMES = 0
else:
    CASE_SENSITIVE_FILENAMES = 1

if sys.byteorder == "big":
    ENDIANNESS = "BIG_ENDIAN"
else:
    ENDIANNESS = "LITTLE_ENDIAN"




################################################################################
# The root object
#

class Con_Thingy(object):
    __slots__ = ()



################################################################################
# PC objects
#

class PC(object):
    __slots__ = ("mod")
    _immutable_fields_ = ("mod",)


class BC_PC(PC):
    __slots__ = ("off")
    _immutable_fields_ = ("mod", "off")
    
    def __init__(self, mod, off):
        assert isinstance(mod, Builtins.Con_Module)
        self.mod = mod
        self.off = off


class Py_PC(PC):
    __slots__ = ("f")
    _immutable_fields_ = ("mod", "f")

    def __init__(self, mod, f):
        assert isinstance(mod, Builtins.Con_Module)
        self.mod = mod
        self.f = f



################################################################################
# Generator support
#

class Con_Gen_Proc:
    _immutable_ = True
    def __init__(self):
        pass
    def next(self):
        raise NotImplementedError


class Class_Con_Gen(Con_Gen_Proc):
    _immutable_ = True


class Class_Con_Proc(Con_Gen_Proc):
    _immutable_ = True


def con_object_gen(pyfunc):
    assert inspect.isgeneratorfunction(pyfunc)
    class _Tmp_Gen(Class_Con_Gen):
        _immutable_ = True
        def __init__(self, *args):
            self._gen = pyfunc(*args)
        def next(self):
            return self._gen.next()
    _Tmp_Gen.__name__ = "gen__%s__%s" % (pyfunc.__module__.replace(".", "_"), pyfunc.__name__)
    return _Tmp_Gen


def con_object_proc(pyfunc):
    assert inspect.isfunction(pyfunc) and not inspect.isgeneratorfunction(pyfunc)
    class _Tmp_Proc(Class_Con_Proc):
        _immutable_ = True
        def __init__(self, *args):
            self._args = args
        def next(self):
            return pyfunc(*self._args)
    _Tmp_Proc.__name__ = "proc__%s__%s" % (pyfunc.__module__.replace(".", "_"), pyfunc.__name__)
    return _Tmp_Proc



################################################################################
# Index translation
#

def translate_idx(vm, i, upper):
    if i < 0:
        i = upper + i
    
    if i < 0 or i >= upper:
        vm.raise_helper("Bounds_Exception", \
          [Builtins.Con_Int(vm, i), Builtins.Con_Int(vm, upper)])

    return i


def translate_idx_obj(vm, i_o, upper):
    if i_o is None:
        i = 0
    else:
        assert isinstance(i_o, Builtins.Con_Int)
        i = i_o.v
    return translate_idx(vm, i, upper)


def translate_slice_idx(vm, i, upper):
    if i < 0:
        i = upper + i
    
    if i < 0 or i > upper:
        vm.raise_helper("Bounds_Exception", \
          [Builtins.Con_Int(vm, i), Builtins.Con_Int(vm, upper)])

    return i


def translate_slice_idx_obj(vm, i_o, upper):
    if i_o is None:
        i = 0
    else:
        assert isinstance(i_o, Builtins.Con_Int)
        i = i_o.v
    return translate_slice_idx(vm, i, upper)


def translate_slice_idxs(vm, i, j, upper):
    i = translate_slice_idx(vm, i, upper)
    j = translate_slice_idx(vm, j, upper)
    if j < i:
        vm.raise_helper("Indices_Exception", \
          [Builtins.Con_Int(vm, i), Builtins.Con_Int(vm, j)])

    return i, j


def translate_slice_idx_objs(vm, i_o, j_o, upper):
    if i_o is None:
        i = 0
    else:
        assert isinstance(i_o, Builtins.Con_Int)
        i = i_o.v
    if j_o is None: 
        j = upper
    else:
        assert isinstance(j_o, Builtins.Con_Int)
        j = j_o.v

    return translate_slice_idxs(vm, i, j, upper)

==========
WarnSquash
==========

WarnSquash (WS) is a tool that helps squash compiler warnings.

WarnSquash is built on top of Clang. Therefore, any actionable warning
(known as a diagnostic in Clang speak) can theoretically be addressed by
WS. However, this does mean that WS is limited to fixing the C family of
languages (C, C++, Objective C).

WarnSquash was originally authored by Gregory Szorc.

Installing
==========

WarnSquash utilizes the Python binding to libclang, the C interface for
the Clang compiler (which is written in C++). So, you will need Clang to
run WarnSquash. We recommend the latest released version. When this
documentation was written, WarnSquash was only tested against a trunk
build of LLVM/Clang (pulled on 2012-01-02). However, it should work on
3.0.

WarnSquash ships with a Python package definition. So, to install it:

    $ python setup.py install

The Clang Python binding officially ships as part of Clang. However,
it doesn't appear that many package maintainers have bothered to include
it. So, you may have to install it yourself.

The good news is the Python binding doesn't need to be compiled, so you
can just drop it in your PYTHONPATH. You can obtain the binding files
from http://llvm.org/viewvc/llvm-project/cfe/trunk/bindings/python/

Running
=======

Once you've installed the package, you should be able to see the help by
running:

    $ warnsquash --help

If that doesn't provide enough help to be useful, we are doing it wrong.

If the Clang Python bindings are installed somewhere weird, you can run
with a modified PYTHONPATH e.g.

    $ PYTHONPATH=~/src/clang/bindings/python:$PYTHONPATH warnsquash --help

Supported Operations
====================

WarnSquash can automatically fix the following warnings:

* Unused function parameter names

In some cases, the fix technique can be controlled by command line
arguments. See the help text for more.

Future Ideas
============

* MOAR fixable warnings
* Interactive prompting for fixing
* Tests

Known Issues
============

Segfaults
---------

A segfault is occurring during reparse if multiple warnings are being fixed
in a single file. Cause is unknown. Possibly a libclang bug.

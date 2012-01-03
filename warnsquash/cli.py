# Copyright 2012 Gregory Szorc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from . import analyzer

import argparse
import difflib

USAGE = """%(prog)s [options] file0 [file1] -- [clang arguments]

WarnSquash helps you remove compiler warnings. To use, pass options to control
WarnSquash followed by the source filename. Then, specifiy two dashes (--)
followed by all the arguments you would issue to `clang` or `clang++` to
perform an action.

For example:

  warnsquash --removed-unused-parameter-names hello.c -- -c -Wall \\
          -Wextra -I ./include -DFOO=BAR

It is not necessary to specify the input file as part of Clang's arguments.

WarnSquash operates against the Clang library, not the executable itself. So,
your library search path (LD_LIBRARY_PATH) and not PATH will have an impact.

By default, warnsquash writes the new (possibly modified) file content to
stdout. Other output methods can be controlled by arguments. It is safe to
redirect stdout to the input file.
"""

def parse_args(args):
    our_args = None
    clang_args = []
    try:
        index = args.index('--')
        clang_args = args[index + 1:]
        our_args = args[0:index]

        if index == 0:
            our_args = []
    except ValueError:
        our_args = args

    parser = argparse.ArgumentParser(usage=USAGE)
    parser.add_argument('file',
            nargs='+',
            help='Filename to parse and fix.')
    parser.add_argument('--print-diff', action='store_true',
            help='Print a diff of the changes.')
    parser.add_argument('--save-changes', action='store_true',
            help='Save changes back to original file.')
    #parser.add_argument('--remove-unused-variables', action='store_true',
    #        help='Remove unused variable declarations.')
    parser.add_argument('--remove-unused-parameter-names', action='store_true',
            help='Remove the names of unused function parameters.')
    parser.add_argument('--comment-unused-parameter-names',
            action='store_true',
            help='Replace unused parameter names with an in-line comment.')

    return (parser.parse_args(our_args), clang_args)

def main(args, fh):
    args, clang_args = parse_args(args)

    for path in args.file:
        u = analyzer.CodeUnit(path, clang_args)

        u.fix_warnings(
            #remove_unused_variables=args.remove_unused_variables,
            remove_unused_parameter_names=args.remove_unused_parameter_names,
            comment_unused_parameter_names=args.comment_unused_parameter_names
        )

        output_performed = False

        if args.save_changes:
            with open(path, 'w') as of:
                for line in u.new_lines:
                    of.write(line)
            print >>fh, 'Wrote changes to source file'
            output_performed = True

        if args.print_diff:
            for line in difflib.unified_diff(u.original_lines, u.new_lines,
                    fromfile=args.file, tofile=args.file):
                fh.write(line)
            output_performed = True

        if not output_performed:
            for line in u.new_lines:
                fh.write(line)


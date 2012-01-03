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

import clang.cindex
import collections
import os.path

class CodeUnit(object):
    """Represents a unit of code which will be operated on."""

    __slots__ = (
        'path', # Loaded path containing parsed source
        'original_lines', # Original lines of input file/source
        'new_lines', # New lines with modified source
        'index', # clang.cindex.Index instance
        'tu', # parsed translation unit
    )

    def __init__(self, path, args):
        """Construct a code unit from source code.

        path -- Filename to load
        args -- Arguments that would be passed to compiler.
        """
        with open(path, 'r') as fh:
            self.original_lines = [l for l in fh]
        self.new_lines = list(self.original_lines)

        self.path = path
        self.index = clang.cindex.Index.create()
        self.tu = self.index.parse(path, args=args, unsaved_files=[(path,
            ''.join(self.original_lines))])
        if not self.tu:
            raise Exception('Compiler error when creating translation unit')

        # Ensure there are no severe warnings
        errors = [d for d in self.tu.diagnostics if d.severity in (
            clang.cindex.Diagnostic.Error, clang.cindex.Diagnostic.Fatal)]

        if len(errors):
            raise Exception('Errors when loading source:\n%s' %
                    '\n'.join([str(s) for s in errors]))

    def fix_warnings(self, callback=None,
            remove_unused_variables=False,
            remove_unused_parameter_names=False,
            comment_unused_parameter_names=False):
        """Fixes warnings in the source code.

        After this is called, you can get the mutated source via .lines

        callback -- If defined, this method will be called before a change is
        made. The callback should return a tuple of (bool, string). The first
        element says whether to apply the fix. If True, the second can control
        the replacement content. If None, default behavior is performed.

        remove_unused_parameter_names -- If True, remove unused parameter names
        from function definitions.

        comment_unused_parameter_names -- If True, replace unused parameter
        names with an in-line comment.
        """

        diagnostics = collections.deque(self.tu.diagnostics)

        # Whenever we modify the source, we call this to reparse. This
        # accomplishes a few things:
        #  1) It ensures that our changes don't break previously-working source
        #  2) It ensures that locations references in diagnostics are updated
        #     with possibly new location.
        #
        # After this is called, existing diagnostics point to an invalid handle
        # and can't be accessed.
        def reparse():
            self.tu.reparse(unsaved_files=[(self.path,
                ''.join(self.new_lines))])
            diagnostics = collections.deque(self.tu.diagnostics)

        while len(diagnostics) > 0:
            diagnostic = diagnostics.popleft()

            # Currently, libclang doesn't expose a strong enumeration for a
            # diagnostic, so we have to infer it from other data.

            # [gps] I have e-mailed the Clang dev list regarding adding this
            # functionality. I also have the beginning of a patch implementing
            # it. We'll see if they are willing to accept it.

            if ((remove_unused_parameter_names or
                    comment_unused_parameter_names) and
                    diagnostic.spelling.startswith('unused parameter')):
                cursor = clang.cindex.Cursor.from_location(self.tu,
                        diagnostic.location)
                assert(cursor.kind == clang.cindex.CursorKind.PARM_DECL)

                variable_name = cursor.displayname

                # Children constitute the type along with qualifiers. We assume
                # that the final child is the last token before the parameter
                # name.
                start_column = \
                    list(cursor.get_children())[0].extent.end.column - 1

                end_column = cursor.extent.end.column - 1

                line = self.new_lines[diagnostic.location.line - 1]

                # TODO remove token in a more clang API proper way.
                # [gps] I can't figure out how to get at things like '*' for
                # pointers. The above calculation leaves these out. The current
                # method is probably safe, but it doesn't feel right.
                relevant = line[start_column:end_column]

                if remove_unused_parameter_names:
                    relevant = relevant.replace(variable_name, '').strip()
                elif comment_unused_parameter_names:
                    relevant = relevant.replace(variable_name, '/* %s */' %
                            variable_name)
                else:
                    raise Exception('Logic error: unhandled option')

                # Oh, Python, why are strings a collection but not really?
                chars = list(line)
                chars[start_column:end_column] = list(relevant)
                line = ''.join(chars)

                self.new_lines[diagnostic.location.line - 1] = line
                reparse()


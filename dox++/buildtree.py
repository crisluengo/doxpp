# -*- coding: utf-8 -*-

# Copyright 2013-2018, Jesse van den Kieboom
# Copyright 2020, Cris Luengo
#
# This file is part of dox++.  dox++ is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

#from . import comment
#from . import nodes
from . import libclang
from . import members
from . import unique_id
from . import log

import os, sys, re, glob, shlex

cindex = libclang.load_libclang()

def expand_sources(sources):
    ret = []
    for source in sources:
        if ('*' in source) or ('?' in source):
            ret.extend(glob.glob(source))
        else:
            ret.append(source)
    return ret

def split_string(string, separator=None):
    # Separate the first part from string, the second part could be empty. Returns a tuple.
    list = string.split(separator, maxsplit=1)
    part1 = list[0]
    if len(list)>1:  # never more than 2 elements
        part2 = list[1]
    else:
        part2 = ''
    return part1, part2

def separate_brief(comment):
    if comment.startswith('\\brief') or comment.startswith('@brief'):
        # The full first paragraph is the brief string
        brief, comment = split_string(comment, '\n\n')
        brief = brief[len('@brief'):].strip()
    else:
        # Only the first line is the brief string
        brief, comment = split_string(comment, '\n')
    return brief, comment

def add_doc(member, brief, doc):
    if not member['brief']:
        member['brief'] = brief
    if member['doc']:
        member['doc'] += '\n\n' + doc
    else:
        member['doc'] = doc


#--- Parsing header files ---

def process_command(comment, status):
    # This function processes commands not associated to a declaration in the header file
    cmd, comment = split_string(comment)
    if len(cmd) > 1 and (cmd[0] == '\\' or cmd[0] == '@'):
        cmd = cmd[1:]
        # Grouping commands: this works differently than in Doxygen.
        # \defgroup defines a group, subsequent definitions fall within the group
        # \addtogroup makes subsequent definitions fall within the group, but doesn't provide
        # documentation for the group itself
        # \endgroup stops the current group
        # Starting a group within a group causes nested groups. Also adding \ingroup to the group's
        # documentation causes it to be nested.
        if cmd == 'defgroup':
            name, comment = split_string(comment, '\n')
            id, name = split_string(name)
            brief, doc = separate_brief(comment)
            current_group = status['current_group']
            if not id in status['groups']:
                status['groups'][id] = members.new_group(id, name, brief, doc, current_group)
            else:
                group = status['groups'][id]
                if not group['name']:
                    group['name'] = name
                add_doc(group, brief, doc)
            if current_group:
                status['groups'][current_group]['subgroups'].add(id)
            status['current_group'] = id

        elif cmd == 'addtogroup':
            id, comment = split_string(comment)
            # We ignore comment here... only the very first token is the id
            if status['current_group']:
                log.error("\\addtogroup %s cannot occur while in a group\n   in file %s", id, status['current_file'])
                return
            if not id in status['groups']:
                status['groups'][id] = members.new_group(id)
            status['current_group'] = id

        elif cmd == 'endgroup':
            if status['current_group']:
                # Find parent group, make it the current group
                status['current_group'] = status['groups'][status['current_group']]['parent']
            else:
                log.warning("\\endgroup cannot occur while not in a group\n   in file %s", status['current_file'])

        # Documenting the current file
        elif cmd == 'file':
            brief, doc = separate_brief(comment)
            add_doc(status['data']['headers'][-1], brief, doc)

        # Documenting things we don't declare right here
        # \class name
        # \struct name
        # \var name
        # etc.
        else:
            type = cmd
            name, comment = split_string(comment, '\n')
            # TODO: do we search for





def extract_comment(token):
    prelen = token.extent.start.column - 1
    comment = token.spelling.strip()

    # Single-line comments must start with /// or //!
    if comment.startswith('//'):
        if len(comment) > 2 and (comment[2] == '/' or comment[2] == '!'):
            line = comment[3:].rstrip()
            if len(line) > 0 and line[0] == ' ':
                line = line[1:]
            return line + '\n'

    # Multi-line comments must start with /** or /*!
    elif comment.startswith('/*') and comment.endswith('*/'):
        if comment[2] == '*' or comment[2] == '!':
            lines = []
            for line in comment[3:-2].splitlines():
                if prelen == 0 or line[0:prelen].isspace():
                    line = line[prelen:].rstrip()
                    if line.startswith(' *') or line.startswith('  '):
                        line = line[2:]
                        if len(line) > 0 and line[0] == ' ':
                            line = line[1:]
                lines.append(line)
            return "\n".join(lines) + '\n\n'

    return None

def process_token(token, comments, status):
    member = members.basic('')
    # TODO: Process data in token into a member structure
    return member

def extract_loop(iter, status):
    # Find the next comment
    token = next(iter)
    while token.kind != cindex.TokenKind.COMMENT:
        token = next(iter)

    # Concatenate individual comments together, but only if they are strictly
    # adjacent, and only the documentation comments
    comments = ''
    prev = None
    while token.kind == cindex.TokenKind.COMMENT:
        comment = extract_comment(token)
        # Check adjacency
        if not prev is None and prev.extent.end.line + 1 < token.extent.start.line:
            # Previous comment not associated with a declaration. Let's parse it
            # and take an action on it.
            comments = comments.strip('\n')
            process_command(comments, status)
            # Reset
            comments = []
        if not comment is None:
            comments += comment
        prev = token
        token = next(iter)
    comments = comments.strip('\n')

    # Get token that comes after, and prepare member data
    if len(comments) > 0:
        member = process_token(token, comments, status)
        # TODO: insert member into status['data']

def extract_documentation(filename, tu, status):
    # Gets the comments out of the file, figures out what entity they belong to,
    # and builds an appropriate data structure in status['data']
    it = tu.get_tokens(extent=tu.get_extent(filename, (0, int(os.stat(filename).st_size))))
    while True:
        try:
            extract_loop(it, status)
        except StopIteration:
            break

#--- Parsing Markdown files ---

def extract_markdown(f, status):
    # Gets the Markdown blocks out of the file, and adds them in the appropriate
    # locations in status['data']
    pass

#--- Main function for this file ---

def buildtree(root_dir, input_files, additional_files, compiler_flags, include_dirs):
    """
    :param root_dir: The root directory for the header files, that you would pass to the compiler with `-I` when using the library
    :param input_files: header files (with wildcards and path relative to working directory), space separated
    :param additional_files: Markdown files (with wildcards and path relative to working directory), space separated
    :param compiler_flags: flags to pass to the compiler
    :param include_dirs: include directories to pass to the compiler
    """
    input_files = expand_sources(input_files)
    additional_files = expand_sources(additional_files)
    compiler_flags = libclang.flags(compiler_flags)
    compiler_flags += ['-I{0}'.format(x) for x in shlex.split(include_dirs, posix=False)]

    # Create a map from CursorKind to classes representing those cursor kinds.
    #kindmap = {}
    #for cls in nodes.Node.subclasses():
    #    if hasattr(cls, 'kind'):
    #        kindmap[cls.kind] = cls

    # Build the output file data representation
    data = {
        'index': '',
        'members': [],
        'headers': [],
        'groups': [],
        'pages': []
    }

    # Our status
    status = {
        'data': data,
        'current_group': '',
        'current_file': '',
        'groups': {},           # these dictionaries contain the same dictionaries as in 'data',
        'files': {},            #    but indexed by their id so they're easy to find. It is the
        'members': {}           #    *same* dictionaries, modifying these will modify 'data'.
    }

    root_dir = os.path.realpath(root_dir)

    # Process all header files
    index = cindex.Index.create()
    processed = {}
    for f in input_files:
        # Skip file if already processed
        f = os.path.realpath(f)  # realpath makes for better comparisons
        if f in processed:
            continue

        # Get the name we'd use in an #include statement
        canonical_name = os.path.relpath(f, start=root_dir)
        print('Processing {0}'.format(canonical_name))
        status['current_file'] = canonical_name
        status['current_group'] = ''

        # Add info for current file
        file_id = unique_id.header(canonical_name)
        status['data']['headers'].append(members.new_header(file_id, canonical_name))
        status['files'][file_id] = status['data']['headers'][-1]

        # Parse the file
        tu = index.parse(f, compiler_flags)
        if len(tu.diagnostics) != 0:
            fatal = False
            for d in tu.diagnostics:
                sys.stderr.write(d.format())
                sys.stderr.write("\n")
                if d.severity == cindex.Diagnostic.Fatal or d.severity == cindex.Diagnostic.Error:
                    fatal = True
                    log.error(d.format())
                else:
                    log.warning(d.format())
            if fatal:
                log.error("Could not generate documentation due to parser errors")
                sys.exit(1)
        if not tu:
            log.error("Could not parse file %s", f)
            sys.exit(1)

        # Extract comments from file
        extract_documentation(f, tu, status)

        # Mark file as complete
        processed[f] = True

    # Process all additional files
    status['current_file'] = ''
    status['current_group'] = ''
    processed = {}
    for f in additional_files:
        # Skip file if already processed
        f = os.path.realpath(f)  # realpath makes for better comparisons
        if f in processed:
            continue
        print('Processing {0}'.format(f))

        # Extract markdown block from file
        extract_markdown(f, status)

        # Mark file as complete
        processed[f] = True

    return status['data']

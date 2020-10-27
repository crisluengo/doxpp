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

from . import libclang
from . import members
from . import unique_id
from . import log

import os, sys, glob, shlex, re


cindex = libclang.load_libclang()

kind_to_type_map = {
    cindex.CursorKind.CLASS_DECL: 'cclass',
    cindex.CursorKind.CLASS_TEMPLATE: 'classtemplate',
    cindex.CursorKind.CONSTRUCTOR: 'constructor',
    cindex.CursorKind.CONVERSION_FUNCTION: 'conversionfunction',
    cindex.CursorKind.CXX_METHOD: 'method',
    cindex.CursorKind.DESTRUCTOR: 'destructor',
    cindex.CursorKind.ENUM_CONSTANT_DECL: 'enumvalue',
    cindex.CursorKind.ENUM_DECL: 'enum',
    cindex.CursorKind.FIELD_DECL: 'field',
    cindex.CursorKind.FUNCTION_DECL: 'function',
    cindex.CursorKind.FUNCTION_TEMPLATE: 'functiontemplate',
    cindex.CursorKind.NAMESPACE: 'namespace',
    cindex.CursorKind.STRUCT_DECL: 'cstruct',
    cindex.CursorKind.TEMPLATE_NON_TYPE_PARAMETER: 'templatenontypeparameter',
    cindex.CursorKind.TEMPLATE_TYPE_PARAMETER: 'templatetypeparameter',
    #cindex.CursorKind.TEMPLATE_TEMPLATE_PARAMETER: 'templatetemplateparameter', # TODO: do we need to add this?
    cindex.CursorKind.TYPEDEF_DECL: 'typedef',
    cindex.CursorKind.TYPE_ALIAS_DECL: 'using',
    cindex.CursorKind.UNION_DECL: 'union',
    cindex.CursorKind.VAR_DECL: 'variable'
}


# These are the commands that can start a documentation block
documentation_commands = {
    'addtogroup',
    'class',
    'def',
    'defgroup',
    'dir',
    'endgroup',
    'enum',
    'example',
    'file',
    'fn',
    'mainpage',
    'name',
    'namespace',
    'overload',
    'page',
    'struct',
    'typedef',
    'union',
    'var'
}


class Status:
    # This defines the status of our parser
    # (it's a way to collect global information without making a global parameter...)
    def __init__(self, data):
        self.data = data
        self.current_group = ['']    # Here we keep a stack of current group IDs. `current_group[-1]` is the current group.
        self.group_locations = []    # Here we keep a list of (line, group_id), for the current file only. line is the line that the group starts. If group_id is '', then no group is active after that line
        self.current_file = {}       # `files[i]` dict for  the current file.
        self.current_file_name = ''  # Full file name (with absolute path).
        self.groups = {}             # These dictionaries contain the same dictionaries as in 'data',
        self.files = {}              #    but indexed by their id so they're easy to find. It is the
        self.members = {}            #    *same* dictionaries, modifying these will modify 'data'.
        self.member_ids = {}         # A dictionary to translate USR to our ID for a member.

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
        brief = brief.strip()
    comment = comment.strip()
    return brief, comment

def add_doc(member, brief, doc):
    if not member['brief']:
        member['brief'] = brief
    if member['doc']:
        member['doc'] += '\n\n' + doc
    else:
        member['doc'] = doc

def clean_comment(comment):
    # Removes first few characters from single-line documentation comment
    line = comment[3:].rstrip()  # removes '///' or '//!'
    if len(line) > 0 and line[0] == '<':
        # This is if the comment is in the style "///< ..."
        line = line[1:]
    if len(line) > 0 and line[0] == ' ':
        line = line[1:]
    return line

def clean_multiline_comment(comment, prelen = 0):
    lines = []
    start = 3
    if len(comment) > 4 and comment[3] == '<':
        # This is if the comment is in the style "/**< ... */"
        start = 4
    for line in comment[start:-2].splitlines():
        if prelen == 0 or line[0:prelen].isspace():
            line = line[prelen:].rstrip()
            if line.startswith(' *') or line.startswith('  '):
                line = line[2:]
                if len(line) > 0 and line[0] == ' ':
                    line = line[1:]
        lines.append(line)
    return lines

def clean_single_line_comment_block(comment):
    lines = []
    for line in comment.splitlines():
        line = clean_comment(line.lstrip())
        lines.append(line)
    return lines

def is_single_line_comment(comment):
    return comment.startswith('//')

def is_documentation_comment(comment, style):  # style should be '/' or '*' for // or /**/
    if style == '/':
        return len(comment) > 2 and (comment[2] == '/' or comment[2] == '!')
    return comment[2] == '*' or comment[2] == '!'  # no need to test length, this syle comment must have at least 4 characters

def get_group_at_line(group_locations, line):
    current_group = ''
    for item in group_locations:
        if line < item[0]:
            return current_group
        current_group = item[1]
    return current_group

ingroup_cmd_match = re.compile(r"^\s*\\ingroup\s+(\S+)\s*$", re.MULTILINE)

def find_ingroup_cmd(member):
    doc = member['doc']
    m = ingroup_cmd_match.search(doc)
    if m:
        group = m.group(1)
        member['doc'] = doc[:m.span(0)[0]]+doc[m.span(0)[1]:]
        return group
    return ''

#--- Parsing header files --- extracting and processing comments ---

def process_command(lines, loc, status: Status):
    # This function processes a specific set of commands that should not be associated
    # to a declaration in the header file

    # Skip empty lines
    while lines and not lines[0]:
        lines = lines[1:]
    if not lines:
        return

    # The comment should start with a valid command
    cmd, args = split_string(lines[0])
    if cmd[0] != '\\' and cmd[0] != '@':
        return
    cmd = cmd[1:]
    if not cmd in documentation_commands:
        return

    # Grouping commands: this works differently than in Doxygen.
    # \defgroup defines a group, subsequent definitions fall within the group
    # \addtogroup makes subsequent definitions fall within the group, but doesn't provide
    # documentation for the group itself
    # \endgroup stops the current group
    # Starting a group within a group causes nested groups. Also adding \ingroup to the group's
    # documentation causes it to be nested.
    if cmd == 'defgroup':
        id, name = split_string(args)
        if not id or not name:
            log.error("\\defgroup needs an ID and a name\n   in file %s", status.current_file_name)
            return
        brief, doc = separate_brief('\n'.join(lines[1:]))
        current_group = status.current_group[-1]
        if not id in status.groups:
            status.groups[id] = members.new_group(id, name, brief, doc, current_group)
            status.data['groups'].append(status.groups[id])
        else:
            group = status.groups[id]
            if not group['name']:
                group['name'] = name
            add_doc(group, brief, doc)
        if current_group:
            group = status.groups[current_group]
            if group['subgroups'].count(id) == 0:  # add group only once
                group['subgroups'].append(id)
        status.current_group.append(id)
        status.group_locations.append((loc, id))

    elif cmd == 'addtogroup':
        id, name = split_string(args)
        # We ignore name here
        if not id:
            log.error("\\addtogroup needs an ID\n   in file %s", status.current_file_name)
            return
        current_group = status.current_group[-1]
        if not id in status.groups:
            status.groups[id] = members.new_group(id, '', '', '', current_group)
            status.data['groups'].append(status.groups[id])
        if current_group:
            group = status.groups[current_group]
            if group['subgroups'].count(id) == 0:  # add group only once
                group['subgroups'].append(id)
        # We also ignore the rest of the comment block
        status.current_group.append(id)
        status.group_locations.append((loc, id))

    elif cmd == 'endgroup':
        current_group = status.current_group[-1]
        if current_group:
            status.current_group.pop()
            status.group_locations.append((loc, status.current_group[-1]))
        else:
            log.warning("\\endgroup cannot occur while not in a group\n   in file %s", status.current_file_name)

    # Documenting the current file
    elif cmd == 'file':
        if args:
            canonical_name = args  # TODO: This is a mess... we need to get the canonical name here.
            file_id = unique_id.header(canonical_name)
            if file_id in status.files:
                file = status.files[file_id]
            else:
                file = members.new_header(file_id, canonical_name)  # TODO: we need to test in the main loop over the files if this has happened
                status.data['headers'].append(file)
                status.files[file_id] = file
        else:
            file = status.current_file
        brief, doc = separate_brief('\n'.join(lines[1:]))
        add_doc(file, brief, doc)

    # Documenting things we don't declare right here
    # \class name
    # \struct name
    # \var name
    # etc.
    else:
        if not args:
            log.error("%s without a name\n   in file %s", status.current_file_name)
            return
        brief, doc = separate_brief('\n'.join(lines[1:]))
        # TODO: implement


def process_comments(tu, status: Status):
    # Gets the comments out of the file, figures out what entity they belong to,
    # and builds an appropriate data structure in status.data
    filename = status.current_file_name
    it = tu.get_tokens(extent=tu.get_extent(filename, (0, int(os.stat(filename).st_size))))
    #for token in it:
    #    print(token.kind, token.spelling)
    token = next(it, None)
    while token:
        # Find the next comment
        while token.kind != cindex.TokenKind.COMMENT:
            token = next(it, None)
            if not token:
                return

        comment = token.spelling.strip()
        if is_single_line_comment(comment):
            # Concatenate individual single-line comments together, but only if they are strictly
            # adjacent, and all are documentation comments
            if is_documentation_comment(comment, '/'):
                loc = token.extent.start.line
                lines = [clean_comment(comment)]
                pos = token.extent.end.line
                token = next(it, None)
                while token and token.kind == cindex.TokenKind.COMMENT:
                    comment = token.spelling.strip()
                    if not is_single_line_comment(comment) or \
                       not is_documentation_comment(comment, '/') or \
                       pos + 1 < token.extent.start.line:
                        break
                    lines.append(clean_comment(comment))
                    pos = token.extent.end.line
                    token = next(it, None)
                process_command(lines, loc, status)
                continue  # token currently is the next token, it hasn't been processed yet, we don't want to skip it
        else:
            # Multi-line comments are not concatenated with anything
            if is_documentation_comment(comment, '*'):
                prelen = token.extent.start.column - 1
                lines = clean_multiline_comment(comment, prelen)
                process_command(lines, token.extent.start.line, status)

        token = next(it, None)

    while status.current_group[-1]:
        log.warning("Missing \\endgroup for group %s\n   in file %s", status.current_group.pop(), status.current_file_name)

#--- Parsing header files --- extracting declarations ---

def merge_member(member, new_member):
    # Merges the two member structures, filling in empty elements in `memeber` with new data, and appending any documentation.
    add_doc(member, new_member['brief'], new_member['doc'])
    for key in new_member:
        if key == 'doc' or key == 'brief':
            continue
        if key == 'members':
            for m in new_member['members']:
                if not m in member['members']:
                    member['members'].append(m)
            continue
        if key in member and not member[key]:
            member[key] = new_member[key]
    return member

def extract_declarations(citer, parent, status: Status):
    # Recursive AST exploration, adds data to `status`.
    if not citer:
        return
    while True:
        try:
            item = next(citer)
        except StopIteration:
            return

        # Check the source of item
        if not item.location.file:
            extract_declarations(item.get_children(), '', status)
            continue

        # Ignore files other than the ones we are scanning for
        if str(item.location.file) != status.current_file_name:
            continue

        # Ignore unexposed things
        if item.kind == cindex.CursorKind.UNEXPOSED_DECL:
            extract_declarations(item.get_children(), parent, status)
            continue

        if item.kind in kind_to_type_map:
            log.debug("member: kind = %s, spelling = %s, parent = %s", item.kind, item.spelling, parent)
            # Create a member data structure for this one
            type = kind_to_type_map[item.kind]
            member = members.new_member('', item.spelling, type, parent, status.current_file_name)

            # Find the associated documentation comment and parse it
            comment = item.raw_comment
            if comment:
                if is_single_line_comment(comment):
                    comment = '\n'.join(clean_single_line_comment_block(comment))
                else:
                    comment = '\n'.join(clean_multiline_comment(comment, item.extent.start.column - 1))  # TODO: this start column is "iffy". We don't know where the comment actually starts!
                cmd, _ = split_string(comment)
                if not(len(cmd) > 1 and cmd[0] == '\\' and cmd[1:] in documentation_commands):
                    brief, doc = separate_brief(comment)
                    add_doc(member, brief, doc)

            # Find the group this member belongs to
            group = find_ingroup_cmd(member)
            if not group:
                group = get_group_at_line(status.group_locations, item.extent.start.line)
            member['group'] = group

            # Associate any other information with this member
            # TODO: process other cursor data and child cursors, depending on what `type` we're dealing with
            process_children = False
            if type == 'cclass':
                process_children = True
                pass
            elif type == 'classtemplate':
                process_children = True
                pass
            elif type == 'constructor':
                pass
            elif type == 'conversionfunction':
                pass
            elif type == 'method':
                pass
            elif type == 'destructor':
                pass
            elif type == 'enumvalue':
                pass
            elif type == 'enum':
                process_children = True
                pass
            elif type == 'field':
                pass
            elif type == 'function':
                pass
            elif type == 'functiontemplate':
                pass
            elif type == 'namespace':
                process_children = True
                pass
            elif type == 'cstruct':
                process_children = True
                pass
            elif type == 'templatenontypeparameter':
                process_children = True
                pass
            elif type == 'templatetypeparameter':
                process_children = True
                pass
            elif type == 'typedef':
                pass
            elif type == 'using':
                pass
            elif type == 'union':
                process_children = True
                pass
            elif type == 'variable':
                pass
            member['deprecated'] = item.availability == cindex.AvailabilityKind.DEPRECATED
            # member.access_specifier (public, protected, private)

            # Deal with IDs
            usr = item.get_usr()
            if usr in status.member_ids:
                id = status.member_ids[usr]
                member = merge_member(status.members[id], member)
            else:
                id = unique_id.member(member, status)
                member['id'] = id
                status.member_ids[usr] = id
                if id in status.members:
                    log.error("USR was unknown, but ID was already there! This means that there is a name clash, unique_id.member is not good enough")
                    continue  # skip the rest of this function, we're in trouble here...
            status.members[id] = member
            if parent:
                status.members[parent]['members'][id] = member
            else:
                status.data['members'].append(member)

            # Process child members
            if process_children:
                extract_declarations(item.get_children(), id, status)

        else:
            log.debug("ignored: kind = %s, spelling = %s, parent = %s", item.kind, item.spelling, parent)
            extract_declarations(item.get_children(), item.get_usr, status)
            continue

            par = self.cursor_to_node[item.semantic_parent]
            if not par:
                par = parent
            if par:
                ret = par.visit(item, citer) # This runs if par is a class, and this item is a CXX_ACCESS_SPEC_DECL or CXX_BASE_SPECIFIER
                if not ret is None:
                    for node in ret:
                        self.register_node(node, par)
            ignoretop = [cindex.CursorKind.TYPE_REF, cindex.CursorKind.PARM_DECL]
            if (not par or ret is None) and not item.kind in ignoretop:
                log.warning("Unhandled cursor: %s", item.kind)

#--- Parsing header files --- extracting include statements ---

def extract_includes(tu, file_member):
    # Gets the list of files directly included by this one (not the ones included
    # by files included here).
    # TODO: This can be better, we might want to use the cursor to retrieve actual `#include` statements.
    it = tu.get_includes()
    for f in it:
        if f.depth == 1:
            file_member['includes'].append(f.include.name)

#--- Parsing Markdown files ---

def extract_markdown(status: Status):
    # Gets the Markdown blocks out of the file, and adds them in the appropriate
    # locations in status.data
    pass

#--- Main function for this file ---

def buildtree(root_dir, input_files, additional_files, compiler_flags, include_dirs):
    """
    :param root_dir: The root directory for the header files, that you would pass to the compiler with `-I` when using the library (string)
    :param input_files: header files (with wildcards and path relative to working directory), space separated (string)
    :param additional_files: Markdown files (with wildcards and path relative to working directory), space separated (string)
    :param compiler_flags: flags to pass to the compiler (string)
    :param include_dirs: include directories to pass to the compiler (string)
    """
    input_files = expand_sources(shlex.split(input_files))
    additional_files = expand_sources(shlex.split(additional_files))
    compiler_flags = libclang.flags(compiler_flags.split())
    compiler_flags += ['-I{0}'.format(x) for x in shlex.split(include_dirs, posix=False)]
    log.debug("Compiler flags: %s", ' '.join(compiler_flags))

    # Build the output file data representation
    data = {
        'index': '',
        'members': [],
        'headers': [],
        'groups': [],
        'pages': []
    }

    # Our status
    status = Status(data)

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
        log.info('Processing %s', canonical_name)
        status.current_file_name = f

        # Reset the rest of the data
        status.current_group = ['']
        status.group_locations = []

        # Add info for current file
        file_id = unique_id.header(canonical_name)
        status.current_file = members.new_header(file_id, canonical_name)
        status.data['headers'].append(status.current_file)
        status.files[file_id] = status.current_file

        # Parse the file
        tu = None
        try:
            tu = index.parse(f, compiler_flags)
        except cindex.TranslationUnitLoadError as e:
            log.error("Could not parse file %s", f)
            log.error(str(e))
            exit(1)
        if not tu:
            log.error("Could not parse file %s", f)
            exit(1)
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
                exit(1)

        # Extract list of headers included by this file
        extract_includes(tu, status.current_file)

        # Extract and process documentation comments with commands
        process_comments(tu, status)

        # Extract declarations and build member tree
        extract_declarations(tu.cursor.get_children(), '', status)

        # Mark this file as complete
        processed[f] = True

    # Process all additional files
    status.current_file = {}
    status.current_file_name = ''
    status.current_group = ['']
    processed = {}
    for f in additional_files:
        # Skip file if already processed
        f = os.path.realpath(f)  # realpath makes for better comparisons
        if f in processed:
            continue
        log.info('Processing %s', f)

        # Extract markdown block from file
        extract_markdown(status)

        # Mark file as complete
        processed[f] = True

    return status.data

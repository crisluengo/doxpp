# dox++
# Copyright 2020, Cris Luengo
# Based on cldoc: Copyright 2013-2018, Jesse van den Kieboom
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

import glob
import os
import re
import shlex
import sys

from . import libclang
from . import log
from . import members
from . import unique_id
from . import walktree

cindex = libclang.load_libclang()

cursor_kind_to_type_map = {
    cindex.CursorKind.CLASS_DECL: 'class',
    cindex.CursorKind.CLASS_TEMPLATE: 'classtemplate',
    cindex.CursorKind.CONSTRUCTOR: 'constructor',
    cindex.CursorKind.CONVERSION_FUNCTION: 'conversionfunction',
    cindex.CursorKind.CXX_BASE_SPECIFIER: 'basespecifier',
    cindex.CursorKind.CXX_METHOD: 'method',
    cindex.CursorKind.DESTRUCTOR: 'destructor',
    cindex.CursorKind.ENUM_CONSTANT_DECL: 'enumvalue',
    cindex.CursorKind.ENUM_DECL: 'enum',
    cindex.CursorKind.FIELD_DECL: 'field',
    cindex.CursorKind.FUNCTION_DECL: 'function',
    cindex.CursorKind.FUNCTION_TEMPLATE: 'functiontemplate',
    cindex.CursorKind.NAMESPACE: 'namespace',
    cindex.CursorKind.STRUCT_DECL: 'struct',
    cindex.CursorKind.TEMPLATE_NON_TYPE_PARAMETER: 'templatenontypeparameter',
    cindex.CursorKind.TEMPLATE_TYPE_PARAMETER: 'templatetypeparameter',
    #cindex.CursorKind.TEMPLATE_TEMPLATE_PARAMETER: 'templatetemplateparameter',  # TODO: do we need to add this?
    cindex.CursorKind.TYPEDEF_DECL: 'typedef',
    cindex.CursorKind.TYPE_ALIAS_DECL: 'using',
    cindex.CursorKind.TYPE_ALIAS_TEMPLATE_DECL: 'usingtemplate',
    cindex.CursorKind.UNION_DECL: 'union',
    cindex.CursorKind.VAR_DECL: 'variable'
}

type_kind_to_type_map = {
    cindex.TypeKind.POINTER: '*',
    cindex.TypeKind.LVALUEREFERENCE: '&',
    cindex.TypeKind.RVALUEREFERENCE: '&&',
}

type_kind_array_types = {
    cindex.TypeKind.CONSTANTARRAY,
    cindex.TypeKind.INCOMPLETEARRAY,
    cindex.TypeKind.VARIABLEARRAY,
    cindex.TypeKind.DEPENDENTSIZEDARRAY
}

type_kind_to_name_map = {
    cindex.TypeKind.VOID: 'void',
    cindex.TypeKind.BOOL: 'bool',
    cindex.TypeKind.CHAR_U: 'char',
    cindex.TypeKind.UCHAR: 'unsigned char',
    cindex.TypeKind.CHAR16: 'char16_t',
    cindex.TypeKind.CHAR32: 'char32_t',
    cindex.TypeKind.USHORT: 'unsigned short',
    cindex.TypeKind.UINT: 'unsigned int',
    cindex.TypeKind.ULONG: 'unsigned long',
    cindex.TypeKind.ULONGLONG: 'unsigned long long',
    cindex.TypeKind.UINT128: 'uint128_t',
    cindex.TypeKind.CHAR_S: 'char',
    cindex.TypeKind.SCHAR: 'signed char',
    cindex.TypeKind.WCHAR: 'wchar_t',
    cindex.TypeKind.SHORT: 'unsigned short',
    cindex.TypeKind.INT: 'int',
    cindex.TypeKind.LONG: 'long',
    cindex.TypeKind.LONGLONG: 'long long',
    cindex.TypeKind.INT128: 'int128_t',
    cindex.TypeKind.FLOAT: 'float',
    cindex.TypeKind.DOUBLE: 'double',
    cindex.TypeKind.LONGDOUBLE: 'long double',
    cindex.TypeKind.NULLPTR: 'nullptr_t',
}

access_specifier_map = {
    cindex.AccessSpecifier.INVALID: '',
    cindex.AccessSpecifier.PUBLIC: 'public',
    cindex.AccessSpecifier.PROTECTED: 'protected',
    cindex.AccessSpecifier.PRIVATE: 'private',
    cindex.AccessSpecifier.NONE: ''
}

# These are the commands that can start a documentation block
# Aliases are mapped to our preferred version
documentation_commands = {
    'addtogroup': 'addtogroup',
    'alias': 'alias',
    'class': 'class',
    'def': 'macro',
    'defgroup': 'defgroup',
    'dir': 'dir',
    'endgroup': 'endgroup',
    'endname': 'endname',
    'enum': 'enum',
    'file': 'file',
    'fn': 'function',
    'function': 'function',
    'macro': 'macro',
    'mainpage': 'mainpage',
    'name': 'name',
    'namespace': 'namespace',
    'page': 'page',
    'struct': 'struct',
    'typedef': 'alias',
    'union': 'union',
    'var': 'variable',
    'variable': 'variable'
}


class Status:
    # This defines the status of our parser
    # (it's a way to collect global information without making a global parameter...)
    def __init__(self, data):
        self.data = data                # We build the output data in here, it's just dictionaries and lists so
                                        # it's easy to output as JSON.

        self.current_group = ['']       # Here we keep a stack of current group IDs.
                                        # `current_group[-1]` is the current group.
        self.group_locations = []       # Here we keep a list of (line, group_id), for the current file only.
                                        # `line` is the line that the group starts.
                                        # If group_id is '', then no group is active after that line.

        self.current_member_group = ''    # These are the same as above, but for grouping class/struct members.
        self.member_group_locations = []  # These groups do not nest, so there's no need for a stack.

        self.current_file = {}          # `files[i]` dict for  the current file.
        self.current_file_name = ''     # Full file name (with absolute path).
        self.current_include_name = ''  # File name relative to project root.

        self.groups = {}                # These dictionaries contain the same dictionaries as in 'data',
        self.files = {}                 #    but indexed by their id so they're easy to find. It is the
        self.members = {}               #    *same* dictionaries, modifying these will modify 'data'.
        self.pages = {}                 #

        self.member_ids = {}            # A dictionary to translate USR to our ID for a member.

        self.unprocessed_commands = []  # Here we keep command documentation blocks that need to be processed later.


class DocumentationCommand:
    def __init__(self, cmd, args, brief, doc, group, file):
        self.cmd = cmd
        self.args = args
        self.brief = brief
        self.doc = doc
        self.group = group
        self.file = file


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
    parts = string.split(separator, maxsplit=1)
    if parts:
        part1 = parts[0]
    else:
        part1 = ''
    if len(parts) > 1:  # never more than 2 elements
        part2 = parts[1]
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
    line = comment[3:]  # removes '///' or '//!'
    if len(line) > 0 and line[0] == '<':
        # This is if the comment is in the style "///< ..."
        line = line[1:]
    if len(line) > 0 and line[0] == ' ':
        line = line[1:]
    return line

def clean_multiline_comment(comment, prelen=0):
    lines = []
    start = 3
    if len(comment) > 4 and comment[3] == '<':
        # This is if the comment is in the style "/**< ... */"
        start = 4
    for line in comment[start:-2].splitlines():
        if prelen == 0 or line[0:prelen].isspace():
            line = line[prelen:]
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
    # no need to test length, this style comment must have at least 4 characters
    return comment[2] == '*' or comment[2] == '!'

def get_group_at_line(group_locations, line):
    current_group = ''
    for item in group_locations:
        if line < item[0]:
            return current_group
        current_group = item[1]
    return current_group

def remove_match_from_string(string, match):
    return string[:match.span(0)[0]] + string[match.span(0)[1]:]

ingroup_cmd_match = re.compile(r'^\s*[\\@]ingroup\s+(\S+)\s*$', re.MULTILINE)

def find_ingroup_cmd(doc):
    m = ingroup_cmd_match.search(doc)
    if m:
        group = m.group(1)
        while m:
            doc = remove_match_from_string(doc, m)
            # Ignore subsequent `\ingroup` commands
            m = ingroup_cmd_match.search(doc)
        return group, doc
    return '', doc

subpage_cmd_match_1 = re.compile(r'[\\@]subpage\s+(\S+)')
subpage_cmd_match_2 = re.compile(r'[\\@]subpage\s+(\S+)\s+\"[^"]\"')

def find_subpage_cmd(member):
    doc = member['doc']
    # First we look for \subpage <name> "text"
    m = subpage_cmd_match_2.search(doc)
    # If that's not found, we look for \subpage <name>
    m = subpage_cmd_match_1.search(doc)
    # TODO


# --- Processing documentation commands ---

def process_generic_command(cmd: DocumentationCommand, status: Status):
    # \cmd <name>
    if not cmd.args:
        log.error("\\%s needs a name argument\n   in file %s", cmd.cmd, cmd.file)
        return
    name, args = split_string(cmd.args)
    if args:
        log.warning("Ignoring additional arguments to \\%s command\n   in file %s", cmd.cmd, cmd.file)
    # Find which member we're talking about
    id = walktree.find_member(name, '', status.members)
    if not id:
        log.error("The member '%s' has not been declared, documentation ignored.\n   in file %s", cmd.args, cmd.file)
        return
    member = status.members[id]
    group, doc = find_ingroup_cmd(cmd.doc)
    if not group:
        group = cmd.group
    if member['group']:
        if group and member['group'] != group:
            log.warning("Member '%s' already is in group %s, cannot assign to group %s", id, member['group'], group)
    else:
        member['group'] = group
    add_doc(member, cmd.brief, doc)

def process_macro_command(cmd: DocumentationCommand, status: Status):
    # \macro <name>
    if not cmd.args:
        log.error("\\macro needs a name argument\n   in file %s", cmd.file)
        return
    name, args = split_string(cmd.args)
    if args:
        log.warning("Ignoring additional arguments to \\macro command\n   in file %s", cmd.file)
    # Do we already have a member for this macro?
    id = unique_id.macro(name)
    group, doc = find_ingroup_cmd(cmd.doc)
    if not group:
        group = cmd.group
    if id in status.members:
        # Add data to existing member
        member = status.members[id]
        if member['member_type'] != 'macro':
            log.error("Documenting a macro with ID %s that is identical to an existing non-macro\n   in file %s",
                      id, cmd.file)
            return
        add_doc(member, cmd.brief, doc)
        if not member['group']:
            member['group'] = group
    else:
        # Create a new member
        member = members.new_member(id, name, 'macro', '', cmd.file)
        member['brief'] = cmd.brief
        member['doc'] = doc
        member['group'] = group
        status.members[id] = member
        status.data['members'].append(member)

def process_file_command(cmd: DocumentationCommand, status: Status):
    # \file <name>
    # Note that the no-name version has already been processed
    if not cmd.args:
        log.error("\\file needs a file name when not in a header file\n   in file %s", cmd.file)
        return
    # Find header file we're referring to. We look for all matches with an arbitrary set of path elements
    # prepended. The shortest such name is the one we pick.
    best_match = ''
    match_length = 1e9
    for header in status.data['headers']:
        name = header['name']
        if name == cmd.args:
            best_match = header['id']
            break
        if len(name) < match_length and name.endswith(os.sep + cmd.args):
            match_length = len(name)
            best_match = header['id']
    if not best_match:
        log.error("The file '%s' has not been parsed, documentation ignored.\n   in file %s", cmd.args, cmd.file)
        return
    header = status.files[best_match]
    add_doc(header, cmd.brief, cmd.doc)

def create_page(name, title, doc, status: Status):
    if name in status.pages:
        cur_doc = status.pages[name]['doc']
        if cur_doc:
            doc = cur_doc + '\n\n' + doc
        status.pages[name]['doc'] = doc
    else:
        page = members.new_page(name, title, doc)
        status.data['pages'].append(page)
        status.pages[name] = page

def process_mainpage_command(cmd: DocumentationCommand, status: Status):
    title = cmd.args
    if not title:
        title = "Main"
    create_page('index', title, cmd.doc, status)

def process_page_command(cmd: DocumentationCommand, status: Status):
    name, title = split_string(cmd.args)
    if not name or not title:
        log.error("\\page requires a name and title, documentation ignored.\n   in file %s", cmd.file)
        return
    create_page(name, title, cmd.doc, status)

def process_documentation_command(cmd: DocumentationCommand, status: Status):
    # This function processes commands that add documentation to members
    if cmd.cmd == 'dir':
        # TODO: How do we record these? Is this even useful?
        log.error("\\dir currently not implemented, documentation ignored.\n   in file %s", cmd.file)
        return
    if cmd.cmd == 'file':
        process_file_command(cmd, status)
        return
    if cmd.cmd == 'macro':
        process_macro_command(cmd, status)
        return
    if cmd.cmd == 'mainpage':
        process_mainpage_command(cmd, status)
        return
    if cmd.cmd == 'page':
        process_page_command(cmd, status)
        return
    # Handle namespace, class, struct, union, enum, alias, function, variable
    process_generic_command(cmd, status)

def process_grouping_command(cmd, args, brief, doc, loc, status: Status):
    # This function processes commands that handle grouping of members.
    # Returns True if the command was processed, false otherwise.
    #
    # Grouping commands work differently than in Doxygen:
    # \defgroup defines a group, subsequent definitions fall within the group.
    # \addtogroup makes subsequent definitions fall within the group, but doesn't provide
    # documentation for the group itself.
    # \endgroup stops the current group.
    # Starting a group within a group causes nested groups. Also adding \ingroup to the group's
    # documentation causes it to be nested.
    # \name and \endname work similarly, but only inside a class or struct definition.
    if cmd == 'defgroup':
        id, name = split_string(args.strip())
        if not id or not name:
            log.error("\\defgroup needs an ID and a name\n   in file %s", status.current_include_name)
            return True
        current_group = status.current_group[-1]
        if id not in status.groups:
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
        return True
    if cmd == 'addtogroup':
        id, name = split_string(args)
        # We ignore name here
        if not id:
            log.error("\\addtogroup needs an ID\n   in file %s", status.current_include_name)
            return True
        current_group = status.current_group[-1]
        if id not in status.groups:
            status.groups[id] = members.new_group(id, '', '', '', current_group)
            status.data['groups'].append(status.groups[id])
        if current_group:
            group = status.groups[current_group]
            if group['subgroups'].count(id) == 0:  # add group only once
                group['subgroups'].append(id)
        # We also ignore the rest of the comment block
        status.current_group.append(id)
        status.group_locations.append((loc, id))
        return True
    if cmd == 'endgroup':
        current_group = status.current_group[-1]
        if current_group:
            status.current_group.pop()
            status.group_locations.append((loc, status.current_group[-1]))
        else:
            log.warning("\\endgroup cannot occur while not in a group\n   in file %s", status.current_include_name)
        return True
    if cmd == 'name':
        status.current_member_group = args
        status.group_locations.append((loc, args))
        return True
    if cmd == 'endname':
        status.current_member_group = ''
        status.group_locations.append((loc, ''))
        return True
    return False


# --- Parsing header files --- extracting and processing comments ---

def process_comment_command(lines, loc, status: Status):
    # This function processes a specific set of commands that should not be associated
    # to a declaration in the header file

    # Skip empty lines
    while lines and not lines[0]:
        lines = lines[1:]
    if not lines:
        return

    # The comment should start with a valid command
    cmd, args = split_string(lines[0].strip())
    if not cmd or cmd[0] not in ['\\', '@']:
        return
    cmd = cmd[1:]
    if cmd not in documentation_commands:
        return
    cmd = documentation_commands[cmd]

    # Everything after the first line is documentation
    doc = '\n'.join(lines[1:])
    brief = ''
    if cmd not in ['page', 'mainpage']:
        brief, doc = separate_brief(doc)

    # Grouping commands
    if process_grouping_command(cmd, args, brief, doc, loc, status):
        return

    # Documenting the current file
    if cmd == 'file' and not args:
        add_doc(status.current_file, brief, doc)
        return

    # Documenting things we don't declare right here, this we'll do after processing all header files
    status.unprocessed_commands.append(DocumentationCommand(cmd, args, brief, doc, status.current_group[-1],
                                                            status.current_include_name))

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

        comment = token.spelling.lstrip()
        if is_single_line_comment(comment):
            # Concatenate individual single-line comments together, but only if they are strictly
            # adjacent, and all are documentation comments
            if is_documentation_comment(comment, '/'):
                loc = token.extent.start.line
                lines = [clean_comment(comment)]
                pos = token.extent.end.line
                token = next(it, None)
                while token and token.kind == cindex.TokenKind.COMMENT:
                    comment = token.spelling.lstrip()
                    if not is_single_line_comment(comment) or \
                       not is_documentation_comment(comment, '/') or \
                       pos + 1 < token.extent.start.line:
                        break
                    lines.append(clean_comment(comment))
                    pos = token.extent.end.line
                    token = next(it, None)
                process_comment_command(lines, loc, status)
                continue  # token currently is the next token, it hasn't been processed yet, we don't want to skip it
        else:
            # Multi-line comments are not concatenated with anything
            if is_documentation_comment(comment, '*'):
                prelen = token.extent.start.column - 1
                lines = clean_multiline_comment(comment, prelen)
                process_comment_command(lines, token.extent.start.line, status)

        token = next(it, None)

    while status.current_group[-1]:
        log.warning("Missing \\endgroup for group %s\n   in file %s",
                    status.current_group.pop(), status.current_include_name)
    if status.current_member_group:
        log.warning("Missing \\endname\n   in file %s", status.current_include_name)

# --- Parsing Markdown files ---

def process_markdown_command(lines, status: Status):
    # This function processes a specific set of commands in Markdown files
    # Similar to process_comment_command()

    # Skip empty lines
    while lines and not lines[0]:
        lines = lines[1:]
    if not lines:
        return

    # The comment should start with a valid command
    cmd, args = split_string(lines[0].strip())
    if not cmd or cmd[0] not in ['\\', '@']:
        return
    cmd = cmd[1:]
    if cmd not in documentation_commands:
        return
    cmd = documentation_commands[cmd]

    # Everything after the first line is documentation
    brief, doc = separate_brief('\n'.join(lines[1:]))

    # Grouping commands
    if process_grouping_command(cmd, args, brief, doc, 0, status):
        return

    # Documentation
    process_documentation_command(DocumentationCommand(cmd, args, brief, doc, status.current_group[-1],
                                                       status.current_include_name), status)

def extract_markdown(filename, status: Status):
    # Gets the Markdown blocks out of the file, and adds them in the appropriate
    # locations in status.data
    with open(filename, 'r') as fp:
        lines = []
        for line in fp:
            line = line.rstrip('\n')
            cmd, args = split_string(line.strip())
            if cmd and cmd[0] in ['\\', '@']:
                if cmd[1:] == 'comment':
                    continue  # Ignore comments
                if cmd[1:] in documentation_commands:
                    # We found a new documentation command, which starts a new block to process.
                    # Process previous block first, then start a new block
                    if lines:
                        process_markdown_command(lines, status)
                    lines = [line]
                    continue
            # In all other cases, append the line to the block and continue
            lines.append(line)
        # At the end of the file, process the last block we collected
        process_markdown_command(lines, status)


# --- Parsing header files --- extracting declarations ---

def full_typename(decl):
    type = decl.displayname
    parent = decl.semantic_parent
    if not parent or parent.kind == cindex.CursorKind.TRANSLATION_UNIT:
        return type
    parent_type = full_typename(parent)
    if not type:
        return parent_type
    if parent_type:
        return parent_type + '::' + type
    return type

std_namespace_match = re.compile(r"^std::__.*::(.+)*$")

def process_type_recursive(type, cursor, output):
    kind = type.kind
    done = False
    # Reference/pointer qualifiers
    if kind in type_kind_to_type_map:
        process_type_recursive(type.get_pointee(), cursor, output)
        output['qualifiers'].append(type_kind_to_type_map[kind])
        done = True
    # Is it an array?
    if kind in type_kind_array_types:
        process_type_recursive(type.get_array_element_type(), None, output)
        output['qualifiers'].append('[]')
        done = True
    # Const qualifier
    if type.is_const_qualified():
        output['qualifiers'].append('const')
    if done:
        return
    # Actual type
    decl = type.get_declaration()
    if decl and decl.displayname:
        typename = full_typename(decl)
    elif kind in type_kind_to_name_map:
        typename = type_kind_to_name_map[kind]
    elif hasattr(type, 'spelling'):
        #canon = type.get_canonical()  # TODO: this is for function pointer types
        #if canon.kind == cindex.TypeKind.FUNCTIONPROTO:
        #    kind = canon.kind
        #    result = process_type(canon.get_result())
        #    arguments = [process_type(arg) for arg in canon.argument_types()]
        typename = type.spelling
        if typename.startswith('const '):
            typename = typename[len('const '):]
    elif cursor:
        typename = cursor.displayname
    else:
        typename = ''
    # Remove std namespace shenanigans
    match = std_namespace_match.fullmatch(typename)
    if match:
        typename = 'std::' + match[1]
    # Done
    output['typename'] = typename

def process_type(type, cursor=None):
    output = {'typename': '', 'qualifiers': []}
    process_type_recursive(type, cursor, output)
    return output

def find_default_value(tokens):
    for ii in range(len(tokens) - 1):
        if tokens[ii] == '=':
            return tokens[ii + 1]
    return None

def is_constexpr(item):
    name = item.spelling
    for t in item.get_tokens():
        if t.spelling == 'constexpr':
            return True
        if t.spelling == name:
            return False
    return False

def process_function_declaration(item, member):
    member['return_type'] = process_type(item.type.get_result())
    arguments = []
    for child in item.get_children():
        if child.kind == cindex.CursorKind.PARM_DECL:
            name = child.spelling
            param = None
            default = None
            for elem in child.get_children():
                if elem.kind == cindex.CursorKind.TYPE_REF:
                    param = process_type(child.type, cursor=elem)
                    default = find_default_value([x.spelling for x in child.get_tokens()])
                    break
            if param is None:
                param = process_type(child.type)
                default = find_default_value([x.spelling for x in child.get_tokens()])
            param['name'] = name
            param['default'] = default
            arguments.append(param)
    member['arguments'] = arguments

def merge_member(member, new_member):
    # Merges the two member structures, filling in empty elements in `member` with new data.
    # We don't append documentation, only replace, because Clang passes the same document block
    # every time we encounter a re-declaration of a member.
    for key in new_member:
        if key == 'members':
            for m in new_member['members']:
                if m not in member['members']:
                    member['members'].append(m)
            continue
        if key in member and not member[key]:
            member[key] = new_member[key]

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

        if item.kind in cursor_kind_to_type_map:
            # What are we dealing with?
            member_type = cursor_kind_to_type_map[item.kind]

            # Find out what the actual parent is.
            # The `parent` passed in is the member where this declaration lives (lexical parent),
            # but it not necessarily the actual (semantic) parent.
            # For example a class method defined outside the class body will have as the `parent` whatever
            # namespace this definition is written inside, rather than the class.
            # But for a using template, for some reason, the semantic parent of the template parameters is
            # set to the enclosing namespace rather than the using statement:
            # - namespace
            #     - TYPE_ALIAS_TEMPLATE_DECL
            #         - TEMPLATE_TYPE_PARAMETER (but semantic parent is "namespace")
            #         - TYPE_ALIAS_DECL (the actual 'using' statement)
            if member_type == 'templatenontypeparameter' or member_type == 'templatetypeparameter':
                semantic_parent = parent
            else:
                semantic_parent = item.semantic_parent
                if semantic_parent:
                    semantic_parent = item.semantic_parent.get_usr()
                if semantic_parent:
                    if semantic_parent in status.member_ids:
                        semantic_parent = status.member_ids[semantic_parent]
                    else:
                        log.error("USR of semantic parent was unknown, using lexical parent instead")
                        semantic_parent = parent
                else:
                    log.debug("Semantic parent not given, assuming lexical parent is semantic parent")
                    semantic_parent = parent

            log.debug("member: kind = %s, displayname = %s, spelling = %s, parent = %s, semantic_parent = %s",
                      item.kind, item.displayname, item.spelling, parent, semantic_parent)
            # log.debug("        tokens = %s", [x.spelling for x in item.get_tokens()])

            # Is the parent a namespace, or something else?
            parent_is_namespace = False
            if not semantic_parent or status.members[semantic_parent]['member_type'] == 'namespace':
                parent_is_namespace = True

            # Process base class specifier differently
            if member_type == 'basespecifier':
                if not semantic_parent:
                    log.error("Base class specifier has no semantic parent!?")
                    continue
                type = process_type(item.type, item)['typename']
                access = access_specifier_map[item.access_specifier]
                status.members[semantic_parent]['bases'].append({
                    'typename': type,
                    'access': access
                })
                continue

            # Process template parameters differently
            if member_type in ['templatenontypeparameter', 'templatetypeparameter']:
                name = item.spelling
                if not semantic_parent:
                    log.error("Template parameter %s doesn't have a parent", name)
                    return
                if 'template_parameters' not in status.members[semantic_parent]:
                    log.error("Template parameter %s has a parent that is not a template", name)
                    return
                default = None
                if member_type == 'templatetypeparameter':
                    type = 'type'
                    for child in item.get_children():
                        if child.kind == cindex.CursorKind.TYPE_REF:
                            default = process_type(child.type, child)
                        break
                else:
                    if not name:
                        # This happens for SFINAE template parameters
                        # TODO: This would happen for any parameter that is not named. What to do?
                        type = '<SFINAE>'
                        # TODO: To get a proper representation of this template parameter we'd need to
                        #       process the tokens manually.
                    else:
                        type = process_type(item.type, item)
                    default = find_default_value([x.spelling for x in item.get_tokens()])
                status.members[semantic_parent]['template_parameters'].append({
                    'name': name,
                    'type': type,
                    'default': default
                })
                continue

            # Disambiguate templated types:
            is_template = False
            if member_type == 'functiontemplate':
                is_template = True
                # Could be 'methodtemplate' also
                if parent_is_namespace:
                    member_type = 'function'
                else:
                    member_type = 'method'
            elif member_type == 'classtemplate':
                is_template = True
                member_type = 'class'
                # Could be 'structtemplate' also
                tokens = list(item.get_tokens())
                n = 0
                for i in range(len(tokens)):
                    if tokens[i].kind == cindex.TokenKind.PUNCTUATION and tokens[i].spelling == '<':
                        n += 1
                    if tokens[i].kind == cindex.TokenKind.PUNCTUATION and tokens[i].spelling == '>':
                        n -= 1
                        if n == 0:
                            i += 1
                            if i < len(tokens):
                                if tokens[i].kind == cindex.TokenKind.KEYWORD and tokens[i].spelling == 'struct':
                                    member_type = 'struct'
                            break
            elif member_type == 'usingtemplate':
                is_template = True
                member_type = 'using'

            # Create a member data structure for this member
            member = members.new_member('', item.spelling, member_type, semantic_parent, status.current_include_name)

            # Find the associated documentation comment and parse it
            comment = item.raw_comment
            if comment:
                if is_single_line_comment(comment):
                    comment = '\n'.join(clean_single_line_comment_block(comment))
                else:
                    comment = '\n'.join(clean_multiline_comment(comment, item.extent.start.column - 1))
                    # TODO: this start column is "iffy". We don't know where the comment actually starts!
                cmd, _ = split_string(comment)
                if not(len(cmd) > 1 and cmd[0] in ['\\', '@'] and cmd[1:] in documentation_commands):
                    member['brief'], member['doc'] = separate_brief(comment)

            # Fix constructor and destructor names for templated classes
            if member_type in ['constructor', 'destructor']:
                if item.semantic_parent.kind == cindex.CursorKind.CLASS_TEMPLATE:
                    # Remove the "<...>" at the end of the name
                    member['name'] = item.spelling.split('<', maxsplit=1)[0]

            # Find the group this member belongs to
            group, member['doc'] = find_ingroup_cmd(member['doc'])
            if parent_is_namespace:
                # Namespace members are grouped using "\defgroup" groups
                if not group:
                    group = get_group_at_line(status.group_locations, item.extent.start.line)
                member['group'] = group
            else:
                # Class, struct and union members are grouped using "\name" groups
                # For the enumvalue member type we get here too, but we clear the "group" element later
                # Also, we ignore any `\ingroup` commands
                if group:
                    log.warning("Ignoring \\ingroup command in documentation for %s\n   in file %s", member['name'],
                                status.current_include_name)
                member['group'] = get_group_at_line(status.group_locations, item.extent.start.line)

            # Associate any other information with this member
            process_children = False
            member['deprecated'] = item.availability == cindex.AvailabilityKind.DEPRECATED
            if member_type in ['class', 'struct']:
                member['templated'] = is_template
                member['bases'] = []
                member['derived'] = []
                member['members'] = []
                process_children = True
            elif member_type in ['method', 'conversionfunction', 'constructor', 'destructor']:
                member['templated'] = is_template
                member['static'] = item.is_static_method()
                member['virtual'] = item.is_virtual_method()
                member['pure_virtual'] = item.is_pure_virtual_method()
                member['const'] = item.is_const_method()
                member['access'] = access_specifier_map[item.access_specifier]
                member['constexpr'] = is_constexpr(item)
                member['method_type'] = member_type
                # TODO: a child member could be cindex.CursorKind.CXX_FINAL_ATTR?
                process_function_declaration(item, member)
                member_type = 'function'  # write out as function
            elif member_type == 'enumvalue':
                member['value'] = item.enum_value
                member['group'] = ''  # these should not be part of a group
            elif member_type == 'enum':
                member['scoped'] = item.is_scoped_enum()
                member['type'] = process_type(item.enum_type)['typename']
                member['members'] = []
                process_children = True
            elif member_type == 'field':
                member['type'] = process_type(item.type, item)
                member['static'] = item.storage_class == cindex.StorageClass.STATIC
                member['mutable'] = item.is_mutable_field()
                member['access'] = access_specifier_map[item.access_specifier]
                member['constexpr'] = is_constexpr(item)
                if item.is_bitfield():
                    member['width'] = item.get_bitfield_width()
                member_type = 'variable'
            elif member_type == 'function':
                member['templated'] = is_template
                member['constexpr'] = is_constexpr(item)
                process_function_declaration(item, member)
            elif member_type == 'namespace':
                member['members'] = []
                process_children = True
            elif member_type in ['typedef', 'using']:
                member_type = 'alias'
                type = process_type(item.underlying_typedef_type, item)
                if type['typename']:
                    member['type'] = type
                else:
                    member['type'] = {}  # This happens if we're processing a 'usingtemplate'. Leave the type
                    #                      empty so that it can be replaced later
                if is_template:
                    process_children = True
            elif member_type == 'union':
                member['members'] = []
                process_children = True
            elif member_type == 'variable':
                member['type'] = process_type(item.type, item)
                member['static'] = item.storage_class == cindex.StorageClass.STATIC
                member['constexpr'] = is_constexpr(item)
            if is_template:  # 'classtemplate', 'structtemplate', 'functiontemplate', 'methodtemplate', 'usingtemplate'
                member['template_parameters'] = []
            member['member_type'] = member_type
            # TODO: For template specializations, the following should be useful:
            # for ii in range(item.get_num_template_arguments()):
            #     kind = item.get_template_argument_kind(ii)
            #     if kind == cindex.TemplateArgumentKind.NULL:
            #         pass
            #     elif kind == cindex.TemplateArgumentKind.TYPE:
            #         item.get_template_argument_type(ii)
            #     elif kind == cindex.TemplateArgumentKind.DECLARATION:
            #         pass
            #     elif kind == cindex.TemplateArgumentKind.NULLPTR:
            #         pass
            #     elif kind == cindex.TemplateArgumentKind.INTEGRAL:
            #         item.get_template_argument_value(ii)
            #         item.get_template_argument_unsigned_value(ii)
            #     else:
            #         log.error("Template parameter kind not recognized")
            #         continue
            #

            # Deal with IDs -- we do this at the end of the above so we can use all that data to generate our ID.
            usr = item.get_usr()
            if usr in status.member_ids:
                id = status.member_ids[usr]
                log.debug("Member %s (%s) already exists, merging.", id, usr)
                merge_member(status.members[id], member)
            else:
                id = unique_id.member(member, status)
                log.debug("Member %s (%s) is new, adding.", id, usr)
                member['id'] = id
                status.member_ids[usr] = id
                if id in status.members:
                    log.error("USR was unknown, but ID was already there! This means that there is a name clash, "
                              "unique_id.member is not good enough")
                    continue  # skip the rest of this function, we're in trouble here...
                status.members[id] = member
                if semantic_parent:
                    status.members[semantic_parent]['members'].append(member)
                else:
                    status.data['members'].append(member)

            # Process child members
            if process_children:
                extract_declarations(item.get_children(), id, status)

        else:
            log.debug("ignore: kind = %s, spelling = %s, parent = %s", item.kind, item.spelling, parent)
            extract_declarations(item.get_children(), parent, status)


# --- Parsing header files --- extracting include statements ---

def is_under_directory(file, path):
    if os.path.commonpath([file, path]) == path:
        return os.path.relpath(file, path), True
    return file, False

def extract_includes(tu, status: Status, include_dirs):
    # Gets the list of files directly included by this one (not the ones included
    # by files included here).
    # include_dirs[0] is always the project's root dir
    this_file_includes = status.current_file['includes']
    it = tu.get_includes()
    for f in it:
        if f.depth == 1:
            include = os.path.realpath(f.include.name)
            include, in_project = is_under_directory(include, include_dirs[0])
            if not in_project:
                full_include = include
                for dir in include_dirs[1:]:
                    part, res = is_under_directory(full_include, dir)
                    if res and len(part) < len(include):
                        include = part
            if os.path.isabs(include):
                log.warning("Included file %s not in any of the directories on the path\n   in file %s",
                            include, status.current_include_name)
            this_file_includes.append({
                'filename': include,
                'in_project': in_project
            })


# --- Main function for this file ---

def buildtree(root_dir, input_files, additional_files, compiler_flags, include_dirs, options):
    """
    Builds the member tree as well as the headers, groups and pages lists, which together represent all
    the information about the code in the C++ project that is needed to produce useful documentation for
    the project.

    :param root_dir: The root directory for the header files, that you would pass to the compiler with `-I`
           when using the library (string)
    :param input_files: header files (with wildcards and path relative to working directory), space separated (string)
    :param additional_files: Markdown files (with wildcards and path relative to working directory), space
           separated (string)
    :param compiler_flags: flags to pass to the compiler (string)
    :param include_dirs: include directories to pass to the compiler (string)
    :param options: dictionary with options for how to process things

    Options can contain the keys:
    - 'code_formatting': 'yes' or 'no', indicating whether to use "`<name>`" or "<name>" when writing the name of
        members. The `` is Markdown for code formatting. This applies to the \ref command only, since formatting of
        member names elsewhere is done by the backend, not this function. If a member name is not preceded by \ref,
        this tool will not recognize it as such. Instead, manually add `` around member names if not referenced.
    """

    # Process the input parameters
    root_dir = os.path.realpath(root_dir)
    input_files = expand_sources(shlex.split(input_files))
    additional_files = expand_sources(shlex.split(additional_files))
    compiler_flags = compiler_flags.split()
    include_dirs = [os.path.realpath(x) for x in shlex.split(include_dirs, posix=False)]

    # Get system include directories and figure out compiler flags
    include_dirs = [root_dir] + libclang.get_system_includes(compiler_flags) + include_dirs
    compiler_flags += ['-I{0}'.format(x) for x in include_dirs]
    log.debug("Compiler flags: %s", ' '.join(compiler_flags))

    # Build the output file data representation
    data = {
        'members': [],
        'headers': [],
        'groups': [],
        'pages': []
    }

    # Our status
    status = Status(data)
    # Add a member for the base namespace, this makes traversing the tree easier.
    status.members = walktree.create_member_dict(status.data['members'])

    # Process all header files
    index = cindex.Index.create()
    processed = {}
    for f in input_files:
        # Skip file if already processed
        f = os.path.realpath(f)  # realpath makes for better comparisons
        if f in processed:
            continue

        # Get the name we'd use in an #include statement
        status.current_include_name = os.path.relpath(f, start=root_dir)
        log.info('Processing %s', status.current_include_name)
        status.current_file_name = f

        # Reset the rest of the data
        status.current_group = ['']
        status.group_locations = []

        # Add info for current file
        file_id = unique_id.header(status.current_include_name)
        status.current_file = members.new_header(file_id, status.current_include_name)
        status.data['headers'].append(status.current_file)
        status.files[file_id] = status.current_file

        # Parse the file
        tu = None
        try:
            tu = index.parse(f, compiler_flags, options=cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES +
                                                        cindex.TranslationUnit.PARSE_INCOMPLETE)
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
        extract_includes(tu, status, include_dirs)

        # Extract and process documentation comments with commands
        process_comments(tu, status)

        # Extract declarations and build member tree
        extract_declarations(tu.cursor.get_children(), '', status)

        # Mark this file as complete
        processed[f] = True

    # Process all stored member documentation that was not associated to a declaration in the sources
    for cmd in status.unprocessed_commands:
        process_documentation_command(cmd, status)
    status.unprocessed_commands = []

    # Process all additional files
    status.current_file = {}
    status.current_file_name = ''
    processed = {}
    for f in additional_files:
        # Record file name in `current_include_name` for use in error messages
        status.current_include_name = f

        # Skip file if already processed
        f = os.path.realpath(f)  # realpath makes for better comparisons
        if f in processed:
            continue
        log.info('Processing %s', f)

        # Reset the parts of status that we use
        status.current_group = ['']
        status.group_locations = []

        # Extract markdown blocks from file
        extract_markdown(f, status)

        # Mark file as complete
        processed[f] = True

    # Go through all members with a 'type' element, and replace the type dictionary with a string

    #    member['type']['typename'] = '[type name](#type-name-id) ' + ''.join(type['qualifiers'])
    # TODO
    # For functions, 'return_type' and 'arguments'.
    # For templated members, 'template_parameters'. If 'type' == 'type', examine 'default', otherwise examine 'type'.

    # Go through all classes with base classes, and:
    # - add links to derived classes
    #    member['derived'] = ['derived-class-id', 'derived-class-id', ...]
    # - add links to derived class members that override virtual base class members
    #    member['override'] = 'base-class-member-id'
    # - add links to the overridden virtual base class members
    #    member['overridden'] = ['derived-class-member-id', 'derived-class-member-id', ...]
    # TODO

    # Go through all members, headers, groups and pages, identify `\ref` and `\see` commands,
    # identify linked members, and replace with links
    # TODO

    # Go through all pages, identify `\subpage` commands, identify linked members, establish hierarchy,
    # and replace with links
    # TODO, see find_subpage_cmd()

    return status.data

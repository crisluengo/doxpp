# dox++
# Copyright 2020-2021, Cris Luengo
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

# Some global "constants" we set from the options
code_formatting = False
tab_size = 4

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
    cindex.TypeKind.NULLPTR: 'std::nullptr_t',
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
    'defgroup': 'group',
    'dir': 'dir',
    'endgroup': 'endgroup',
    'endname': 'endname',
    'enum': 'enum',
    'file': 'file',
    'fn': 'function',
    'function': 'function',
    'group': 'group',
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

        self.current_header = {}        # `files[i]` dict for  the current file.
        self.current_file_name = ''     # Full file name (with absolute path).
        self.current_header_name = ''   # File name relative to project root.

        self.members = {}               # These dictionaries contain the same dictionaries as in 'data',
        self.headers = {}               #    but indexed by their ID so they're easy to find. It is the
        self.groups = {}                #    *same* dictionaries, modifying these will modify 'data'.
        self.pages = {}                 #

        self.member_ids = {}            # A dictionary to translate USR to our ID for a member.

        self.anchors = {}               # A dictionary translating header anchors (IDs) to their text.

        self.unprocessed_commands = []  # Here we keep command documentation blocks that need to be processed later.


class DocumentationCommand:
    def __init__(self, cmd, args, doc, group, file, header_id=''):
        self.cmd = cmd
        self.args = args
        self.doc = doc
        self.group = group
        self.file = file
        self.header_id = header_id


def expand_sources(sources):
    ret = []
    for source in sources:
        if ('*' in source) or ('?' in source):
            source = glob.glob(source)
            if source:
                source.sort()
                ret.extend(source)
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
    comment = comment.expandtabs(tab_size)
    line = comment[3:]  # removes '///' or '//!'
    if len(line) > 0 and line[0] == '<':
        # This is if the comment is in the style "///< ..."
        line = line[1:]
    if len(line) > 0 and line[0] == ' ':
        line = line[1:]
    return line

def clean_single_line_comment_block(comment):
    lines = []
    for line in comment.splitlines():
        line = clean_comment(line.lstrip())
        lines.append(line)
    return lines

def clean_multiline_comment(comment, prelen=None):
    comment = comment.expandtabs(tab_size)
    start = 3
    if start < len(comment)  and comment[start] == '<':
        # This is if the comment is in the style "/**< ... */"
        start = 4
    lines = comment[start:-2].strip(' ').splitlines()
    # At this point, the first line is fixed, but the other lines might be indented uniformly
    if prelen:
        # Assume each line starting at 1 has `prelen` spaces in front. Let's remove them.
        for ii in range(1, len(lines)):
            if lines[ii][0:prelen].isspace():
                lines[ii] = lines[ii][prelen:]
            else:
                # TODO: should we warn here about shenanigans?
                pass
    if len(lines) == 1:
        return lines
    # At this point, all but the first line might have some uniform indentation, depending on the style
    # of the comment:
    #
    #   /*! foo             /*! foo             /** foo             /** foo
    #    * some text            some text       some text           *** some text
    #
    # We want to remove the same stuff from each of those lines. We look for a combination of spaces
    # and asterisks in the first line, compare all other lines to ensure they're all the same, then
    # remove that prefix. We should ignore empty lines though.
    if len(lines) == 2:
        # If there's only one additional line, strip any combination of spaces and asterisks at the left and be done.
        lines[1] = lines[1].lstrip(' *')
        return lines
    # Now we look for a common prefix
    tmp_lines = []
    for line in lines[1:]:
        if line.rstrip():
            tmp_lines.append(line)
    line1 = min(tmp_lines)
    line2 = max(tmp_lines)
    if line1 == line2:
        # This is a weird situation... Not sure what to do
        return lines
    prefix = os.path.commonprefix([line1, line2])
    if prefix:
        # All lines start with `prefix`. Ensure it is only spaces and asterisks.
        prelen = len(prefix) - len(prefix.lstrip(' *'))
        if len(line1) == prelen:
            # One of the lines only has our prefix. Can we add a space?
            if line2[prelen] == ' ':
                prelen += 1
        for ii in range(1, len(lines)):
            lines[ii] = lines[ii][prelen:]
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

ingroup_cmd_match = re.compile(r'^ *[\\@]ingroup +(.+?) *$', re.MULTILINE)

def find_ingroup_cmd(doc):
    # Finds `\ingroup <name>`, removes it from the documentation block, and returns `<name>`
    m = ingroup_cmd_match.search(doc)
    if m:
        group = m.group(1)
        doc = ingroup_cmd_match.sub('', doc).strip()
        return group, doc
    return '', doc

section_cmd_match = re.compile(r'^ *[\\@]((?:sub){,2})section +((?:\w|-)+) +(.*?) *$', re.MULTILINE)
anchor_cmd_match = re.compile(r'\n* *[\\@]anchor +((?:\w|-)+) *(?:$|\n)')

def find_anchor_cmds(doc, status: Status):
    # Finds section headings and explicit anchors, and adds them to a list.
    # `\section name title`, `\subsection name title`, `\subsubsection name title`, `\anchor name`
    # We're replacing with:
    # `# title {#name}`,     `## title {#name}`,       `### title {#name}`,         `{#name}`
    # We're listing them in the status.anchors dictionary.

    sections = []
    anchors = []

    def section_cmd_replace(match):
        level = len(match[1]) // 3 + 1
        name = match[2]
        title = match[3]
        if name in status.anchors:
            log.error("Anchor %s already exists, ignored.", name)
            return '{} {}'.format('#' * level, title)
        status.anchors[name] = title
        sections.append([name, title, level])
        return '{} {} {{#{}}}'.format('#' * level, title, name)

    def anchor_cmd_replace(match):
        name = match[1]
        if name in status.anchors:
            log.error("Anchor %s already exists, ignored.", name)
            return ''
        status.anchors[name] = ''
        anchors.append(name)
        return '\n{{: #{} }}\n\n'.format(name)

    doc = section_cmd_match.sub(section_cmd_replace, doc)
    doc = anchor_cmd_match.sub(anchor_cmd_replace, doc)
    return doc, sections, anchors

def is_token_char(char):
    return char.isalnum() or char=='_'

def ends_with_token_char(str):
    return str and is_token_char(str[-1])

def starts_with_token_char(str):
    return str and is_token_char(str[0])


# --- find_member ---

split_function_arg_parts = re.compile(r'(?:\w|:)+|\*|&+|\[]')  # Split qualifiers
split_function_args = re.compile(r'^((?:\w|:)+)\((.*)\)$')     # Split function from arguments

def parse_function_arguments(arg_list, start_id, members):
    if arg_list == ['']:  # This happens if the function is specified as `funcname()`.
        return []
    arguments = []
    for arg in arg_list:
        parts = split_function_arg_parts.findall(arg)
        if len(parts) > 1 and parts[0] == 'const':
            parts[0], parts[1] = parts[1], parts[0]  # Move the 'const' to after the type
        id = find_member(parts[0], start_id, members)
        if id:
            parts[0] = walktree.get_fully_qualified_name(id, members)
        arguments.append({
            'typename': parts[0],
            'qualifiers': ''.join(parts[1:])
        })
    return arguments

def same_argument(arg1, arg2):
    return arg1['typename'] == arg2['typename'] and arg1['qualifiers'] == arg2['qualifiers']

def find_member_match_names(member, names, function_params):
    if len(names) == 1:
        # We've matched the whole name
        if function_params is None:
            # No need to match function parameters
            return member['id']
        else:
            # We need to match function parameters too
            if member['member_type'] == 'function':
                args = member['arguments']
                if len(args) == len(function_params) and \
                        all([same_argument(arg1, arg2) for arg1, arg2 in zip(args, function_params)]):
                    return member['id']
            # TODO: We need to distinguish const member functions from the non-const version.
            #       This requires improving the matching for the type...
    elif 'members' in member:
        return find_member_inner(member['members'], names[1:], function_params)
    return ''

def find_member_inner(member_list, names, function_params):
    for member in member_list:
        if member['name'] == names[0]:
            id = find_member_match_names(member, names, function_params)
            if id:
                return id
    return ''

def find_member(name, start_id, members):
    """
    :param name: Name of the member to be found (string).
    :param start_id: ID of the member in whose context `name` is given (string).
    :param members: The member dictionary, as returned by `create_member_dict`.
    :return: ID of the member `name`, or an empty string if no match exists.

    Finds a member with name `name`, as a direct child of `start_id`, or as a direct child of the parent
    of `start_id`, recursively visiting its parents too. This is equivalent to identifying a name in the
    context of the member `start_id`.
    Returns the `id` of the first match found. If `name` has parenthesis, these are assumed to contain
    function arguments, and will be used to disambiguate in the case of overloaded functions.
    """
    # TODO: This doesn't work correctly for members injected into a different namespace, for example
    #       members of inline namespaces, anonymous namespaces, or through a `using` statement.
    name = name.strip()
    if not name:
        return ''
    function_params = None
    if name.startswith('operator'):
        part = name[len('operator'):].strip()
        # We can have:
        # - <op>     + - * / % ^ & | ~ ! = < > += -= *= /= %= ^= &= |= << >> >>= <<= == != <= >= <=> && || ++ -- , ->* -> () []
        # - <type>
        # - new
        # - new[]
        # - delete
        # - delete[]
        # - ""<name>
        # - co_await  (new in C++20)
        if not part:
            log.warning('I see "operator" as a member name, forgot quotes?')
            return ''
        if part[0] == '(':
            if part[1] != ')':
                log.error('Cannot parse "%s" as member name', name)
                return ''
            name = 'operator()'
            args = part[2:].strip()
            if args:
                if args[0] != '(' or args[-1] != ')':
                    log.error('Cannot parse "%s" as member name', name)
                    return ''
                args = args[1:-1]
        else:
            part, args = split_string(part, '(')
            args = args.strip()
            if args:
                if args[-1] != ')':
                    log.error('Cannot parse "%s" as member name', name)
                    return ''
                args = args[0:-1]
            if part[0].isalpha():
                part = ' ' + part
            name = ('operator' + part).strip()
        if args:
            function_params = parse_function_arguments(args.split(','), start_id, members)
    elif '(' in name:
        match = split_function_args.fullmatch(name)
        if not match:
            log.error('Cannot parse "%s" as member name', name)
            return ''
        name = match[1]
        function_params = parse_function_arguments(match[2].split(','), start_id, members)
    elif name in type_kind_to_name_map.values():
        # Ignore standard types
        return ''
    names = name.split('::')  # TODO: This goes wrong with `operator ns::type`.
    if not names:
        return ''
    base = members[start_id]
    if not 'members' in base:
        base = members[base['parent']]
    while True:
        if 'name' in base and base['name'] == names[0]:
            # prefer 'Name' over 'Name::Name'
            id = find_member_match_names(base, names, function_params)
            if id:
                return id
        id = find_member_inner(base['members'], names, function_params)
        if id:
            return id
        if 'parent' not in base:
            return ''
        base = members[base['parent']]


def find_file(name, headers):
    # Find header file we're referring to. We look for all matches with an arbitrary set of path elements
    # prepended. The one with fewest such prepended path elements is the one we pick.
    best_match = ''
    match_length = 1e9  # some number larger than any possible number of path elements, basically Infty.
    for header in headers.values():
        hdr = header['name']
        if hdr == name:
            return header['id']
        n = hdr.count(os.sep)  # TODO: we should normalize paths to always use '/'
        if n < match_length and hdr.endswith(os.sep + name):
            match_length = n
            best_match = header['id']
    return best_match


# --- Post-process documentation to add links ---

def get_type_id_or_empty_string(type, start_id, template_params, members):
    if type['typename'] in template_params:
        return ''
    if 'function_prototype' in type and type['function_prototype']:
        type['retval']['id'] = get_type_id_or_empty_string(type['retval'], start_id, template_params, members)
        for arg in type['arguments']:
            arg['id'] = get_type_id_or_empty_string(arg, start_id, template_params, members)
        return ''
    return find_member(type['typename'], start_id, members)

def collect_template_params(member, template_params, members):
    # Recurse through `member` and its ancestors, noting any template parameter names they have
    if 'templated' in member and member['templated']:
        for t in member['template_parameters']:
            if t['type'] == 'type':
                template_params.add(t['name'])
    if 'parent' in member and member['parent']:
        collect_template_params(members[member['parent']], template_params, members)

def post_process_types(members):
    # Add 'id' member to 'type' dicts
    for member in members.values():
        template_params = set()
        collect_template_params(member, template_params, members)
        if 'type' in member and isinstance(member['type'], dict):
            member['type']['id'] = get_type_id_or_empty_string(member['type'], member['id'], template_params, members)
        if 'return_type' in member and member['return_type']:
            member['return_type']['id'] = get_type_id_or_empty_string(member['return_type'], member['id'], template_params, members)
        if 'arguments' in member:
            for arg in member['arguments']:
                arg['id'] = get_type_id_or_empty_string(arg, member['id'], template_params, members)
        if 'template_parameters' in member:
            for arg in member['template_parameters']:
                if isinstance(arg['default'], dict):
                    arg['default']['id'] = get_type_id_or_empty_string(arg['default'], member['id'], template_params, members)
                elif isinstance(arg['type'], dict):
                    arg['type']['id'] = get_type_id_or_empty_string(arg['type'], member['id'], template_params, members)

def cleanup_qualifiers(member):
    # Replace 'qualifiers' member in 'type' dicts with a string
    if 'type' in member and isinstance(member['type'], dict) and member['type']:
        member['type']['qualifiers'] = ''.join(member['type']['qualifiers'])
    if 'return_type' in member and member['return_type']:
        member['return_type']['qualifiers'] = ''.join(member['return_type']['qualifiers'])
    if 'arguments' in member:
        for arg in member['arguments']:
            arg['qualifiers'] = ''.join(arg['qualifiers'])
    if 'template_parameters' in member:
        for arg in member['template_parameters']:
            if isinstance(arg['default'], dict):
                arg['default']['qualifiers'] = ''.join(arg['default']['qualifiers'])
            elif isinstance(arg['type'], dict):
                arg['type']['qualifiers'] = ''.join(arg['type']['qualifiers'])

def post_process_inheritance(members):
    # Add links to derived classes in the base classes
    for member in members.values():
        if 'bases' in member:
            for base in member['bases']:
                name = base['typename']
                id = find_member(name, '', members)
                if id:
                    base['id'] = id
                    base_member = members[id]
                    base_member['derived'].append(member['id'])

ref_cmd_match = re.compile(r'[\\@]ref +((?:\w|::|%|-)+(?: *\(.*?\))?)(?: +"(.*?)")?')
ref_cmd_quotes_match = re.compile(r'[\\@]ref +"((?:[^"]|"")+)"(?: +"(.*?)")?')
see_cmd_match = re.compile(r'^ *[\\@](?:see|sa) +(.+?) *$', re.MULTILINE)  # TODO: multiline `\see`?
see_arg_match = re.compile(r'([^,(]+(?:\(.*?\))?)')  # Split \see command arguments

def post_process_links(elements, status: Status):
    # Process documentation for `\ref` and `\see` commands
    for elem in elements.values():

        def find_if_member(name, text):
            parent = elem['id']
            if parent not in status.members:
                parent = ''
            id = find_member(name, parent, status.members)
            if id:
                if not text:
                    text = name
                    if code_formatting:
                        text = '`{}`'.format(text)
            return id, text

        def find_and_format_name(name, text):
            # For matches of member name, or any ID
            id, text = find_if_member(name, text)
            if not id:
                if name in status.members:
                    id = name
                    if not text:
                        text = status.members[id]['name']
                    if code_formatting:
                        text = '`{}`'.format(text)
                elif name in status.groups:
                    id = name
                    if not text:
                        text = status.groups[id]['name']
                elif name in status.pages:
                    id = name
                    if not text:
                        text = status.pages[id]['title']
                elif name in status.headers:
                    id = name
                    if not text:
                        text = status.headers[id]['name']
                elif name in status.anchors:
                    id = name
                    if not text:
                        text = status.anchors[id]
                else:
                    log.error("Reference to '%s' could not be matched.\n   in documentation for %s", name, elem['id'])
                    return text
            return '[{}](#{})'.format(text, id)

        def find_and_format_quotes_name(name, text):
            # For matches of header name, member name, or any ID, when given in quotes
            id = find_file(name, status.headers)
            if id:
                if not text:
                    text = status.headers[id]['name']
                return '[{}](#{})'.format(text, id)
            return find_and_format_name(name, text)

        def ref_cmd_replace(match):
            return find_and_format_name(match[1], match[2])

        def ref_cmd_quotes_replace(match):
            return find_and_format_quotes_name(match[1], match[2])

        def see_cmd_replace(match):
            # For matches of a `\see` or `\sa` command.
            output = '!!! see\n    '
            first = True
            for element in see_arg_match.findall(match[1]):
                # TODO: the regexp above doesn't work for `operator,`
                element = element.strip()
                if element[0] == '"':
                    link = find_and_format_quotes_name(element[1:-1], '')
                else:
                    link = find_and_format_name(element, '')
                if first:
                    first = False
                else:
                    output += ', '
                output += link
            output += '\n\n'
            return output

        if 'brief' in elem:  # this one not present in pages
            elem['brief'] = ref_cmd_match.sub(ref_cmd_replace, elem['brief'])
            elem['brief'] = ref_cmd_quotes_match.sub(ref_cmd_quotes_replace, elem['brief'])
        if 'doc' in elem:  # this one is missing if elem is status.members['']
            elem['doc'] = ref_cmd_match.sub(ref_cmd_replace, elem['doc'])
            elem['doc'] = ref_cmd_quotes_match.sub(ref_cmd_quotes_replace, elem['doc'])
            elem['doc'] = see_cmd_match.sub(see_cmd_replace, elem['doc'])

relates_cmd_match = re.compile(r'^ *[\\@]relate[sd] +(.+?) *$', re.MULTILINE)

def post_process_relates(members):
    # Process documentation for `\relates` commands (and `\related` synonym)
    for member in members.values():

        def relates_cmd_replace(match):
            id = find_member(match[1], member['id'], members)
            if id and members[id]['member_type'] in ['class', 'struct', 'union']:
                members[id]['related'].append(member['id'])
                member['relates'] = id
            else:
                log.error("Reference %s could not be matched to class or struct.\n   in documentation for %s", match[1], member['id'])
            return ''

        if 'doc' in member:  # this one is missing if member is status.members['']
            # We only look for the command in documentation to functions, variables, macros, aliases, enums
            if member['member_type'] in ['function', 'variable', 'macro', 'alias', 'enum']:
                parent = member['parent']
                # We only look for the command in documentation to namespace members (not class, struct, union or enum members)
                if not parent or members[parent]['member_type'] == 'namespace':
                    member['brief'] = relates_cmd_match.sub(relates_cmd_replace, member['brief'], count=1)
                    if not member['relates']:
                        member['doc'] = relates_cmd_match.sub(relates_cmd_replace, member['doc'], count=1)
                    # count=1 means we only handle the first occurrence of the command. Delete any further commands:
                    member['brief'] = relates_cmd_match.sub('', member['brief'])
                    member['doc'] = relates_cmd_match.sub('', member['doc'])
                    # TODO: produce error if there are more of these commands?

subpage_cmd_match = re.compile(r'[\\@]subpage +((?:\w|-)+(?: *\(.*?\))?)(?: +"(.*?)")?')

def post_process_subpages(pages):
    # Process documentation for `\subpage` commands
    for page in pages.values():

        def subpage_cmd_replace(match):
            id = match[1]
            text = match[2]
            if not text:
                text = pages[id]['title']
            if id not in pages:
                log.error("Page reference %s could not be matched.\n   in documentation for %s", id, page['id'])
                return text
            # Check to ensure `id` doesn't already have a parent
            if pages[id]['parent']:
                log.error("Page %s already has a parent.\n   in documentation for %s", id, page['id'])
                return text
            # Check to ensure `id` is not an ancestor of `page`
            parent = page['parent']
            while parent:
                if parent == id:
                    log.error("Page %s is an ancestor of %s.\n   in documentation for %s", id, page['id'], page['id'])
                    return text
                parent = pages[parent]['parent']
            page['subpages'].append(id)
            pages[id]['parent'] = page['id']
            return '[{}](#{})'.format(text, id)

        page['doc'] = subpage_cmd_match.sub(subpage_cmd_replace, page['doc'])
        pass


# --- Processing documentation commands ---

def process_generic_command(cmd: DocumentationCommand, status: Status):
    # \cmd <name>
    # \cmd <id>
    if not cmd.args:
        log.error("\\%s needs a name argument\n   in file %s", cmd.cmd, cmd.file)
        return
    name, args = split_string(cmd.args)
    if args:
        log.warning("Ignoring additional arguments to \\%s command\n   in file %s", cmd.cmd, cmd.file)
    # Find which member we're talking about
    if name in status.members:
        id = name
    else:
        id = find_member(name, '', status.members)
    if not id:
        log.error("The member '%s' has not been declared, documentation ignored.\n   in file %s", cmd.args, cmd.file)
        return
    member = status.members[id]
    group, doc = find_ingroup_cmd(cmd.doc)
    if not group:
        group = cmd.group
    if member['group']:
        if group and member['group'] != group:
            log.warning("Member '%s' already is in group %s, cannot assign to group %s.\n   in file %s",
                        id, member['group'], group, cmd.file)
    else:
        member['group'] = group
    brief, doc = separate_brief(doc)
    doc, sections, anchors = find_anchor_cmds(doc, status)
    add_doc(member, brief, doc)
    member['sections'].extend(sections)
    member['anchors'].extend(anchors)

def process_macro_command(cmd: DocumentationCommand, status: Status):
    # \macro <name>
    if not cmd.args:
        log.error("\\macro needs a name argument.\n   in file %s", cmd.file)
        return
    name = cmd.args
    macro_params = []
    if '(' in name:
        match = split_function_args.fullmatch(name)
        if not match:
            log.error("Cannot parse macro name '%s', ignoring documentation.\n   in file %s", name, cmd.file)
            return
        name = match[1]
        macro_params = match[2].split(',')
        for ii in range(len(macro_params)):
            macro_params[ii] = macro_params[ii].strip()
    if not unique_id.is_valid(name):
        log.error("'%s' is not a valid name for a macro, ignoring documentation.\n   in file %s", name, cmd.file)
    # Do we already have a member for this macro?
    id = unique_id.macro(name)
    group, doc = find_ingroup_cmd(cmd.doc)
    if not group:
        group = cmd.group
    if id in status.members:
        # Add data to existing member
        member = status.members[id]
        if member['member_type'] != 'macro':
            log.error("Documenting a macro with ID %s that is identical to an existing non-macro.\n   in file %s",
                      id, cmd.file)
            return
        if member['macro_params'] != macro_params:
            log.warning("Documenting a previously documented macro, this time the parameters are different.\n" +
                        "   in file %s", id, cmd.file)
        brief, doc = separate_brief(doc)
        doc, sections, anchors = find_anchor_cmds(doc, status)
        add_doc(member, brief, doc)
        member['sections'].extend(sections)
        member['anchors'].extend(anchors)
        if not member['group']:
            member['group'] = group
    else:
        # Create a new member
        member = members.new_member(id, name, 'macro', '', cmd.header_id)
        brief, doc = separate_brief(doc)
        doc, sections, anchors = find_anchor_cmds(doc, status)
        member['brief'] = brief
        member['doc'] = doc
        member['sections'] = sections
        member['anchors'] = anchors
        member['group'] = group
        member['macro_params'] = macro_params
        status.members[id] = member
        status.data['members'].append(member)

def process_file_command(cmd: DocumentationCommand, status: Status):
    # \file <name>
    # Note that the no-name version has already been processed
    if not cmd.args:
        log.error("\\file needs a file name when not in a header file\n   in file %s", cmd.file)
        return
    id = find_file(cmd.args, status.headers)
    if not id:
        log.error("The file '%s' has not been parsed, documentation ignored.\n   in file %s", cmd.args, cmd.file)
        return
    header = status.headers[id]
    brief, doc = separate_brief(cmd.doc)
    doc, sections, anchors = find_anchor_cmds(doc, status)
    add_doc(header, brief, doc)
    header['sections'].extend(sections)
    header['anchors'].extend(anchors)

def create_page(name, title, doc, file, status: Status):
    if name in status.pages:
        # Page already exists, append documentation
        page = status.pages[name]
        doc, sections, anchors = find_anchor_cmds(doc, status)
        cur_doc = page['doc']
        if cur_doc:
            doc = cur_doc + '\n\n' + doc
        page['doc'] = doc
        page['sections'].extend(sections)
        page['anchors'].extend(anchors)
    else:
        # Validate `name` to have only {\w|-} characters
        if not unique_id.is_valid(name):
            log.error("\\page has invalid name '%s', documentation ignored.\n   in file %s", name, file)
            return
        # Create new page
        doc, sections, anchors = find_anchor_cmds(doc, status)
        page = members.new_page(name, title, doc)
        page['sections'] = sections
        page['anchors'] = anchors
        status.data['pages'].append(page)
        status.pages[name] = page

def process_mainpage_command(cmd: DocumentationCommand, status: Status):
    title = cmd.args
    if not title:
        title = "Main"
    create_page('index', title, cmd.doc, cmd.file, status)

def process_page_command(cmd: DocumentationCommand, status: Status):
    name, title = split_string(cmd.args)
    if not name or not title:
        log.error("\\page requires a name and title, documentation ignored.\n   in file %s", cmd.file)
        return
    create_page(name, title, cmd.doc, cmd.file, status)

def process_documentation_command(cmd: DocumentationCommand, status: Status):
    # This function processes commands that add documentation to members
    if cmd.cmd == 'dir':
        log.error("\\dir not implemented, documentation ignored.\n   in file %s", cmd.file)
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

def process_grouping_command(cmd, args, doc, loc, status: Status):
    # This function processes commands that handle grouping of members.
    # Returns True if the command was processed, false otherwise.
    #
    # Grouping commands work differently than in Doxygen:
    # \group defines a group.
    # \addtogroup makes subsequent definitions fall within the group.
    # \endgroup stops the current group.
    # Defining a group within a group causes nested groups. Also adding \ingroup to the group's
    # documentation causes it to be nested.
    # \name and \endname open and close a class member group, they can appear anywhere but they
    # only have an effect on class (or struct) members.
    if cmd == 'group':
        id, name = split_string(args.strip())
        if not id or not name:
            log.error("\\group needs a name and a title.\n   in file %s", status.current_header_name)
            return True
        if not unique_id.is_valid(id):
            log.error("\\group has invalid name '%s', ignored.\n   in file %s", id, status.current_header_name)
            return True
        parent_group, doc = find_ingroup_cmd(doc)
        has_ingroup = True
        if not parent_group:
            parent_group = status.current_group[-1]
            has_ingroup = False
        open_group = False
        if doc.endswith('\\addtogroup'):
            open_group = True
            doc = doc[:-len('\\addtogroup')].strip()
        brief, doc = separate_brief(doc)
        doc, sections, anchors = find_anchor_cmds(doc, status)
        if id not in status.groups:
            group = members.new_group(id, name, brief, doc, parent_group)
            group['sections'] = sections
            group['anchors'] = anchors
            status.groups[id] = group
            status.data['groups'].append(group)
        else:
            group = status.groups[id]
            if not group['name']:
                group['name'] = name
            if group['parent']:
                if has_ingroup and parent_group != group['parent']:
                    log.warning("\\ingroup command ignored, group %s already has a parent.\n   in file %s", id, status.current_header_name)
                parent_group = ''  # ignore the parent group chosen here.
            else:
                group['parent'] = parent_group
            add_doc(group, brief, doc)
            group['sections'].extend(sections)
            group['anchors'].extend(anchors)
        if parent_group:
            if parent_group in status.groups:
                group = status.groups[parent_group]
            else:
                group = members.new_group(parent_group)
                status.groups[parent_group] = group
                status.data['groups'].append(group)
            if group['subgroups'].count(id) == 0:  # add group only once
                group['subgroups'].append(id)
        if open_group:
            status.current_group.append(id)
            status.group_locations.append((loc, id))
        return True
    if cmd == 'addtogroup':
        id, name = split_string(args)
        # We ignore name here
        if not id:
            log.error("\\addtogroup needs a name\n   in file %s", status.current_header_name)
            return True
        if not unique_id.is_valid(id):
            log.error("\\addtogroup has invalid name '%s', ignored.\n   in file %s", id, status.current_header_name)
            return True
        if doc:
            log.warning("Ignoring documentation block associated to \\addtogroup command\n   in file %s",
                        status.current_header_name)
        if id not in status.groups:
            status.groups[id] = members.new_group(id)
            status.data['groups'].append(status.groups[id])
        status.current_group.append(id)
        status.group_locations.append((loc, id))
        return True
    if cmd == 'endgroup':
        parent_group = status.current_group[-1]
        if parent_group:
            status.current_group.pop()
            status.group_locations.append((loc, status.current_group[-1]))
        else:
            log.warning("\\endgroup must occur after an \\addtogroup command\n   in file %s",
                        status.current_header_name)
        if doc:
            log.warning("Ignoring documentation block associated to \\endgroup command\n   in file %s",
                        status.current_header_name)
        return True
    if cmd == 'name':
        status.current_member_group = args
        status.member_group_locations.append((loc, args))
        return True
    if cmd == 'endname':
        status.current_member_group = ''
        status.member_group_locations.append((loc, ''))
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
    doc = '\n'.join(lines[1:]).strip()

    # Grouping commands
    if process_grouping_command(cmd, args, doc, loc, status):
        return

    # Documenting the current file
    if cmd == 'file' and not args:
        brief, doc = separate_brief(doc)
        doc, sections, anchors = find_anchor_cmds(doc, status)
        add_doc(status.current_header, brief, doc)
        status.current_header['sections'].extend(sections)
        status.current_header['anchors'].extend(anchors)
        return

    # Documenting things we don't declare right here, this we'll do after processing all header files
    status.unprocessed_commands.append(DocumentationCommand(cmd, args, doc, status.current_group[-1],
                                                            status.current_header_name, status.current_header['id']))

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
                    status.current_group.pop(), status.current_header_name)
    if status.current_member_group:
        log.warning("Missing \\endname\n   in file %s", status.current_header_name)

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
    doc = '\n'.join(lines[1:]).strip()

    # Grouping commands
    if process_grouping_command(cmd, args, doc, 0, status):
        return

    # Documentation
    process_documentation_command(DocumentationCommand(cmd, args, doc, status.current_group[-1],
                                                       status.current_header_name), status)

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

fixup_angled_brackets_match = re.compile(r"> >")

def process_type_recursive(type, cursor, output):
    kind = type.kind
    done = False
    # Reference/pointer qualifiers
    if kind in type_kind_to_type_map:
        process_type_recursive(type.get_pointee(), cursor, output)
        if not('function_prototype' in output and output['function_prototype']):
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
    if kind in type_kind_to_name_map:
        output['typename'] = type_kind_to_name_map[kind]
    elif kind == cindex.TypeKind.FUNCTIONPROTO:
        # Parse function prototype
        output['function_prototype'] = True
        output['retval'] = process_type(type.get_result(), None)
        output['arguments'] = [process_type(arg) for arg in type.argument_types()]
        # output['typename'] = type.spelling
        output['typename'] = output['retval']['typename'] + '(*)(' + \
                             ', '.join([arg['typename'] for arg in output['arguments']]) + ')'
    elif hasattr(type, 'spelling'):
        typename = type.spelling
        if typename.startswith('const '):
            typename = typename[len('const '):]
        typename = fixup_angled_brackets_match.sub('>>', typename)
        output['typename'] = typename
    elif cursor:
        output['typename'] = cursor.displayname
    else:
        output['typename'] = ''
    # TODO: For template types, we might want to split up the type and the template arguments (recursively!)
    #       so that we can later link the type to its docs.

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

def is_inline(item):
    name = item.spelling
    for t in item.get_tokens():
        if t.spelling == 'inline':
            return True
        if t.spelling == name:
            return False
    return False

def is_explicit(item):
    name = item.spelling
    for t in item.get_tokens():
        if t.spelling == 'explicit':
            return True
        if t.spelling == name:
            return False
    return False

def get_defaulted_or_deleted(item):
    # `item` is a declaration for a constructor, destructor or assignment operator.
    # We look for the first '(' character, then for the matching ')' character. If the next
    # character is '=', it will be followed by either 'default' or 'delete' (or '0').
    # TODO: Is this logic always correct?
    # TODO: In C++20, comparison operators can be default as well.
    i = item.get_tokens()
    try:
        t = next(i)
        while t.spelling != '(':
            t = next(i)
        count = 1
        t = next(i)
        while True:
            if t.spelling == '(':
                count += 1
            elif t.spelling == ')':
                count -= 1
            t = next(i)
            if count == 0:
                break
        if t.spelling == '=':
            return next(i).spelling
    except StopIteration:
        pass
    return ''

def process_template_type_parameter(item):
    name = item.spelling
    if not name:
        # This happens for SFINAE template parameters
        # TODO: This would happen for any parameter that is not named. What to do?
        name = '<SFINAE>'
        # TODO: To get a proper representation of this template parameter we'd need to
        #       process the tokens manually.
    default = None
    for child in item.get_children():
        if child.kind == cindex.CursorKind.TYPE_REF:
            default = process_type(child.type, child)
            break
    return {
        'name': name,
        'type': 'type',
        'default': default
    }

def process_template_nontype_parameter(item):
    name = item.spelling
    if not name:
        # This happens for SFINAE template parameters
        # TODO: This would happen for any parameter that is not named. What to do?
        name = '<SFINAE>'
        type = {'typename': '', 'qualifiers': []}
        # TODO: To get a proper representation of this template parameter we'd need to
        #       process the tokens manually.
    else:
        type = process_type(item.type, item)
    default = find_default_value([x.spelling for x in item.get_tokens()])
    return {
        'name': name,
        'type': type,
        'default': default
    }

def process_function_declaration(item, member):
    member['constexpr'] = is_constexpr(item)
    member['noexcept'] = item.exception_specification_kind in [cindex.ExceptionSpecificationKind.BASIC_NOEXCEPT, cindex.ExceptionSpecificationKind.COMPUTED_NOEXCEPT]
    member['return_type'] = process_type(item.type.get_result())
    arguments = []
    template_parameters = []
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
        elif child.kind == cindex.CursorKind.CXX_FINAL_ATTR:
            member['final'] = True
        elif child.kind == cindex.CursorKind.CXX_OVERRIDE_ATTR:
            member['override'] = True
        elif child.kind == cindex.CursorKind.TEMPLATE_NON_TYPE_PARAMETER:
            template_parameters.append(process_template_nontype_parameter(child))
        elif child.kind == cindex.CursorKind.TEMPLATE_TYPE_PARAMETER:
            template_parameters.append(process_template_type_parameter(child))
    member['arguments'] = arguments
    if member['templated']:
        member['template_parameters'] = template_parameters
    elif template_parameters:
        log.warning('Unexpected thing happened here: a non-templated function has template parameters!')

def merge_member(member, new_member):
    # Merges the two member structures, filling in empty elements in `member` with new data.
    # We don't append documentation, only replace, because Clang passes the same document block
    # every time we encounter a re-declaration of a member.
    # Because a class can have a forward declaration in a different file, and that file could
    # have been processed earlier, if the existing structure has no 'brief', we replace everything.
    # This assumes that it is the actual declaration that is documented, not the forward declaration.
    replace = new_member['brief'] and not member['brief']
    for key in new_member:
        if key == 'members':
            for m in new_member['members']:
                if m not in member['members']:
                    member['members'].append(m)
            continue
        if replace or (key not in member or not member[key]):
            member[key] = new_member[key]

def add_undocumented_member(item: cindex.Cursor, status: Status):
    # Adds members to status.data (and status.members) without much information, to be filled in
    # at a later time, for the purpose of documenting its members now. This is called when documenting
    # the child of a member that has been declared in an #included header file, and that header file
    # is either not part of the documentation input, or it will be parsed later.
    if item.kind in cursor_kind_to_type_map:
        # What are we dealing with?
        member_type = cursor_kind_to_type_map[item.kind]
        if member_type not in ['namespace', 'class', 'struct', 'union']:
            log.error("This is unexpected!")
            return ''
        semantic_parent = ''
        semantic_parent_item = item.semantic_parent
        if semantic_parent_item:
            semantic_parent = semantic_parent_item.get_usr()
        if semantic_parent:
            if semantic_parent not in status.member_ids:
                add_undocumented_member(semantic_parent_item, status)
            semantic_parent = status.member_ids[semantic_parent]
        member = members.new_member('', item.spelling, member_type, semantic_parent, '')
        member['members'] = []
        id = unique_id.member(member, status)  # TODO: This goes wrong with templated types, we haven't figured out the template params, and the ID will be wrong here
        member['id'] = id
        status.member_ids[item.get_usr()] = id
        if id in status.members:
            log.error("USR for member %s was unknown, but ID %s was already there! This means that " +
                      "there is a name clash, unique_id.member is not good enough.\n   in file %s",
                      member['name'], id, status.current_header_name)
            return ''
        status.members[id] = member
        if semantic_parent:
            status.members[semantic_parent]['members'].append(member)
        else:
            status.data['members'].append(member)
        return id
    else:
        log.error("This is unexpected!")
        return ''

def extract_declarations(citer, parent, status: Status, level = 0):
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
            extract_declarations(item.get_children(), '', status, level)
            continue

        # Ignore files other than the ones we are scanning for
        if str(item.location.file) != status.current_file_name:
            continue

        # This section can be uncommented to display the full AST, useful for learning about it.
        # semantic_parent = item.semantic_parent
        # if semantic_parent:
        #     semantic_parent = semantic_parent.displayname
        # else:
        #     semantic_parent = 'None'
        # print('  ' * level, "- member: kind = %s, displayname = %s, spelling = %s, parent = %s, semantic_parent = %s" % (
        #       item.kind, item.displayname, item.spelling, parent, semantic_parent))
        # print('  ' * level, "          tokens =", [x.spelling for x in item.get_tokens()])
        # print('  ' * level, "          comment =", item.raw_comment)
        # extract_declarations(item.get_children(), item.displayname, status, level + 1)
        # continue

        # Ignore unexposed things
        if item.kind == cindex.CursorKind.UNEXPOSED_DECL:
            extract_declarations(item.get_children(), parent, status)
            continue

        if item.kind == cindex.CursorKind.CXX_FINAL_ATTR:
            # This should only happen for classes
            status.members[parent]['final'] = True
            continue

        if item.kind in cursor_kind_to_type_map:
            # What are we dealing with?
            member_type = cursor_kind_to_type_map[item.kind]
            name = item.spelling

            # Find out what the actual parent is.
            #
            # The `parent` passed in is the member where this declaration lives (lexical parent),
            # but it not necessarily the actual (semantic) parent.
            # For example a class method defined outside the class body will have as the `parent` whatever
            # namespace this definition is written inside, rather than the class.
            #
            # But for a using template, for some reason, the semantic parent of the template parameters is
            # set to the enclosing namespace rather than the using statement:
            # - namespace
            #     - TYPE_ALIAS_TEMPLATE_DECL
            #         - TEMPLATE_TYPE_PARAMETER (but semantic parent is "namespace")
            #         - TYPE_ALIAS_DECL (the actual 'using' statement)
            if member_type == 'templatenontypeparameter' or member_type == 'templatetypeparameter':
                semantic_parent = parent
            else:
                semantic_parent = ''
                semantic_parent_item = item.semantic_parent
                if semantic_parent_item:
                    semantic_parent = semantic_parent_item.get_usr()
                if semantic_parent:
                    if semantic_parent in status.member_ids:
                        semantic_parent = status.member_ids[semantic_parent]
                    else:
                        # This seems to happen in template specializations.
                        # It also also when a class member definition is in a header file that is not the
                        # header file where the class is defined, and that header file is processed first, such
                        # that the class is yet unknown.
                        if str(item.semantic_parent.location.file) == status.current_file_name:
                            # The semantic parent is defined in this file, this must be a template specialization
                            log.debug("Semantic parent for %s had unknown USR, but is defined in this file: skipping.\n   in file %s",
                                      item.semantic_parent.displayname + '::' + item.displayname, status.current_header_name)
                            continue
                        # The semantic parent is defined elsewhere, let's assume we'll be seeing the definition later
                        semantic_parent = add_undocumented_member(semantic_parent_item, status)
                        if not semantic_parent:
                            continue
                        log.warning("USR of semantic parent for %s was unknown, added undocumented member %s.\n   in file %s",
                                    item.displayname, semantic_parent, status.current_header_name)
                else:
                    log.debug("Semantic parent for %s not given, assuming lexical parent is semantic parent.\n" +
                              "   in file %s", item.displayname, status.current_header_name)
                    semantic_parent = parent

            log.debug("member: kind = %s, member_type = %s, displayname = %s, spelling = %s, parent = %s, semantic_parent = %s",
                      item.kind, member_type, item.displayname, item.spelling, parent, semantic_parent)
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
                if not semantic_parent:
                    log.error("Template parameter %s doesn't have a parent.\n   in file %s",
                              name, status.current_header_name)
                    return
                if 'template_parameters' not in status.members[semantic_parent]:
                    log.error("Template parameter %s has a parent that is not a template.\n   in file %s",
                              name, status.current_header_name)
                    return
                if member_type == 'templatetypeparameter':
                    param = process_template_type_parameter(item)
                else:
                    param = process_template_nontype_parameter(item)
                status.members[semantic_parent]['template_parameters'].append(param)
                continue

            # Process actual using element of templated using directive differently
            # We've already created the alias member, we are just missing the type
            if member_type == 'using' and parent and status.members[parent]['member_type'] == 'alias':
                type = process_type(item.underlying_typedef_type, item)
                type['qualifiers'] = ''.join(type['qualifiers'])
                status.members[parent]['type'] = type
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
                # Could be 'struct' or 'union' also
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
                                if tokens[i].kind == cindex.TokenKind.KEYWORD:
                                    if tokens[i].spelling == 'struct':
                                        member_type = 'struct'
                                    elif tokens[i].spelling == 'union':
                                        member_type = 'union'
                            break
            elif member_type == 'usingtemplate':
                is_template = True
                member_type = 'using'

            # Create a member data structure for this member
            member = members.new_member('', name, member_type, semantic_parent, status.current_header['id'])

            # Find the associated documentation comment and parse it
            group = ''
            comment = item.raw_comment
            if comment:
                if is_single_line_comment(comment):
                    comment = '\n'.join(clean_single_line_comment_block(comment))
                else:
                    comment = '\n'.join(clean_multiline_comment(comment))
                comment = comment.strip()
                cmd, _ = split_string(comment)
                if not(len(cmd) > 1 and cmd[0] in ['\\', '@'] and cmd[1:] in documentation_commands):
                    group, comment = find_ingroup_cmd(comment)
                    member['brief'], member['doc'] = separate_brief(comment)
                    member['doc'], member['sections'], member['anchors'] = find_anchor_cmds(member['doc'], status)

            # Fix constructor and destructor names for templated classes
            if member_type in ['constructor', 'destructor']:
                if item.semantic_parent.kind == cindex.CursorKind.CLASS_TEMPLATE:
                    # Remove the "<...>" at the end of the name
                    member['name'] = name.split('<', maxsplit=1)[0]

            # Fix conversion operator names
            # Clang gives the name to the base type, not to the name of an alias as it might appear in the source code
            if name.startswith('operator '):
                i = item.get_tokens()
                try:
                    t = next(i)
                    while t.spelling != 'operator':
                        t = next(i)
                    t = next(i)
                    type = ''
                    while t.spelling != '(':
                        p = t.spelling
                        if ends_with_token_char(type) and starts_with_token_char(p):
                            p = ' ' + p
                        type += p
                        t = next(i)
                    member['name'] = 'operator ' + type
                except StopIteration:
                    log.error("Couldn't find conversion operator type for %s\n   in file %s",
                              name, status.current_header_name)
                    pass

            # Find the group this member belongs to
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
                    log.warning("Ignoring \\ingroup command in documentation for %s\n   in file %s",
                                member['name'], status.current_header_name)
                member['group'] = get_group_at_line(status.member_group_locations, item.extent.start.line)

            # Associate any other information with this member
            process_children = False
            member['deprecated'] = item.availability == cindex.AvailabilityKind.DEPRECATED
            if member_type in ['class', 'struct']:
                if not item.is_definition():
                    # This is a forward declaration, let's skip it
                    continue
                member['templated'] = is_template
                if is_template:
                    member['template_parameters'] = []
                member['abstract'] = item.is_abstract_record()
                member['final'] = False
                if not parent_is_namespace:
                    member['access'] = access_specifier_map[item.access_specifier]
                member['bases'] = []
                member['derived'] = []
                member['members'] = []
                member['related'] = []
                process_children = True
            elif member_type in ['method', 'conversionfunction', 'constructor', 'destructor']:
                member['templated'] = is_template
                if is_template:
                    member['template_parameters'] = []
                member['static'] = item.is_static_method()
                member['virtual'] = item.is_virtual_method()
                member['pure_virtual'] = item.is_pure_virtual_method()
                member['final'] = False
                member['override'] = False
                member['const'] = item.is_const_method()
                member['access'] = access_specifier_map[item.access_specifier]
                if is_template and member['name'] == status.members[semantic_parent]['name']:
                    # Templated member functions are of type 'functiontemplate',
                    # so Clang doesn't tell us if it's a constructor or not.
                    member_type = 'constructor'
                    # is_converting_constructor
                    # is_copy_constructor
                    # is_default_constructor
                    # is_move_constructor
                if member_type in ['conversionfunction', 'constructor']:
                    member['explicit'] = is_explicit(item)
                if member['name'] == 'operator=':
                    member_type = 'assignmentoperator'
                if member_type in ['assignmentoperator', 'constructor', 'destructor']:
                    v = get_defaulted_or_deleted(item)
                    member['defaulted'] = v == 'default'
                    member['deleted'] = v == 'delete'
                    if member['defaulted'] != item.is_default_method():
                        log.debug("I and Clang don't agree on the %s::%s method being defaulted" +
                                  " (I think it is %sdefaulted)\n   in file %s",
                                  status.members[semantic_parent]['name'], member['name'],
                                  '' if member['defaulted'] else 'not ', status.current_header_name)
                member['method_type'] = member_type
                process_function_declaration(item, member)
                if member_type in ['conversionfunction', 'constructor', 'destructor']:
                    member['return_type'] = {}
                member_type = 'function'  # write out as function
            elif member_type == 'enumvalue':
                member['value'] = item.enum_value
                member['group'] = ''  # these should not be part of a group
            elif member_type == 'enum':
                member['scoped'] = item.is_scoped_enum()
                if not parent_is_namespace:
                    member['access'] = access_specifier_map[item.access_specifier]
                type = process_type(item.enum_type)['typename']
                member['type'] = type
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
                if is_template:
                    member['template_parameters'] = []
                process_function_declaration(item, member)
            elif member_type == 'namespace':
                member['inline'] = is_inline(item)
                member['members'] = []
                process_children = True
            elif member_type in ['typedef', 'using']:
                member['oldfashioned'] = member_type == 'typedef'
                member_type = 'alias'
                member['templated'] = is_template
                if is_template:
                    member['template_parameters'] = []
                if not parent_is_namespace:
                    member['access'] = access_specifier_map[item.access_specifier]
                member['type'] = process_type(item.underlying_typedef_type, item)
                process_children = is_template
            elif member_type == 'union':
                if not item.is_definition():
                    # This is a forward declaration, let's skip it
                    continue
                member['templated'] = is_template
                if is_template:
                    member['template_parameters'] = []
                if not parent_is_namespace:
                    member['access'] = access_specifier_map[item.access_specifier]
                member['members'] = []
                member['related'] = []
                process_children = True
            elif member_type == 'variable':
                member['type'] = process_type(item.type, item)
                member['static'] = item.storage_class == cindex.StorageClass.STATIC
                member['constexpr'] = is_constexpr(item)
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

            # Deal with IDs -- we do this at the end of the above so we can use all that data to generate our ID.
            usr = item.get_usr()
            if usr in status.member_ids:
                id = status.member_ids[usr]
                log.debug("Member %s (%s) already exists, merging.", id, usr)
                member['id'] = id
                cleanup_qualifiers(member)
                merge_member(status.members[id], member)
            else:
                id = unique_id.member(member, status)
                log.debug("Member %s (%s) is new, adding.", id, usr)
                member['id'] = id
                status.member_ids[usr] = id
                if id in status.members:
                    log.error("USR for member %s was unknown, but ID %s was already there! This means that " +
                              "there is a name clash, unique_id.member is not good enough.\n   in file %s",
                              member['name'], id, status.current_header_name)
                    continue  # skip the rest of this function, we're in trouble here...
                cleanup_qualifiers(member)
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

def extract_includes(tu, status: Status, header_files, include_dirs):
    # Gets the list of files directly included by this one (not the ones included
    # by files included here).
    # include_dirs[0] is always the project's root dir
    this_file_includes = status.current_header['includes']
    it = tu.get_includes()
    for f in it:
        if f.depth == 1:
            include = os.path.realpath(f.include.name)
            include_name, is_under_project = is_under_directory(include, include_dirs[0])
            if is_under_project:
                if include in header_files:
                    this_file_includes.append('"[{}](#{})"'.format(include_name, unique_id.header(include_name)))
                else:
                    this_file_includes.append('"{}"'.format(include_name))
            else:
                full_include = include
                for dir in include_dirs[1:]:
                    part, res = is_under_directory(full_include, dir)
                    if res and len(part) < len(include):
                        include = part
                if os.path.isabs(include):
                    log.warning("Included file %s not in any of the directories on the path\n   in file %s",
                                include, status.current_header_name)
                this_file_includes.append('<{}>'.format(include))


# --- Main function for this file ---

def buildtree(root_dir, header_files, markdown_files, compiler_flags, include_dirs, options):
    """
    Builds the member tree as well as the headers, groups and pages lists, which together represent all
    the information about the code in the C++ project that is needed to produce useful documentation for
    the project.

    :param root_dir: The root directory for the header files, that you would pass to the compiler with `-I`
           when using the library (string)
    :param header_files: header files (with wildcards and path relative to working directory), space separated (string)
    :param markdown_files: Markdown files (with wildcards and path relative to working directory), space
           separated (string)
    :param compiler_flags: flags to pass to the compiler (string)
    :param include_dirs: include directories to pass to the compiler (string)
    :param options: dictionary with options for how to process things

    Options must contain the keys:
    - 'code_formatting': 'yes' or 'no', indicating whether to use "`<name>`" or "<name>" when writing the name of
        members. The `` is Markdown for code formatting. This applies to the \ref command only, since formatting of
        member names elsewhere is done by the backend, not this function. If a member name is not preceded by \ref,
        this tool will not recognize it as such. Instead, manually add `` around member names if not referenced.
    - 'tab_size': integer value for how many spaces each tab character advances.
    """

    # Set global "constants" according to options
    global code_formatting, tab_size
    code_formatting = options['code_formatting']
    tab_size = options['tab_size']

    # Process the input parameters
    root_dir = os.path.realpath(root_dir)
    header_files = [os.path.realpath(x) for x in expand_sources(shlex.split(header_files))]
    markdown_files = [os.path.realpath(x) for x in expand_sources(shlex.split(markdown_files))]
    compiler_flags = compiler_flags.split()
    include_dirs = [os.path.realpath(x) for x in shlex.split(include_dirs, posix=False)]

    # Get system include directories and figure out compiler flags
    include_dirs = [root_dir] + libclang.get_system_includes(compiler_flags) + include_dirs
    compiler_flags += ['-I{0}'.format(x) for x in include_dirs]
    compiler_flags.insert(0, '-xc++')
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
    for f in header_files:
        # Skip file if already processed
        if f in processed:
            continue

        # Get the name we'd use in an #include statement
        status.current_header_name = os.path.relpath(f, start=root_dir)
        log.info('Processing %s', status.current_header_name)
        status.current_file_name = f

        # Reset the rest of the data
        status.current_group = ['']
        status.group_locations = []
        status.current_member_group = ''
        status.member_group_locations = []

        # Add info for current file
        file_id = unique_id.header(status.current_header_name)
        status.current_header = members.new_header(file_id, status.current_header_name)
        status.data['headers'].append(status.current_header)
        status.headers[file_id] = status.current_header

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
        extract_includes(tu, status, header_files, include_dirs)

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
    status.current_header = {}
    status.current_file_name = ''
    processed = {}
    for f in markdown_files:
        # Skip file if already processed
        if f in processed:
            continue
        log.info('Processing %s', f)

        # Record file name in `current_include_name` for use in error messages
        status.current_header_name = f

        # Reset the parts of status that we use
        status.current_group = ['']
        status.group_locations = []
        status.current_member_group = ''
        status.member_group_locations = []

        # Extract markdown blocks from file
        extract_markdown(f, status)

        # Mark file as complete
        processed[f] = True

    # TODO: Verify that we don't have duplicate IDs. Within members and headers we're sure that they're
    #       unique, but groups, pages, (sub-)sections and anchors could all have IDs that clash among
    #       each other or with member or header IDs.

    # Go through all members with a 'type' element, and add an 'id' member representing the type
    post_process_types(status.members)

    # Go through all classes with base classes, and add references from base to derived, as well
    # as links back and forth between overridden functions
    post_process_inheritance(status.members)

    # Go through all members and resolve the `\relates` commands
    post_process_relates(status.members)

    # Go through all members, headers, groups and pages, identify `\ref` and `\see` commands,
    # identify linked members, and replace with links
    post_process_links(status.members, status)
    post_process_links(status.headers, status)
    post_process_links(status.groups, status)
    post_process_links(status.pages, status)

    # Go through all pages, identify `\subpage` commands, identify linked members, establish hierarchy,
    # and replace with links
    post_process_subpages(status.pages)

    return status.data

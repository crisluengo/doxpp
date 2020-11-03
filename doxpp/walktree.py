# dox++
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

import re
import json

from . import log


# --- find_member ---

split_function_arg_parts = re.compile(r'[a-zA-Z0-9_:]+|\*|&+|\[]')  # Split qualifiers
split_function_args = re.compile(r'^([a-zA-Z0-9_:]+)\((.*)\)$')     # Split function from arguments

def parse_function_arguments(arg_list):
    arguments = []
    for arg in arg_list:
        parts = split_function_arg_parts.findall(arg)
        if len(parts) > 1 and parts[0] == 'const':
            parts[0], parts[1] = parts[1], parts[0]  # Move the 'const' to after the type
        arguments.append({
            'typename': parts[0],
            'qualifiers': parts[1:]
        })
    return arguments

def same_argument(arg1, arg2):
    return arg1['typename'] == arg2['typename'] and arg1['qualifiers'] == arg2['qualifiers']

def find_member_inner(base, names, function_params):
    for member in base:
        if member['name'] == names[0]:
            if len(names) == 1:
                # We've matched the whole name
                if function_params:
                    # We need to match function parameters too
                    if member['member_type'] == 'function':
                        args = member['arguments']
                        if len(args) == len(function_params) and \
                                all([same_argument(arg1, arg2) for arg1, arg2 in zip(args, function_params)]):
                            return member['id']
                else:
                    # No need to match function parameters
                    return member['id']
            elif 'members' in member:
                return find_member_inner(member['members'], names[1:], function_params)
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
    name = name.strip()
    if not name:
        return ''
    function_params = []
    if '(' in name:
        match = split_function_args.fullmatch(name)
        if not match:
            log.error('Cannot parse "%s"', name)
            return ''
        name = match[1]
        function_params = parse_function_arguments(match[2].split(','))
    names = name.split('::')
    if not names:
        return ''
    if not 'members' in members[start_id]:
        start_id = members['parent']
    while True:
        base = members[start_id]['members']
        id = find_member_inner(base, names, function_params)
        if id:
            return id
        if 'parent' not in members[start_id]:
            return ''
        start_id = members['parent']


# --- create_member_dict ---

def create_member_dict_recursive(members, output):
    for member in members:
        output[member['id']] = member
        if 'members' in member:
            create_member_dict_recursive(member['members'], output)

def create_member_dict(members):
    """
    Creates a dictionary that maps member IDs to the member data.
    :param members: hierarchical member data read in from the JSON file.
    :return: dictionary.
    """
    output = {}
    output[''] = {
        'id': '',
        'members': members
        # TODO: add dictionary keys expected by code.
    }
    create_member_dict_recursive(members, output)
    return output

# --- load_data_from_json_file ---

def load_data_from_json_file(filename):
    """
    Loads data from JSON file created by the `dox++parse` tool
    :param filename: name of JSON file to read data from
    :return: dictionary with data as described in `json_output.md`
    """
    with open(filename, 'r') as input_file:
        return json.loads(input_file.read())

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

import os
import json

from . import log


# --- get_prefix ---

def get_prefix(id, members, key='name'):
    """
    Creates a list with the names of parents of member `id`. List excludes the name of `id` itself.
    :param id: string.
    :param members: dictionary created by `create_member_dict` or `create_element_dict`.
    :param key: dictionary key to record, typically 'name' for members or groups, 'title' for pages.
    :return: list of strings.
    """
    path_reverse = []
    id = members[id]['parent']
    while id:
        member = members[id]
        path_reverse.append(member[key])
        id = member['parent']
    return path_reverse[::-1]

# --- get_fully_qualified_name ---

def get_fully_qualified_name(id, members):
    """
    Creates a string with the fully qualified name of the member `id`.
    :param id: string.
    :param members: dictionary created by `create_member_dict`.
    :return: string.
    """
    names = get_prefix(id, members)
    names.append(members[id]['name'])
    return '::'.join(names)


# --- build_file_hierarchy ---

def split_path(head):
    out = []
    while head:
        head, tail = os.path.split(head)
        out.append(tail)
    out.reverse()
    return out

def assign_file_part_recursive(parts, file, out):
    if len(parts) == 1:
        out.append(file.copy())
        out[-1]['name'] = parts[0]
    else:
        if not out or parts[0] != out[-1]['name']:  # Because we're processing files in alphabetical order, it it's there it's always the last element of out
            out.append({'name': parts[0], 'children': []})
        assign_file_part_recursive(parts[1:], file, out[-1]['children'])

def move_directories_to_top(out):
    order = [i for i, x in enumerate(out) if 'children' in x] + [i for i, x in enumerate(out) if 'children' not in x]
    out[:] = [out[i] for i in order]
    for dir in out:
        if 'children' in dir:
            move_directories_to_top(dir['children'])
        else:
            break

def build_file_hierarchy(headers, directories_first=True):
    """
    Builds a file hierarchy.
    :param headers: data['headers'] list
    :param directories_first: Set to False to keep directories in alphabetical order among files
    :return: hierarchical list of dictionaries with directories and files
    out[ii]['name'] = file/directory name
    out[ii]['children'] = list of dictionaries with directories and files, if this is a directory
    out[ii][key] = value for key in corresponding data['headers'] element, if this is a file (i.e. copies over everything)
    """
    out = []
    for file in sorted(headers, key=lambda x: x['name']):
        if not file['page_id']:
            continue
        parts = split_path(file['name'])
        assign_file_part_recursive(parts, file, out)
    if directories_first:
        move_directories_to_top(out)
    return out


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

def create_element_dict(elements):
    """
    Creates a dictionary that maps IDs to the data. Can be used for headers,
    groups or pages. For members, use `create_member_dict`.
    :param elements: data read in from the JSON file.
    :return: dictionary.
    """
    output = {}
    for element in elements:
        output[element['id']] = element
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

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


# --- get_fully_qualified_name ---

def get_fully_qualified_name(id, members):
    """
    Creates a string with the fully qualified name of the member `id`.
    :param id: string.
    :param members: dictionary created by `create_member_dict`.
    :return: string.
    """
    output = ''
    while id:
        part = members[id]['name']
        if output:
            output = part + '::' + output
        else:
            output = part
        id = members[id]['parent']
    return output


# --- populate_member_lists ---

def populate_member_lists_recursive(members, data):
    for member in members:
        data['headers']['members'].append(member['id'])
        data['groups']['members'].append(member['id'])
        if 'members' in member:
            populate_member_lists_recursive(member['members'], data)

def populate_member_lists(data):
    """
    Updates data['headers'] and data['groups'], such that each element in those lists
    contains a new key 'members'. These will list the member IDs (from data['members'])
    that belong in the element.
    :param data: data returned by load_data_from_json_file()
    """
    data['headers']['members'] = []
    data['groups']['members'] = []
    populate_member_lists_recursive(data['members'], data)


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

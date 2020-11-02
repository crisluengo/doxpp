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

import urllib.parse
import re

def header(name):
    return urllib.parse.quote(name, safe='')
    #return name.replace('/','__')

qualifier_map = {
    '*': 'P',     # Pointer
    '&': 'L',     # L-value reference
    '&&': 'R',    # R-value reference
    '[]': 'A',    # Array
    'const': 'C'  # Const
}

def type_from_string(string):
    # Assuming string is fully qualified type name, no qualifiers
    # (awkward distinction between "qualified" and "qualifiers"...)
    return re.sub('::', '-', string)
    # TODO: There's something more to do where, for templated types

def type(dict):
    qualifiers = ''.join([qualifier_map[x] for x in dict['qualifiers']])
    id = '-' + type_from_string(dict['typename']) + '-' + qualifiers
    return id

def member(dict, status):
    id = urllib.parse.quote(dict['name'], safe='')  # This ensures `operator<` doesn't produce an invalid URL or link ID.
    if dict['parent']:
        id = status.members[dict['parent']]['id'] + '-' + id
    if 'template_parameters' in dict:
        id += '-T'
        # TODO: do we need additionally to say something about template parameter types?
    member_type = dict['member_type']
    if member_type == 'function':
        for arg in dict['arguments']:
            id += type(arg)
    if 'const' in dict and dict['const']:
        id += '-C'
    return id

def macro(name):
    # TODO: do we need more than this?
    return "-macro-" + name

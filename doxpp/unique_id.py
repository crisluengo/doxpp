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

def header(name):
    return urllib.parse.quote(name, safe='')
    #return name.replace('/','__')

qualifier_map = {
    '*': 'P',
    '&': 'L',
    '&&': 'R',
    '[]': 'A',
    'const': 'C'
}

def type(dict):
    qualifiers = ''.join([qualifier_map[x] for x in dict['qualifiers']])
    id = '-' + dict['typename'] + '-' + qualifiers
    return id

def member(dict, status):
    id = dict['name']
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

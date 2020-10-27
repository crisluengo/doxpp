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

def basic(id, name='', brief='', doc=''):
    return {
        'id': id,
        'name': name,
        'brief': brief,
        'doc': doc
    }

def new_group(id, name='', brief='', doc='', parent=''):
    group = basic(id, name, brief, doc)
    group.update({
        'parent': parent,
        'subgroups': []
    })
    return group

def new_header(id, name='', brief='', doc=''):
    header = basic(id, name, brief, doc)
    header.update({
        'includes': []
    })
    return header

def new_member(id, name='', member_type='', parent='', file=''):
    member = basic(id, name)
    member.update({
        'member_type': member_type,
        'parent': parent,       # ID of the parent member, empty string if declared in global namespace
        'file': file,           # ID of the first file this member was encountered
        'group': '',            # ID of the group it is in, if any
        'members': {},          # member structs for the things declared inside this member
        'deprecated': False     # Set to True if marked 'deprecated'
    })
    return member
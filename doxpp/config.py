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

import configparser


def generate(filename):
    config = configparser.ConfigParser()
    config['clang'] = {
        'compiler flags': '',         # could be '-std=c++11', for example
        'include directories': '',    # make these space-separated
    }
    config['log'] = {
        'level': 'warning',           # 'error', 'warning', 'info' or 'debug'
    }
    config['input'] = {
        'root directory': '.',        # the include path recorded for header files will be relative to this
        'header files': '*.h *.hpp',  # do give a path here, relative to working directory, for example: '*.h lib/*.h'
        'markdown files': '*.md',     # additional files to read
        'tab size': '4'               # size of a TAB character
    }
    config['json'] = {
        'filename': 'dox++out.json',
        'use typewriter font': 'no',  # 'yes' or 'no', the Markdown output uses backticks (code formatting) around type names
        'formatting': 'compact'       # 'compact' or 'readable'
    }
    with open(filename, 'w') as configfile:
        configfile.write('# Default dox++ configuration file\n\n')
        config.write(configfile)


def read(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    if not 'clang' in config:
        config['clang'] = {}
    if not 'log' in config:
        config['log'] = {}
    if not 'input' in config:
        config['input'] = {}
    if not 'json' in config:
        config['json'] = {}
    return config

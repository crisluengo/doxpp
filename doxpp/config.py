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


default_config_values = {
    'clang': {
        'compiler flags': '',         # could be '-std=c++11', for example
        'include directories': '',    # make these space-separated
    },
    'log': {
        'level': 'warning',           # 'error', 'warning', 'info' or 'debug'
    },
    'input': {
        'root directory': '.',        # the include path recorded for header files will be relative to this
        'header files': '*.h *.hpp',  # do give a path here, relative to working directory, for example: '*.h lib/*.h'
        'markdown files': '*.md',     # additional files to read
        'tab size': '4'               # size of a TAB character
    },
    'json': {
        'filename': 'dox++out.json',
        'use typewriter font': 'no',  # 'yes' or 'no', the Markdown output uses backticks (code formatting) around type names
        'formatting': 'compact'       # 'compact' or 'readable'
    },
    'project': {
        'name': 'Project Name',
        'brief': 'Short project description',
        'url': '',
        'logo': ''
    },
    'html': {
        'output directory' : 'html',  # relative path to where the HTML output is generated
        'document private members': 'yes',
        'document protected members': 'yes',
        'document undocumented members': 'no',
        'modify include statement': 'def modify_include_statement(id): return id',
        'theme color': '#22272e',
        'favicon': '',                # favicon to use instead of the default one
        'stylesheets': '',            # style sheets to use instead of the default ones (separate multiple files with spaces)
        'templates': '',              # relative path to templates to use instead of the default ones
        'extra files': '',            # additional files to copy to output directory (separate multiple files with spaces)
        'html header': '',            # HTML code to add to the <head> section of each HTML page
        'page header': '',            # HTML code to add to the top of each page
        'fine print': '[default]'     # text to use at the bottom of each page, leave empty for no footer
    }
}


def generate(filename: str):
    config = configparser.ConfigParser()
    config['clang'] = default_config_values['clang']
    config['log'] = default_config_values['log']
    config['input'] = default_config_values['input']
    config['json'] = default_config_values['json']
    config['project'] = default_config_values['project']
    config['html'] = default_config_values['html']
    with open(filename, 'w') as configfile:
        configfile.write('# Default dox++ configuration file\n\n')
        config.write(configfile)


def read(filename: str):
    config = configparser.ConfigParser(interpolation=None)
    config.read(filename)
    if not 'clang' in config:
        config['clang'] = {}
    if not 'log' in config:
        config['log'] = {}
    if not 'input' in config:
        config['input'] = {}
    if not 'json' in config:
        config['json'] = {}
    if not 'project' in config:
        config['project'] = {}
    if not 'html' in config:
        config['html'] = {}
    return config


def get(config: configparser.ConfigParser, section: str, value: str):
    return config[section].get(value, fallback=default_config_values[section][value])

def get_boolean(config: configparser.ConfigParser, section: str, value: str):
    return config[section].getboolean(value, fallback=default_config_values[section][value])

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
        'compiler flags': '',
        'include directories': '',
    },
    'log': {
        'level': 'warning',           # 'error', 'warning', 'info' or 'debug'
    },
    'input': {
        'root directory': '.',
        'header files': '*.h *.hpp',
        'markdown files': '*.md',
        'tab size': '4'
    },
    'json': {
        'filename': 'dox++out.json',
        'use typewriter font': 'no',
        'formatting': 'compact'       # 'compact' or 'readable'
    },
    'project': {
        'name': 'Project Name',
        'brief': 'Short project description',
        'version': '',
        'url': '',
        'download': '',
        'logo': ''
    },
    'html': {
        'output directory' : 'html',
        'document private virtual members': 'yes',
        'document private non-virtual members': 'yes',
        'document protected members': 'yes',
        'document undocumented members': 'no',
        'modify include statement': 'def modify_include_statement(id): return id',
        'theme color': '#cb4b16',
        'favicon': '',
        'stylesheets': '',
        'templates': '',
        'documentation link class': 'm-doc',
        'extra files': '',
        'html header': '',
        'page header': '',
        'fine print': '[default]',
        'navigation bar 1': "[('', '#pages', []),('', '#modules', []),('', '#namespaces', [])]",
        'navigation bar 2': "[('', '#classes', []),('', '#files', [])]",
        'file index expand levels': '1',
        'class index expand levels': '1',
        'class index expand inner': 'no',
    },
    'math': {
        'cache file': 'math_cache'
    },
    'search': {
        'enable': 'yes',
        'download binary': 'no',
        'base URL': '',
        'external URL': '',
        'add snake case suffixes': 'yes',
        'add camel case suffixes': 'yes'
    }
}


def generate(filename: str):
    config = configparser.ConfigParser()
    for key in default_config_values.keys():
        config[key] = default_config_values[key]
    with open(filename, 'w') as configfile:
        configfile.write('# Default dox++ configuration file\n\n')
        config.write(configfile)


def read(filename: str):
    config = configparser.ConfigParser(interpolation=None)
    config.read(filename)
    for key in default_config_values.keys():
        if not key in config:
            config[key] = {}
    return config


def get(config: configparser.ConfigParser, section: str, value: str):
    return config[section].get(value, fallback=default_config_values[section][value])

def get_boolean(config: configparser.ConfigParser, section: str, value: str):
    return True if config[section].get(value, fallback=default_config_values[section][value]) == 'yes' else False

def get_int(config: configparser.ConfigParser, section: str, value: str):
    return int(config[section].get(value, fallback=default_config_values[section][value]))

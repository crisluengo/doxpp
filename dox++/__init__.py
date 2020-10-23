# Copyright 2013-2018, Jesse van den Kieboom
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

import argparse, configparser
from . import log
from . import buildtree
import json

def generate_config_file(filename):
    config = configparser.ConfigParser()
    config['input'] = {
        'root directory': '.',        # the include path recorded for header files will be relative to this
        'header files': '*.h *.hpp',  # do give a path here, relative to working directory, for example: '*.h lib/*.h'
        'markdown files': '*.md'      # additional files to read
    }
    config['output'] = {
        'filename': 'dox++out.json',
        'log level': 'warning'      # 'error', 'warning', 'info' or 'debug'
    }
    config['clang'] = {
        'compiler flags': '',       # could be '-std:c++11', for example
        'include directories': '',  # make these space-separated
    }
    with open(filename, 'w') as configfile:
        configfile.write('# Default dox++ configuration file')
        config.write(configfile)

def run():
    parser = argparse.ArgumentParser(description='Clang based documentation generator.', usage='%(prog)s [options] [config file]')
    parser.add_argument('-g', default=False, action='generate', const=True, help='generate a default configuration file')
    parser.add_argument('config_file', nargs=1, default='dox++config', help='name of the configuration file')
    args = parser.parse_args()

    # Generate configuration file if requested, then quit
    if args.generate:
        generate_config_file(args.config_file)
        return

    # Read configuration file, ensure all sections are present
    config = configparser.ConfigParser()
    config.read(args.config_file)
    if not 'input' in config:
        config['input'] = {}
    if not 'output' in config:
        config['output'] = {}
    if not 'clang' in config:
        config['clang'] = {}

    log.setLevel(config['output'].get('log level', 'warning'))  # the default value

    data = buildtree.buildtree(
        config['input'].get('root directory', ''),
        config['input'].get('header files', ''),
        config['input'].get('markdown files', ''),
        config['clang'].get('compiler flags', ''),
        config['clang'].get('include directories', '')
    )

    filename = config['output'].get('filename', 'dox++out.json')
    with open(filename, 'w') as outputfile:
        outputfile.write(json.dumps(data))

if __name__ == '__main__':
    run()

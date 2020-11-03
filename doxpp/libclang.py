# dox++
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

import os
import platform
import subprocess

from . import log
from .clang import cindex


def get_system_includes(f):
    devnull = open(os.devnull)

    try:
        p = subprocess.Popen(['clang++', '-E', '-xc++'] + f + ['-v', '-'],
                             stdin=devnull,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except OSError as e:
        log.error("Fatal: Failed to run clang++ to obtain system include headers, please install clang++ to use dox++")
        message = str(e)
        if message:
            log.error("  Error message: %s", message)
        exit(1)

    devnull.close()

    lines = p.communicate()[1].splitlines()
    init = False
    paths = []

    for line in lines:
        line = line.decode('UTF-8')
        if line.startswith('#include <...>'):
            init = True
        elif line.startswith('End of search list.'):
            init = False
        elif init:
            p = line.strip()
            suffix = ' (framework directory)'
            if p.endswith(suffix):
                p = p[:-len(suffix)]
            paths.append(os.path.realpath(p))
            
    return paths

def load_libclang():
    from ctypes.util import find_library

    if platform.system() == 'Darwin':
        libclangs = [
            '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/libclang.dylib',
            '/Library/Developer/CommandLineTools/usr/lib/libclang.dylib'
        ]
        found = False
        for libclang in libclangs:
            if os.path.exists(libclang):
                cindex.Config.set_library_path(os.path.dirname(libclang))
                found = True
                break
        if not found:
            lname = find_library("clang")
            if not lname is None:
                cindex.Config.set_library_file(lname)
    else:
        versions = [None, '7.0', '6.0', '5.0', '4.0', '3.9', '3.8', '3.7', '3.6', '3.5', '3.4', '3.3', '3.2']
        for v in versions:
            name = 'clang'
            if not v is None:
                name += '-' + v
            lname = find_library(name)
            if not lname is None:
                cindex.Config.set_library_file(lname)
                break

    testconf = cindex.Config()
    try:
        testconf.get_cindex_library()
    except cindex.LibclangError as e:
        log.error("Fatal: Failed to locate libclang library.\ndox++ depends on libclang for parsing sources, please make sure you have libclang installed.")
        log.error(str(e))
        exit(1)

    return cindex

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

import logging
import sys

if sys.stderr.isatty():
    logging.addLevelName( logging.WARNING, "\033[33m%s\033[0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName( logging.ERROR, "\033[31m%s\033[0m" % logging.getLevelName(logging.ERROR))
    formatter = logging.Formatter('\033[1m[%(levelname)s]\033[0m: %(message)s')
else:
    formatter = logging.Formatter('[%(levelname)s]: %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)

levels = {
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'info': logging.INFO,
    'debug': logging.DEBUG
}

def setLevel(level):
    if level in levels:
        logger.setLevel(levels[level])

def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)

setLevel(logging.ERROR)
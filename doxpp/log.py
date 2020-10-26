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

logger = logging.getLogger()

handler = logging.StreamHandler()
formatter = logging.Formatter('\033[1m[%(levelname)s]\033[0m: %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)

WARNING = logging.WARNING
ERROR = logging.ERROR
DEBUG = logging.DEBUG
INFO = logging.INFO

levels = {
    'warning': WARNING,
    'error': ERROR,
    'info': INFO,
    'debug': DEBUG
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

setLevel(ERROR)
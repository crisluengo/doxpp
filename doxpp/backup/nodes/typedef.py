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

from .node import Node
from .ctype import Type

from ..clang import cindex

class Typedef(Node):
    kind = cindex.CursorKind.TYPEDEF_DECL

    def __init__(self, cursor, comment):
        Node.__init__(self, cursor, comment)

        children = [child for child in cursor.get_children()]

        if len(children) == 1 and children[0].kind == cindex.CursorKind.TYPE_REF:
            tcursor = children[0]
            self.type = Type(tcursor.type, tcursor)
        else:
            self.process_children = True
            self.type = Type(self.cursor.type.get_canonical(), cursor=self.cursor)
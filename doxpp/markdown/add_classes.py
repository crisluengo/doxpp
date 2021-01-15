# dox++
# Copyright 2021, Cris Luengo
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

# Add classes to dox++ documentation
# The m.css style sheets expects <img> tags to have the class "m-image"
# and the <table> tags to have the class "m-table".

import markdown


class AddClassesTreeprocessor(markdown.treeprocessors.Treeprocessor):

    def run(self, doc):
        for elem in doc.iter(tag='img'):
            c = elem.get('class', '')
            if c:
                c += ' '
            c += 'm-image'
            elem.set('class', c)
        for elem in doc.iter(tag='table'):
            c = elem.get('class', '')
            if c:
                c += ' '
            c += 'm-table'
            elem.set('class', c)


class AddClassesExtension(markdown.extensions.Extension):

    def extendMarkdown(self, md):
        add_classes = AddClassesTreeprocessor(md)
        md.treeprocessors.register(add_classes, 'add_classes', 1) # Lowest possible priority -- do this at the end of all other processing
        md.registerExtension(self)

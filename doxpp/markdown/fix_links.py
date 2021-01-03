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

# Fixing links in dox++ generated documentation
# Looks for <a href="#id"> and replaces it with <a href="page_id.html#id">
# (or with <a href="page_id.html"> if page_id==id).

import markdown


class FixLinksTreeprocessor(markdown.treeprocessors.Treeprocessor):

    id_map = None

    def run(self, doc):
        for elem in doc.iter(tag='a'):
            id = elem.get('href', None)
            #print("Found anchor with link =", id)
            if id and id[0] == '#':
                id = id[1:]
                if id in self.id_map:
                    page_id = self.id_map[id]
                    link = page_id + '.html'
                    if page_id != id:
                        link += '#' + id
                    elem.set("href", link)
                    #print("    Replaced with link =", link)



class FixLinksExtension(markdown.extensions.Extension):

    def __init__(self, id_map):
        self.id_map = id_map

    def extendMarkdown(self, md):
        fix_links = FixLinksTreeprocessor(md)
        fix_links.id_map = self.id_map
        md.treeprocessors.register(fix_links, 'fix_links', 1) # Lowest possible priority -- do this at the end of all other processing
        md.registerExtension(self)

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

# Recording linked images in dox++ generated documentation
# Looks for <img src="filename"> and stores the filename in a set().

import markdown
import os
import urllib


class RecordLinkedImagesTreeprocessor(markdown.treeprocessors.Treeprocessor):

    images = None

    def run(self, doc):
        for elem in doc.iter(tag='img'):
            fname = elem.get('src', None)
            if fname and not urllib.parse.urlparse(fname).netloc:
                self.images.add(os.path.basename(fname))


class RecordLinkedImagesExtension(markdown.extensions.Extension):

    def __init__(self, images):
        self.images = images

    def extendMarkdown(self, md):
        record_images = RecordLinkedImagesTreeprocessor(md)
        record_images.images = self.images
        md.treeprocessors.register(record_images, 'record_images', 1) # Lowest possible priority -- do this at the end of all other processing
        md.registerExtension(self)

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

import markdown

from . import log
from . import walktree

extensions = ['attr_list',      # https://python-markdown.github.io/extensions/attr_list/
              'md_in_html',     # https://python-markdown.github.io/extensions/md_in_html/
              'tables',         # https://python-markdown.github.io/extensions/tables/
              'fenced_code',    # https://python-markdown.github.io/extensions/fenced_code_blocks/
              'admonition',     # https://python-markdown.github.io/extensions/admonition/
              'codehilite',     # https://python-markdown.github.io/extensions/code_hilite/
              'sane_lists',     # https://python-markdown.github.io/extensions/sane_lists/
              'smarty'          # https://python-markdown.github.io/extensions/smarty/
              ]
extension_configs = {
    'codehilite': {
        'css_class': 'codehilite'
    }
}
md = markdown.Markdown(extensions=extensions, extension_configs=extension_configs, output_format="html5")


class Status:
    # This defines the status of our generator
    def __init__(self, data):
        # Data read in from JSON file
        self.data = data

        # These dictionaries contain the same dictionaries as in 'data', but indexed by their ID so they're
        # easy to find. It is the *same* dictionaries, modifying these will modify 'data'.
        self.members = walktree.create_member_dict(data['members'])
        self.headers = walktree.create_element_dict(data['headers'])
        self.groups = walktree.create_element_dict(data['groups'])
        self.pages = walktree.create_element_dict(data['pages'])

        # This dictionary links each unique ID to a page where it can be found.
        # To link to an ID, link to "<page>.html#<ID>", unless page==ID, in which case
        # it suffices to link to "<page>.html".
        self.id_map = {}

        self.html_pages = set()


def assign_page(status: Status):
    # - If it is a class/struct member, it goes in the class/struct page
    # - If it has a group name, it goes in the group page
    # - If it is in a namespace, it goes in the namespace page
    # - Otherwise it goes in the header page
    for member in status.members.values():
        if not member['id']:
            # This is the "root" member
            continue
        if member['member_type'] == 'enumvalue':
            # These are added to the page that their parent is in. Because of the way we generate the members list,
            # the parent has already been processed
            html_page = status.id_map[member['parent']]
        elif member['member_type'] in ['class', 'struct', 'namespace']:
            # class, struct and namespace go in their own page
            html_page = member['id']
        elif member['parent'] and status.members[member['parent']]['member_type'] in ['class', 'struct']:
            # class or struct members go in the class/struct page
            html_page = member['parent']
        elif member['group']:
            # otherwise, if group member, go in the group page
            html_page = member['group']
        elif member['parent']:
            # otherwise, if namespace member, go in the namespace page
            html_page = member['parent']
        else:
            # otherwise, go in the header page
            html_page = member['header']
        print(member['id'], html_page)
        status.id_map[member['id']] = html_page
        status.html_pages.add(html_page)


def createhtml(input_file, output_dir, options):
    """
    Generates HTML pages for the documentation in the JSON file `input_file`.

    :param input_file: the name of the JSON file that contains the documentation to format (string)
    :param output_dir: directory where the HTML files will be written (string)
    :param options: dictionary with options for how to process things

    Options can contain the keys:
    - '':
    """

    # Load data
    status = Status(walktree.load_data_from_json_file(input_file))

    # Find out in which page the detailed documentation for each member has to go
    assign_page(status)
    print(status.html_pages)

    # Generate the pages
    # - For each element in `status.html_pages`:
    #   - Generate the index with brief documentation (parsed by Markdown)
    #   - Add the corresponding detailed documentation (parsed by Markdown)
    #   - Fix links to point to the right page
    # - For each element in `status.pages`:
    #   - Add documentation (parsed by Markdown)
    #   - Fix links to point to the right page

    # Generate indexes for pages, groups (==modules), namespaces/classes/structs (==classes), and headers

    # Generate search data

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

import os
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
        # Items not in here are not documented.
        self.id_map = {}

        # This dictionary links each page to the things that will be listed there (with or without
        # detailed documentation). Things can be listed on multiple pages.
        self.html_pages_index = {}

        # This dictionary links each page to the things that will be documented there (with or without
        # detailed documentation). Things are documented in only one page. This is the inverse of `id_map`.
        self.html_pages_detailed = {}


def list_item_on_page(item, page, status: Status):
    if page not in status.html_pages_index:
        status.html_pages_index[page] = set()
    status.html_pages_index[page].add(item)


def document_item_on_page(item, page, status: Status):
    status.id_map[item] = page
    if page not in status.html_pages_detailed:
        status.html_pages_detailed[page] = set()
    status.html_pages_detailed[page].add(item)
    list_item_on_page(item, page, status)

def show_member(member, show_private, show_undocumented):
    if not (show_undocumented or member['brief']):
        return False
    if not (show_private or ('access' in member and member['access'] == 'private')):
        return False
    return True

def assign_page(status: Status, show_private, show_undocumented):
    # All header files and groups will have a page, whether they're documented or not
    for header in status.headers.values():
        html_page = header['id']
        status.id_map[html_page] = html_page
        status.html_pages_index[html_page] = set()
    for group in status.groups.values():
        html_page = group['id']
        status.id_map[html_page] = html_page
        status.html_pages_index[html_page] = set()
        for child in group['subgroups']:
            # Subgroups listed in parent group's page
            list_item_on_page(child, html_page, status)
    # Assign members to a specific page
    for member in status.members.values():
        id = member['id']
        if not id:
            # This is the "root" member
            continue
        if member['member_type'] == 'enumvalue':
            # These are added to the page that their parent is in. Because of the way we generate the members list,
            # the parent has already been processed. This is shown in the documentation even if not documented,
            # as long as the parent is.
            if show_member(status.members[member['parent']], show_private, show_undocumented):
                document_item_on_page(id, status.id_map[member['parent']], status)
            continue
        if not show_member(member, show_private, show_undocumented):
            # Undocumented or private, ignore
            continue
        if member['member_type'] in ['class', 'struct', 'union', 'namespace']:
            # Class, struct, union and namespace go in their own page
            document_item_on_page(id, id, status)
        elif member['parent'] and status.members[member['parent']]['member_type'] in ['class', 'struct', 'union']:
            # Class or struct members go in the class/struct/union page
            document_item_on_page(id, member['parent'], status)
            # Don't list anywhere else
            continue
        elif member['group']:
            # Otherwise, if group member, go in the group page
            document_item_on_page(id, member['group'], status)
        elif member['parent']:
            # Otherwise, if namespace member, go in the namespace page
            document_item_on_page(id, member['parent'], status)
        else:
            # Otherwise, go in the header page
            document_item_on_page(id, member['header'], status)
        # Additionally, they're listed in the group page, the namespace page and the header page
        list_item_on_page(id, member['header'], status)
        if member['group']:
            list_item_on_page(id, member['group'], status)
        if member['parent'] and status.members[member['parent']]['member_type'] == 'namespace':
            list_item_on_page(id, member['parent'], status)


def generate_member_page(page, status: Status):
    # Generate the index with brief documentation (parsed by Markdown)
    # Add the corresponding detailed documentation (parsed by Markdown)
    # TODO
    return ''


def generate_page_page(page, status: Status):
    # Add documentation (parsed by Markdown)
    # TODO
    return ''


def fix_links(html, status: Status):
    # Fix links in HTML document to point to the right page
    # TODO
    return html


def createhtml(input_file, output_dir, options):
    """
    Generates HTML pages for the documentation in the JSON file `input_file`.

    :param input_file: the name of the JSON file that contains the documentation to format (string)
    :param output_dir: directory where the HTML files will be written (string)
    :param options: dictionary with options for how to process things

    Options must contain the keys:
    - 'show_private': include private members in the documentation
    - 'show_undocumented': include undocumented members in the documentation
    Options should also contain keys used in the HTML templates.
    """

    # Load data
    status = Status(walktree.load_data_from_json_file(input_file))

    # Find out which pages to create, what is listed in each, and in which page
    # the detailed documentation for each member has to go
    assign_page(status, options['show_private'], options['show_undocumented'])
    #print('\n\nhtml_pages_index', status.html_pages_index)
    #print('\n\nhtml_pages_detailed', status.html_pages_detailed)
    #print('\n\nid_map', status.id_map)

    # Generate the pages
    for page in status.html_pages_index.keys():
        html = generate_member_page(page, status)
        html = fix_links(html, status)
        with open(os.path.join(output_dir, page + '.html'), 'w') as file:
            file.write(html)
    for page in status.pages.values():
        html = generate_page_page(page, status)
        html = fix_links(html, status)
        with open(os.path.join(output_dir, page['id'] + '.html'), 'w') as file:
            file.write(html)
    if 'index' not in status.pages:
        # TODO: create an index
        pass

    # Generate indexes for pages, groups (==modules), namespaces/classes/structs (==classes), and headers (==files)
    # TODO

    # Generate search data
    # TODO

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

        # This dictionary links each page to the members that will be listed there (with or without
        # detailed documentation). Members can be listed on multiple pages.
        self.html_pages_index = {}

        # This dictionary links each page to the members that will be documented there (with or without
        # detailed documentation). Members are documented in only one page. This is the inverse of `id_map`,
        # except that it contains only members.
        self.html_pages_detailed = {}


def register_anchors_to_page(compound, page_id, status: Status):
    for anchor in compound['anchors']:
        status.id_map[anchor] = page_id

def list_member_on_page(member_id, page_id, status: Status):
    if page_id not in status.html_pages_index:
        status.html_pages_index[page_id] = set()
    status.html_pages_index[page_id].add(member_id)

def document_member_on_page(member, page_id, status: Status):
    member['page_id'] = page_id
    member_id = member['id']
    status.id_map[member_id] = page_id
    if page_id not in status.html_pages_detailed:
        status.html_pages_detailed[page_id] = set()
    status.html_pages_detailed[page_id].add(member_id)
    list_member_on_page(member_id, page_id, status)
    register_anchors_to_page(member, page_id, status)

def create_page(compound, status: Status):
    page_id = compound['id']
    compound['page_id'] = page_id
    status.id_map[page_id] = page_id
    if page_id not in status.html_pages_index:
        status.html_pages_index[page_id] = set()
    register_anchors_to_page(compound, page_id, status)

def show_member(member, show_private, show_undocumented):
    if not (show_undocumented or member['brief']):
        return False
    if not (show_private or ('access' in member and member['access'] == 'private')):
        return False
    return True

def assign_page(status: Status, show_private, show_undocumented):
    # All header files and groups will have a page, whether they're documented or not
    for header in status.headers.values():
        create_page(header, status)
    for group in status.groups.values():
        create_page(group, status)
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
                document_member_on_page(member, status.id_map[member['parent']], status)
            continue
        if not show_member(member, show_private, show_undocumented):
            # Undocumented or private, ignore
            continue
        if member['member_type'] in ['class', 'struct', 'union', 'namespace']:
            # Class, struct, union and namespace go in their own page
            document_member_on_page(member, id, status)
        elif member['parent'] and status.members[member['parent']]['member_type'] in ['class', 'struct', 'union']:
            # Class or struct members go in the class/struct/union page
            document_member_on_page(member, member['parent'], status)
            # Don't list anywhere else
            continue
        elif member['relates']:
            document_member_on_page(member, member['relates'], status)
        elif member['group']:
            # Otherwise, if group member, go in the group page
            document_member_on_page(member, member['group'], status)
        elif member['parent']:
            # Otherwise, if namespace member, go in the namespace page
            document_member_on_page(member, member['parent'], status)
        else:
            # Otherwise, go in the header page
            document_member_on_page(member, member['header'], status)
        # Additionally, they're listed in the group page, the namespace page and the header page
        list_member_on_page(id, member['header'], status)
        if member['group']:
            list_member_on_page(id, member['group'], status)
        if member['parent'] and status.members[member['parent']]['member_type'] == 'namespace':
            list_member_on_page(id, member['parent'], status)
    # All pages have a page, obviously
    for page in status.pages.values():
        create_page(page, status)


def parse_markdown(status: Status):
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

    # TODO: Add these extensions:
    #       https://github.com/SaschaCowley/Markdown-Headdown
    #       https://github.com/jambonrose/markdown_superscript_extension
    #       https://github.com/jambonrose/markdown_subscript_extension

    # TODO: Create a LaTeX math extension based on some stuff in m.css as well as the following:
    #       https://github.com/justinvh/Markdown-LaTeX
    #       https://github.com/ShadowKyogre/python-asciimathml

    # TODO: Create an extension that fixes links of the form `#<member_id>` to `<page_id>.html#<member_id>`,
    #       where `page_id` is given by `status.id_map[member_id]`.

    for header in status.headers.values():
        if header['brief']:
            header['brief'] = md.reset().convert(header['brief'])
        if header['doc']:
            header['doc'] = md.reset().convert(header['doc'])
    for group in status.groups.values():
        if group['brief']:
            group['brief'] = md.reset().convert(group['brief'])
        if group['doc']:
            group['doc'] = md.reset().convert(group['doc'])
    for member in status.members.values():
        if member['id'] not in status.id_map:
            continue
        if member['brief']:
            member['brief'] = md.reset().convert(member['brief'])
        if member['doc']:
            member['doc'] = md.reset().convert(member['doc'])
    for page in status.pages.values():
        if page['doc']:
            page['doc'] = md.reset().convert(page['doc'])


def generate_member_page(page, status: Status):
    # TODO Jinja stuff here
    return ''


def generate_page_page(page, status: Status):
    # TODO Jinja stuff here
    return ''


def generate_default_index_page(status: Status):
    # TODO Jinja stuff here
    return ''


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

    # Parse all Markdown
    parse_markdown(status)

    # Generate the pages
    for page in status.html_pages_index.keys():
        html = generate_member_page(page, status)
        with open(os.path.join(output_dir, page + '.html'), 'w') as file:
            file.write(html)
    for page in status.pages.values():
        html = generate_page_page(page, status)
        with open(os.path.join(output_dir, page['id'] + '.html'), 'w') as file:
            file.write(html)
    if 'index' not in status.pages:
        html = generate_default_index_page(status)
        with open(os.path.join(output_dir, 'index.html'), 'w') as file:
            file.write(html)
        pass

    # Generate indexes for pages, groups (==modules), namespaces/classes/structs (==classes), and headers (==files)
    # TODO

    # Generate search data
    # TODO

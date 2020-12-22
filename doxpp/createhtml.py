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

# Some bits of code are taken from m.css:
#   Copyright 2017-2020 Vladimír Vondruš <mosra@centrum.cz>
#   Copyright 2020 Yuri Edward <nicolas1.fraysse@epitech.eu>
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included
#   in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#   THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

import os
import urllib.parse
import markdown
import jinja2

from . import log
from . import walktree
from . import members

from .search import CssClass, ResultFlag, ResultMap, Trie, serialize_search_data, base85encode_search_data, search_filename, searchdata_filename, searchdata_filename_b85, searchdata_format_version


doxpp_path = os.path.dirname(os.path.realpath(__file__))
default_templates = os.path.join(doxpp_path, 'html_templates')


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
        self.id_map = {
            'classes': 'classes',
            'files': 'files',
            'index': 'index',
            'modules': 'modules',
            'namespaces': 'namespaces',
            'pages': 'pages'
        }

        # This dictionary links each page to the members that will be listed there (with or without
        # detailed documentation). Members can be listed on multiple pages.
        self.html_pages_index = {}

        # This dictionary links each page to the members that will be documented there (with or without
        # detailed documentation). Members are documented in only one page. This is the inverse of `id_map`,
        # except that it contains only members.
        self.html_pages_detailed = {}

    def get_link(self, id):
        # Convert an ID into a URL to link to
        page = self.id_map[id]
        if page == id:
            return page + '.html'
        else:
            return page + '.html#' + id

    def find_title(self, id):
        standard = {
            'classes': 'Classes',
            'files': 'Files',
            'index': 'Home',
            'modules': 'Modules',
            'namespaces': 'Namespaces',
            'pages': 'Pages'
        }
        if id in standard:
            return standard[id]
        if id in self.members:
            return self.members[id]['name']
        if id in self.headers:
            return self.headers[id]['name']
        if id in self.groups:
            return self.groups[id]['name']
        if id in self.pages:
            return self.pages[id]['title']
        # TODO: how about links to (sub-)sections and anchors?
        return '(unknown)'

def register_anchors_to_page(compound, page_id, status: Status):
    for section in compound['sections']:
        status.id_map[section[0]] = page_id
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
    if 'access' in member and not (show_private or (member['access'] == 'private')):
        return False
    return True

def assign_page(status: Status, show_private, show_undocumented):
    # TODO: Add option `show_if_documented_children`
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



def create_indices(status: Status):
    index = {}
    index['symbols'] = []   # Used in classes and namespaces index
    index['files'] = []     # Used in files index
    index['modules'] = []   # Used in modules index
    index['pages'] = []     # used in pages index
    # Symbols (class, struct, union and namespace)
    for member in status.members.values():
        # TODO: for namespaces, we need to add a flag to indicate if there's child namespaces
        if not member['id']:
            continue
        if member['member_type'] not in ['namespace', 'class', 'struct', 'union']:
            continue
        member['children'] = []
        if 'page_id' not in member or not member['page_id']:
            continue
        if member['parent']:
            parent = status.members[member['parent']]
            parent['children'].append(member) # Parent has been processed earlier, has a 'children' key
            if member['member_type'] == 'namespace':
                parent['has_child_namespace'] = True
        else:
            index['symbols'].append(member)
    index['symbols'].sort(key=lambda x: x['name'])
    for member in status.members.values():
        if 'children' in member:
            member['children'].sort(key=lambda x: x['name'])
    # Files (headers)
    index['files'] = walktree.build_file_hierarchy(status.data['headers'])
    # Modules (groups)
    status.data['groups'].sort(key=lambda x: x['name'])
    for group in status.data['groups']:
        if not group['parent']:
            index['modules'].append(group)
        group['children'] = []
        for s in group['subgroups']:
            group['children'].append(status.groups[s])
    # Pages
    status.data['pages'].sort(key=lambda x: x['title'])
    for page in status.data['pages']:
        if page['id'] == 'index':
            continue  # the index is not on the list of pages
        if not page['parent']:
            index['pages'].append(page)
        page['children'] = []
        for s in page['subpages']:
            page['children'].append(status.pages[s])
    return index


def process_navbar_links(navbar, status: Status):
    # Convert (title, id, sub) into (title, link, id, sub)
    out = []
    for title, id, sub in navbar:
        if sub:
            sub = process_navbar_links(sub, status)
        link = status.get_link(id)
        if not title:
            title = status.find_title(id)
        out.append((title, link, id, sub))
    return out


def process_sections_recursive(sections, level):
    if sections[0][2] < level:
        return []
    section = sections.pop(0)
    subsections = []
    while sections and sections[0][2] > section[2]:
        subsections.append(process_sections_recursive(sections, level + 1))
    return (section[0], section[1], subsections)

def process_sections(compound):
    # compound['sections'] is a flat list of tuples [(name, title, level), ...]
    # we turn it into a hierarchical list according to level: [(name, title, [...]), ...]
    sections = compound['sections']
    compound['sections'] = []
    while sections:
        compound['sections'].append(process_sections_recursive(sections, 1))

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
        process_sections(header)
    for group in status.groups.values():
        if group['brief']:
            group['brief'] = md.reset().convert(group['brief'])
        if group['doc']:
            group['doc'] = md.reset().convert(group['doc'])
        process_sections(group)
    for member in status.members.values():
        if member['id'] not in status.id_map:
            continue
        if member['brief']:
            member['brief'] = md.reset().convert(member['brief'])
        if member['doc']:
            member['doc'] = md.reset().convert(member['doc'])
        process_sections(member)
    for page in status.pages.values():
        if page['doc']:
            page['doc'] = md.reset().convert(page['doc'])
        process_sections(page)


def generate_member_page(page, status: Status):
    # TODO Jinja stuff here
    return ''


def generate_page_page(page, status: Status):
    # TODO Jinja stuff here
    return ''


def createhtml(input_file, output_dir, options, template_params):
    """
    Generates HTML pages for the documentation in the JSON file `input_file`.

    :param input_file: the name of the JSON file that contains the documentation to format (string)
    :param output_dir: directory where the HTML files will be written (string)
    :param options: dictionary with options for how to process things
    :param template_params: dictionary with template parameters

    Options must contain the keys:
    - 'show_private': include private members in the documentation
    - 'show_undocumented': include undocumented members in the documentation
    - 'extra_files': list of extra files to copy to the output directory
    - 'templates': path to templates to use instead of default ones
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

    # Create tree structure for index pages
    index = create_indices(status)

    # Navbar links
    if 'LINKS_NAVBAR1' in template_params:
        template_params['LINKS_NAVBAR1'] = process_navbar_links(template_params['LINKS_NAVBAR1'], status)
    if 'LINKS_NAVBAR2' in template_params:
        template_params['LINKS_NAVBAR2'] = process_navbar_links(template_params['LINKS_NAVBAR2'], status)

    # If no stylesheets were given, use the default one
    if not 'STYLESHEETS' in template_params or not template_params['STYLESHEETS']:
        template_params['STYLESHEETS'] = ['m-light-documentation.compiled.css']

    # If custom template dir was supplied, use the default template directory
    # as a fallback
    template_paths = [options['templates']]
    if options['templates'] != default_templates:
        template_paths.append(default_templates)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_paths),
                             trim_blocks=True, lstrip_blocks=True, enable_async=True)

    # Filter to return file basename or the full URL, if absolute
    def basename_or_url(path):
        if urllib.parse.urlparse(path).netloc:
            return path
        return os.path.basename(path)
    def rtrim(value):
        return value.rstrip()
    env.filters['rtrim'] = rtrim
    env.filters['basename_or_url'] = basename_or_url
    env.filters['urljoin'] = urllib.parse.urljoin

    # Generate the html for the members
    for page in status.html_pages_index.keys():
        html = generate_member_page(page, status)
        with open(os.path.join(output_dir, page + '.html'), 'w') as f:
            f.write(html)

    # Generate the html for the pages
    if 'index' not in status.pages:
        page = members.new_page('index', options['PROJECT_NAME'], '')
        status.pages['index'] = page
    for page in status.pages.values():
        file = page['id'] + '.html'
        path_reverse = [page['id']]
        parent = page['parent']
        while parent:
            path_reverse.append(parent)
            parent = status.pages[parent]['parent']
        page['breadcrumb'] = []
        for elem in reversed(path_reverse):
            page['breadcrumb'].append((status.pages[elem]['title'], elem + '.html'))
        template = env.get_template('page.html')
        rendered = template.render(compound=page,
                               FILENAME=file,
                               SEARCHDATA_FORMAT_VERSION=searchdata_format_version,
                               **template_params)
        with open(os.path.join(output_dir, file), 'w') as f:
            f.write(rendered)

    # Generate indexes for pages, groups (==modules), namespaces, classes/structs (==classes), and headers (==files)
    for file in ['pages.html', 'modules.html', 'namespaces.html', 'classes.html', 'files.html']:
        template = env.get_template(file)
        rendered = template.render(index=index,
                                   FILENAME=file,
                                   SEARCHDATA_FORMAT_VERSION=searchdata_format_version,
                                   **template_params)
        with open(os.path.join(output_dir, file), 'w') as f:
            f.write(rendered)

    # Generate search data
    # TODO

    # Copy over all referenced files
    # TODO

# dox++
# Copyright 2020-2021, Cris Luengo
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
import re
import urllib.parse
import html
import mimetypes
import shutil
import enum
import glob
from types import SimpleNamespace as Empty

import markdown
import jinja2

from . import log
from . import walktree
from . import members

from .search import CssClass, ResultFlag, ResultMap, Trie, serialize_search_data, base85encode_search_data, search_filename, searchdata_filename, searchdata_filename_b85, searchdata_format_version

from .markdown.admonition import AdmonitionExtension
from .markdown.fix_links import FixLinksExtension
from .markdown.add_classes import AddClassesExtension
from .markdown.record_images import RecordLinkedImagesExtension
from .markdown.mdx_subscript import SubscriptExtension
from .markdown.mdx_superscript import SuperscriptExtension


doxpp_path = os.path.dirname(os.path.realpath(__file__))
default_templates = os.path.join(doxpp_path, 'html_templates')


class Status:
    # This defines the status of our generator
    def __init__(self, data, options):
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

        # This dictionary links page_id to the compound with the relevant information for that page.
        self.html_pages = {}

        # This is the set of images referenced in the documentation
        self.images = set()

        # Options
        self.show_private = options['show_private']
        self.show_protected = options['show_protected']
        self.show_undocumented = options['show_undocumented']
        self.modify_include_statement = options['modify_include_statement']

    def get_link(self, id):
        # Convert an ID into a URL to link to
        try:
            page = self.id_map[id]
        except KeyError:
            log.warning('Referencing type %s, which was excluded from documentation', id)  # TODO: this is normal, though...
            return None
        if page == id:
            return page + '.html'
        else:
            return page + '.html#' + id

    def find_title(self, id):
        # This is used only in process_navbar_links()
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

    def get_compound(self, id):
        if id in self.members:
            return self.members[id]
        elif id in self.headers:
            return self.headers[id]
        elif id in self.groups:
            return self.groups[id]
        elif id in self.pages:
            return self.pages[id]
        else:
            #log.error("Looking for 'compound' data structure for unknown id = %s", id)
            return {}


html_tag_re = re.compile('<.*?>')
def strip_html_tags(title):
    return html_tag_re.sub('', title)

def generate_fully_qualified_names(members, status: Status):
    for member in members:
        name = member['name']
        parent = member['parent']
        if parent:
            if parent in status.members:
                name = status.members[parent]['fully_qualified_name'] + '::<wbr />' + name
            else:
                log.error('Member %s has as parent an unknown id %s', name, parent)
                name = '&lt;unknown&gt;::<wbr />' + name
        member['fully_qualified_name'] = name
        if 'members' in member:
            generate_fully_qualified_names(member['members'], status)


def register_anchors_to_page(compound, page_id, status: Status):
    for section in compound['sections']:
        status.id_map[section[0]] = page_id
    for anchor in compound['anchors']:
        status.id_map[anchor] = page_id

def document_member_on_page(member, page_id, status: Status):
    member['page_id'] = page_id
    status.id_map[member['id']] = page_id
    register_anchors_to_page(member, page_id, status)

def document_member_variables_on_page(member, page_id, status: Status):
    for var in member['variables']:
        document_member_on_page(var, page_id, status)

def create_page(compound, status: Status):
    page_id = compound['id']
    document_member_on_page(compound, page_id, status)
    status.html_pages[page_id] = compound

def delete_page(compound, status: Status):
    del status.id_map[compound['id']]
    del status.html_pages[compound['page_id']]
    compound['page_id'] = ''
    # This function is only evert called for undocumented compounds, which necessarily will not have any
    # sections or anchors, so we don't have to worry about undoing any actions by `register_anchors_to_page()`.

def show_member(member, status: Status):
    if not (status.show_undocumented or member['brief'] or (member['member_type'] == 'enum' and member['has_value_details'])):
        return False
    if not status.show_private and 'access' in member and member['access'] == 'private':
        return False
    if not status.show_protected and 'access' in member and member['access'] == 'protected':
        return False
    return True

def is_class_like(member):
    return member['member_type'] in ['class', 'struct', 'union']

def class_has_documented_members(compound):
    return compound['typeless_functions'] or compound['groups'] or compound['groups_names'] or \
           compound['classes'] or compound['enums'] or compound['aliases'] or compound['functions'] or \
           compound['variables'] or compound['related']

def class_is_simple(compound):  # This is true if it has no documented members other than variables
    return not (compound['typeless_functions'] or compound['groups'] or compound['groups_names'] or
                compound['classes'] or compound['enums'] or compound['aliases'] or compound['functions'] or
                compound['related'] or compound['bases'] or compound['derived'])

def compound_has_documented_members(compound):  # not for classes
    return compound['modules'] or compound['namespaces'] or compound['classes'] or compound['enums'] or \
           compound['aliases'] or compound['functions'] or compound['variables'] or compound['macros']

def add_compound_member_booleans(compound):
    compound['has_class_details'] = False
    compound['has_enum_details'] = False
    compound['has_alias_details'] = False
    compound['has_function_details'] = False
    compound['has_variable_details'] = False
    compound['has_macro_details'] = False

def add_class_member_lists(compound):
    compound['typeless_functions'] = []
    compound['groups'] = []
    compound['groups_names'] = {}
    compound['classes'] = []
    compound['enums'] = []
    compound['aliases'] = []
    compound['functions'] = []
    compound['variables'] = []
    add_compound_member_booleans(compound)

def add_compound_member_lists(compound):  # not for classes
    compound['modules'] = []
    compound['namespaces'] = []
    compound['classes'] = []
    compound['enums'] = []
    compound['aliases'] = []
    compound['functions'] = []
    compound['variables'] = []
    compound['macros'] = []
    add_compound_member_booleans(compound)

def process_enum_values(member, status: Status):
    # member must be an enum
    # We only get here if member is being shown
    for value in member['members']:
        document_member_on_page(value, member['page_id'], status)

def process_class_member(compound, member, status: Status):
    # compound must be a class/struct/union
    if is_class_like(member):
        process_class(member, status)
        if member['simple']:
            document_member_on_page(member, compound['id'], status)
            document_member_variables_on_page(member, compound['id'], status)
            if member['doc'] or member['variables']:
                compound['has_class_details'] = True
        if 'page_id' in member:
            compound['classes'].append(member)
    elif show_member(member, status):
        document_member_on_page(member, compound['id'], status)
        member_type = member['member_type']
        if member['group']:
            if member['group'] not in compound['groups_names']:
                compound['groups_names'][member['group']] = len(compound['groups'])
                compound['groups'].append({
                    'name': member['group'],
                    'id': 'group--' + urllib.parse.quote(member['group']),
                    'members': []
                })
            compound['groups'][compound['groups_names'][member['group']]]['members'].append(member)
        elif member_type == 'enum':
            compound['enums'].append(member)
            process_enum_values(member, status)
        elif member_type == 'alias':
            compound['aliases'].append(member)
        elif member_type == 'function':
            if member['method_type'] == 'method':
                compound['functions'].append(member)
            else:
                compound['typeless_functions'].append(member)  # this can actually also be an assignment operator
        elif member_type == 'variable':
            compound['variables'].append(member)
        else:
            log.error("Member of type %s cannot be listed on %s page", member_type, compound['member_type'])
            return
        if member['doc'] or (member_type == 'enum' and member['has_value_details']):
            compound['has_' + member_type + '_details'] = True

def process_namespace_member(compound, member, status: Status):
    # compound must be a namespace
    if member['member_type'] != 'namespace' and not member['header']:
        # TODO: This only happens because of an issue with parent template class defined in other header file
        log.error("Member %s doesn't have a header file, this is a bug in dox++parse that needs to be fixed", member['id'])
    header_compound = status.headers[member['header']] if member['header'] else {}
    group_compound = status.groups[member['group']] if member['group'] else {}
    if is_class_like(member):
        process_class(member, status)
        if member['simple']:
            if member['group']:
                page_id = member['group']
            elif compound['id']:
                page_id = compound['id']
            else:
                page_id = member['header']
            document_member_on_page(member, page_id, status)
            document_member_variables_on_page(member, page_id, status)
            if member['doc'] or member['variables']:
                (compound if page_id == compound['id'] else status.get_compound(page_id))['has_class_details'] = True
        if 'page_id' in member:
            compound['classes'].append(member)
            if header_compound:
                header_compound['classes'].append(member)
            if group_compound:
                group_compound['classes'].append(member)
    elif member['member_type'] == 'namespace':
        process_namespace(member, status)
        if 'page_id' in member:
            compound['namespaces'].append(member)
            if header_compound:
                header_compound['namespaces'].append(member)
            if group_compound:
                group_compound['namespaces'].append(member)
    elif show_member(member, status):
        if member['relates']:
            page_id = member['relates']
            # Replace the ID in the list of related members by the member itself
            related_list = status.get_compound(page_id)['related']
            try:
                index = related_list.index(member['id'])
                related_list[index] = member
            except ValueError:
                # This should not occur, but let's make sure
                related_list.append(member)
        elif member['group']:
            page_id = member['group']
        elif compound['id']:
            page_id = compound['id']
        else:
            page_id = member['header']
        document_member_on_page(member, page_id, status)
        member_type = member['member_type']
        if member_type == 'enum':
            compound['enums'].append(member)
            if header_compound:
                header_compound['enums'].append(member)
            if group_compound:
                group_compound['enums'].append(member)
            process_enum_values(member, status)
        elif member_type == 'alias':
            compound['aliases'].append(member)
            if header_compound:
                header_compound['aliases'].append(member)
            if group_compound:
                group_compound['aliases'].append(member)
        elif member_type == 'function':
            compound['functions'].append(member)
            if header_compound:
                header_compound['functions'].append(member)
            if group_compound:
                group_compound['functions'].append(member)
        elif member_type == 'variable':
            compound['variables'].append(member)
            if header_compound:
                header_compound['variables'].append(member)
            if group_compound:
                group_compound['variables'].append(member)
        elif member_type == 'macro':
            compound['macros'].append(member)
            if header_compound:
                header_compound['macros'].append(member)
            if group_compound:
                group_compound['macros'].append(member)
        else:
            log.error("Member of type %s cannot be listed on %s page", member_type, compound['member_type'])
            return
        if member['doc'] or (member_type == 'enum' and member['has_value_details']):
            (compound if page_id == compound['id'] else status.get_compound(page_id))['has_' + member_type + '_details'] = True

def process_class(compound, status: Status):
    # compound must be a class/struct/union
    # Process namespace members
    for member in compound['members']:
        process_class_member(compound, member, status)
    # Create a page for this one?
    compound['simple'] = False
    if compound['id'] and (show_member(compound, status) or class_has_documented_members(compound)):
        compound['simple'] = class_is_simple(compound)
        if not compound['simple']:
            create_page(compound, status)

def process_namespace(compound, status: Status):
    # compound must be a namespace
    # Process namespace members
    for member in compound['members']:
        process_namespace_member(compound, member, status)
    # Create a page for this one?
    if compound['id'] and (show_member(compound, status) or compound_has_documented_members(compound)):
        create_page(compound, status)

def has_value_details(member):
    for child in member['members']:
        if child['brief']:
            return True
    return False

def verify_namespace_header(member):
    for child in member['members']:
        if child['header'] and child['header'] != member['header']:
            member['header'] = ''
            return

def find_header_file(compound):
    # TODO: Modules without members, that only have submodules, should be assigned a header file.
    # We first count how many members have the same header file
    headers = {}
    for members in (compound['classes'], compound['enums'], compound['aliases'],
                    compound['functions'], compound['variables'], compound['macros']):
        for member in members:
            if member['header'] in headers:
                headers[member['header']] += 1
            else:
                headers[member['header']] = 1
    # Any header file that is shown in 80% of the members we take as the header for the compound
    threshold = 0.8 * sum(headers.values())
    compound_header = max(headers, key=lambda m: headers[m], default='')
    if compound_header in headers and headers[compound_header] < threshold:
        compound_header = ''
    compound['header'] = compound_header

def process_base_derived_related_lists(status: Status):
    for member in status.members.values():
        if 'bases' in member and member['bases']:
            member['base_classes'] = []
            for base in member['bases']:
                if 'id' in base:
                    tmp = status.members[base['id']].copy()  # we make a copy so we can change the 'access' value.
                    tmp['access'] = base['access']
                    member['base_classes'].append(tmp)
                else:
                    tmp = {
                        'member_type': 'class',  # TODO: we don't know, could be struct.
                        'id': '',
                        'page_id': '',
                        'name': html.escape(base['typename']),
                        'fully_qualified_name': html.escape(base['typename']),
                        'access': base['access']
                    }
                    member['base_classes'].append(tmp)
        if 'derived' in member and member['derived']:
            member['derived_classes'] = []
            for id in member['derived']:
                member['derived_classes'].append(status.members[id])
        if 'related' in member and member['related']:
            related_list = member['related']
            member['related'] = []
            for related in related_list:
                if isinstance(related, dict):
                    member['related'].append(related)

def assign_page(status: Status):
    # TODO: Add option `show_if_documented_children`
    # All header files will have a page, whether they're documented or not
    for header in status.headers.values():
        add_compound_member_lists(header)
        header['member_type'] = 'file'
        create_page(header, status)
    # All groups (modules) will have a page, whether they're documented or not
    for group in status.groups.values():
        if not group['name']:
            # We need a name!
            # Apparently this group was ony added to, never documented.
            group['name'] = group['id']
        add_compound_member_lists(group)
        group['member_type'] = 'module'
        create_page(group, status)
    # Prepare class and namespace members with needed fields. Also:
    #  - find out if enum members have documented values
    #  - find out if namespace members all have the same header file, and reset namespace header if not
    for member in status.members.values():
        if not member['id']:
            continue
        if member['member_type'] == 'namespace':
            add_compound_member_lists(member)
            verify_namespace_header(member)
        elif is_class_like(member):
            add_class_member_lists(member)
        elif member['member_type'] == 'enum':
            member['has_value_details'] = has_value_details(member)
    # Assign members to a specific page
    base = {  # bogus namespace to get things rolling
        'id': '',
        'member_type': 'namespace',
        'members': status.data['members'],
        'header': '',
        'group': ''
    }
    add_compound_member_lists(base)
    process_namespace(base, status)
    # Fix base and derived class lists, and related member lists
    process_base_derived_related_lists(status)
    # Assign a header file to groups and namespaces
    for member in status.members.values():
        if member['id'] and member['header']:
            member['header'] = status.modify_include_statement(member['header'])
    for group in status.groups.values():
        find_header_file(group)
    for member in status.members.values():
        if member['id'] and member['member_type'] == 'namespace':
            find_header_file(member)
    # Don't show undocumented header files that don't list any members
    for header in status.headers.values():
        if not compound_has_documented_members(header) and not header['brief']:
            delete_page(header, status)
    # Don't show undocumented groups (modules) that don't list any members (these are unlikely to exist...)
    for group in status.groups.values():
        if not compound_has_documented_members(group) and not group['brief']:
            delete_page(group, status)
    # Assign sub-groups to be shown in parent group's page; they're always sorted
    for group in status.groups.values():
        group['modules'] = []
        for id in group['subgroups']:
            if status.groups[id]['page_id']:
                group['modules'].append(status.groups[id])
        group['modules'].sort(key=lambda x: x['name'].casefold())
    # Set module value of all members in each module
    for group in status.groups.values():
        module = (group['name'], group['id'] + '.html')
        for members in [group['namespaces'], group['classes']]:
            for member in members:
                member['module'] = module
    # All pages have a page, obviously
    for page in status.pages.values():
        page['member_type'] = 'page'
        create_page(page, status)


def create_indices(status: Status):
    index = {}
    index['symbols'] = []   # Used in classes and namespaces index
    index['files'] = []     # Used in files index
    index['modules'] = []   # Used in modules index
    index['pages'] = []     # used in pages index
    # Symbols (class, struct, union and namespace)
    for member in status.members.values():
        if not member['id']:
            continue
        if member['member_type'] not in ['namespace', 'class', 'struct', 'union']:  # TODO: rewrite using is_class_like()
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
    index['symbols'].sort(key=lambda x: x['name'].casefold())
    for member in status.members.values():
        if 'children' in member:
            member['children'].sort(key=lambda x: x['name'].casefold())
    # Files (headers)
    index['files'] = walktree.build_file_hierarchy(status.data['headers'])
    # Modules (groups)
    status.data['groups'].sort(key=lambda x: x['name'].casefold())
    for group in status.data['groups']:
        if not group['page_id']:
            continue
        if not group['parent']:
            index['modules'].append(group)
        group['children'] = group['modules']
    # Pages
    status.data['pages'].sort(key=lambda x: x['title'].casefold())
    for page in status.data['pages']:
        if page['id'] == 'index':
            continue  # the index is not on the list of pages
        if not page['parent']:
            index['pages'].append(page)
        page['children'] = []
        prev = None
        nav_list = []
        for s in page['subpages']:
            # We don't sort children, but use them in the order they're referenced in the parent page
            child = status.pages[s]
            page['children'].append(child)
            nav_list.append((child['id'] + '.html', child['title']))
        if nav_list:
            prev = None
            parent = (page['id'] + '.html', page['title'])
            for i in range(len(nav_list)):
                next = nav_list[i + 1] if len(nav_list) > i + 1 else None
                page['children'][i]['footer_navigation'] = (prev, parent, next)
                prev = nav_list[i]
    return index


def process_navbar_links(navbar, status: Status):
    # Convert (title, id, sub) into (title, link, id, sub)
    out = []
    for title, id, sub in navbar:
        if sub:
            sub = process_navbar_links(sub, status)
        if len(id) > 1 and id[0] == '#':
            id = id[1:]
            link = status.get_link(id)
            if not link:
                log.error("Navbar references an id that is not in the documentation")
            if not title:
                title = status.find_title(id)
        else:
            link = id
            id = ''
        out.append((title, link, id, sub))
    return out


def remove_p_tag(title):
    # Markdown always encloses its output in paragraph tags, but we don't want these when it's
    # a page or section title, nor for the brief docs.
    if title[:3] == '<p>' and title[-4:] == '</p>':
        title = title[3:-4]
    if '<p>' in title:
        log.warning("Title contains a HTML paragraph tag: %s", title)
    return title

def process_sections_recursive(sections, level, md):
    if sections[0][2] < level:
        return []
    section = sections.pop(0)
    subsections = []
    while sections and sections[0][2] > section[2]:
        subsections.append(process_sections_recursive(sections, level + 1, md))
    return (section[0], remove_p_tag(md.reset().convert(section[1])), subsections)

def process_sections(compound, md):
    # compound['sections'] is a flat list of tuples [(name, title, level), ...]
    # We turn it into a hierarchical list according to level: [(name, title, [...]), ...]
    # We also apply Markdown processing to `title`
    sections = compound['sections']
    compound['sections'] = []
    while sections:
        compound['sections'].append(process_sections_recursive(sections, 1, md))

def parse_markdown(status: Status):
    extensions = [
        # Extensions packaged with `markdown`:
        'attr_list',        # https://python-markdown.github.io/extensions/attr_list/
        'md_in_html',       # https://python-markdown.github.io/extensions/md_in_html/
        'tables',           # https://python-markdown.github.io/extensions/tables/
        'fenced_code',      # https://python-markdown.github.io/extensions/fenced_code_blocks/
        'codehilite',       # https://python-markdown.github.io/extensions/code_hilite/
        'sane_lists',       # https://python-markdown.github.io/extensions/sane_lists/
        'smarty',           # https://python-markdown.github.io/extensions/smarty/
        # Installed with package `markdown-headdown`
        'mdx_headdown',     # https://github.com/SaschaCowley/Markdown-Headdown
        # Our own concoctions
        AdmonitionExtension(),              # Modification of the standard 'admonition' extension
        FixLinksExtension(status.id_map),   # Fixes links from '#id' to 'page_id.html#id'
        AddClassesExtension(),              # Adds m.css classes to <img> and <table>
        RecordLinkedImagesExtension(status.images),  # Stores names of images linked in the documentation
        # Two extensions not installed through PyPI because they cause a downgrade of the Markdown package
        # (would be installed with packages `MarkdownSuperscript` and `MarkdownSubscript`)
        SubscriptExtension(),       # https://github.com/jambonrose/markdown_subscript_extension
        SuperscriptExtension()      # https://github.com/jambonrose/markdown_superscript_extension
    ]
    extension_configs = {
        'codehilite': {
            'css_class': 'm-code',
            'wrapcode': False
        },
        'mdx_headdown': {
            'offset': 1
        }
    }
    # TODO: Create an extension that adds image file names to status.images
    # TODO: Create a LaTeX math extension based on some stuff in m.css as well as the following:
    #       https://github.com/justinvh/Markdown-LaTeX
    #       https://github.com/ShadowKyogre/python-asciimathml
    md = markdown.Markdown(extensions=extensions, extension_configs=extension_configs, output_format="html5")

    for header in status.headers.values():
        if header['brief']:
            header['brief'] = remove_p_tag(md.reset().convert(header['brief']))
        if header['doc']:
            header['doc'] = md.reset().convert(header['doc'])
        process_sections(header, md)
    for group in status.groups.values():
        if group['brief']:
            group['brief'] = remove_p_tag(md.reset().convert(group['brief']))
        if group['doc']:
            group['doc'] = md.reset().convert(group['doc'])
        process_sections(group, md)
    for member in status.members.values():
        if member['id'] not in status.id_map:
            continue
        if member['brief']:
            member['brief'] = remove_p_tag(md.reset().convert(member['brief']))
        if member['doc']:
            member['doc'] = md.reset().convert(member['doc'])
        process_sections(member, md)
    for page in status.pages.values():
        if page['doc']:
            page['doc'] = md.reset().convert(page['doc'])
        if page['title']:
            page['title'] = remove_p_tag(md.reset().convert(page['title']))
        process_sections(page, md)


def render_type(type, status: Status, doc_link_class):
    typename = html.escape(type['typename'])
    if typename:
        if type['id']:
            link = status.get_link(type['id'])
            if link:
                typename = '<a href="' + link + '" class="' + doc_link_class + '">' + typename + '</a>'
        if type['qualifiers']:
            if type['qualifiers'][0] == 'c':
                typename += ' '
            typename += html.escape(type['qualifiers'])
    return typename

def parse_types(status: Status, doc_link_class):
    for member in status.members.values():
        if 'type' in member and isinstance(member['type'], dict):
            member['type']['type'] = render_type(member['type'], status, doc_link_class)
        if 'return_type' in member and member['return_type']:
            member['return_type']['type'] = render_type(member['return_type'], status, doc_link_class)
        if 'arguments' in member:
            for arg in member['arguments']:
                arg['type'] = render_type(arg, status, doc_link_class)
        if 'template_parameters' in member:
            for arg in member['template_parameters']:
                if arg['type'] == 'type':
                    arg['type'] = 'typename'
                    if arg['default']:
                        arg['default'] = render_type(arg['default'], status, doc_link_class)
                else:  # isinstance(arg['type'], 'dict'):
                    arg['type'] = render_type(arg['type'], status, doc_link_class)
                arg['name'] = html.escape(arg['name'])  # just in case this is "<SFINAE>".


def add_wbr(text: str):
    # TODO: This function not yet used
    if '<' in text:  # Stuff contains HTML code, do not touch!
        return text
    if '::' in text:  # C++ names
        return text.replace('::', '::<wbr />')
    if '_' in text:  # VERY_LONG_UPPER_CASE macro names
        return text.replace('_', '_<wbr />')
    # These characters are quite common, so at least check that there is no
    # space (which may hint that the text is actually some human language):
    if '/' in text and not ' ' in text:  # URLs
        return text.replace('/', '/<wbr />')
    return text


def add_breadcrumb(compound, name, compounds):
    path_reverse = [compound['id']]
    parent = compound['parent']
    while parent:
        path_reverse.append(parent)
        parent = compounds[parent]['parent']
    compound['breadcrumb'] = []
    for elem in reversed(path_reverse):
        compound['breadcrumb'].append([compounds[elem][name], elem + '.html'])


def fixup_namespace_compound_members(compound, status: Status):
    # Adjusts data in the members referenced in compound for display in the context of compound.
    # Some details about a member appear differently depending on which page we're looking at.
    # This function only changes member fields that are not primary, (i.e. original data is not lost):
    # - has_details: if a section with member details needs to be shown for this member
    # - include: either () to not show include file information, or ("name", link) to show it
    # - TODO: fixup referenced types in each member to be relative to compound if compound is a namespace
    def has_details(member):
        if member['page_id'] != compound['page_id']:
            return False
        if member['doc']:
            return True
        if is_class_like(member) and member['variables']:  # we only get here if it's 'simple'.
            return True
        if member['member_type'] == 'enum' and member['has_value_details']:
            return True
        return False

    if compound['member_type'] == 'file':
        # None of the members will show an include file
        compound_header = compound['id']
    else:
        compound_header = compound['header']
        if compound_header:
            compound['include'] = ('"' + status.headers[compound_header]['name'] + '"', compound_header + '.html')
        else:
            compound['include'] = ()
    for members in (compound['classes'], compound['enums'], compound['aliases'], compound['functions'],
                    compound['variables'], compound['macros']):
        for member in members:
            if is_class_like(member) and not member['simple']:
                member['has_details'] = False
                continue
            member['has_details'] = has_details(member)
            if member['header'] == compound_header:
                member['include'] = ()
            else:
                member['include'] = ('"' + status.headers[member['header']]['name'] + '"', member['header'] + '.html')
                member['has_details'] = True
                if member['page_id'] == compound['id']:
                    compound['has_' + member['member_type'] + '_details'] = True

def fixup_class_compound_members(compound, status: Status):
    # This function works like `fixup_namespace_compound_members`, but is for when the compound is a class/struct/union.
    # - TODO: fixup referenced types in each member to be relative to compound
    def has_details(member):
        if is_class_like(member):
            if not member['simple']:
                return False
            if member['variables']:
                return True
        if member['doc']:
            return True
        if member['member_type'] == 'enum' and member['has_value_details']:
            return True
        return False

    compound['include'] = ('"' + status.headers[compound['header']]['name'] + '"', compound['header'] + '.html')
    for members in (compound['typeless_functions'], compound['classes'], compound['enums'], compound['aliases'],
                    compound['functions'], compound['variables']):
        for member in members:
            member['has_details'] = has_details(member)
    for group in compound['groups']:
        for member in group['members']:
            member['has_details'] = has_details(member)
    for member in compound['related']:
        member['has_details'] = has_details(member)
        if member['header'] == compound['header']:
            member['include'] = ()
        else:
            member['include'] = ('"' + status.headers[member['header']]['name'] + '"', member['header'] + '.html')
            member['has_details'] = True
            compound['has_' + member['member_type'] + '_details'] = True


class EntryType(enum.Enum):
    # Order must match the search_type_map below; first value is reserved for
    # ResultFlag.ALIAS
    PAGE = 1
    NAMESPACE = 2
    MODULE = 3
    CLASS = 4
    STRUCT = 5
    UNION = 6
    ALIAS = 7
    FILE = 8
    FUNCTION = 9
    MACRO = 10
    ENUM = 11
    ENUM_VALUE = 12
    VARIABLE = 13

entry_type_map = {
    'page': EntryType.PAGE,
    'namespace': EntryType.NAMESPACE,
    'module': EntryType.MODULE,
    'class': EntryType.CLASS,
    'struct': EntryType.STRUCT,
    'union': EntryType.UNION,
    'alias': EntryType.ALIAS,
    'file': EntryType.FILE,
    'function': EntryType.FUNCTION,
    'macro': EntryType.MACRO,
    'enum': EntryType.ENUM,
    'enumvalue': EntryType.ENUM_VALUE,
    'variable': EntryType.VARIABLE
}

search_type_map = [
    # Order must match the EntryType above
    (CssClass.SUCCESS, 'page'),
    (CssClass.PRIMARY, 'namespace'),
    (CssClass.SUCCESS, 'module'),
    (CssClass.PRIMARY, 'class'),
    (CssClass.PRIMARY, 'struct'),
    (CssClass.PRIMARY, 'union'),
    (CssClass.PRIMARY, 'alias'),
    (CssClass.WARNING, 'file'),
    (CssClass.INFO, 'function'),
    (CssClass.INFO, 'macro'),
    (CssClass.PRIMARY, 'enum'),
    (CssClass.DEFAULT, 'enum value'),
    (CssClass.DEFAULT, 'variable')
]

snake_case_point ='_[^_]'
camel_case_point = '[^A-Z][A-Z].'
snake_case_point_re = re.compile(snake_case_point)
camel_case_point_re = re.compile(camel_case_point)
camel_or_snake_case_point_re = re.compile('({})|({})'.format(snake_case_point, camel_case_point))

def add_entry_to_search_data(result, joiner: str, trie: Trie, map: ResultMap, add_lookahead_barriers,
                             add_snake_case_suffixes, add_camel_case_suffixes):
    has_params = hasattr(result, 'params') and result.params is not None

    # Add entry as-is
    index = map.add(joiner.join(result.prefix + [result.name_with_args]),
                    result.url, suffix_length=result.suffix_length, flags=result.flags)

    # Add functions and function macros the second time with () appended, everything is the same
    # except for suffix length which is 2 chars shorter
    index_args = None
    if has_params:
        index_args = map.add(joiner.join(result.prefix + [result.name_with_args]), result.url,
                             suffix_length=result.suffix_length - 2, flags=result.flags)

    # Add the result multiple times with all possible prefixes
    prefixed_name = result.prefix + [result.name]
    for i in range(len(prefixed_name)):
        lookahead_barriers = []
        name = ''
        for j in prefixed_name[i:]:
            if name:
                lookahead_barriers += [len(name)]
                name += joiner
            name += j
        trie.insert(name.lower(), index, lookahead_barriers=lookahead_barriers if add_lookahead_barriers else [])

        # Add functions and function macros the second time with () appended, referencing the other
        # result that expects () appended. The lookahead barrier is at the ( character to avoid the
        # result being shown twice.
        if has_params:
            trie.insert(name.lower() + '()', index_args, lookahead_barriers=lookahead_barriers + [len(name)]
            if add_lookahead_barriers else [])

    # Add the result multiple times again for all parts of the name
    if add_camel_case_suffixes and add_snake_case_suffixes:
        prefix_end_re = camel_or_snake_case_point_re
    elif add_camel_case_suffixes:
        prefix_end_re = camel_case_point_re
    elif add_snake_case_suffixes:
        prefix_end_re = snake_case_point_re
    else:
        prefix_end_re = None
    if prefix_end_re:
        for m in prefix_end_re.finditer(result.name.lstrip('__')):
            name = result.name[m.start(0)+1:]
            trie.insert(name.lower(), index)
            if has_params:
                trie.insert(name.lower() + '()', index_args, lookahead_barriers=[len(name)])

    # Add keyword aliases for this symbol
    for search, title, suffix_length in result.keywords:
        if not title:
            title = search
        keyword_index = map.add(title, '', alias=index, suffix_length=result.suffix_length)
        trie.insert(search.lower(), keyword_index)

    return len(result.keywords) + 1

def build_search_data(status: Status, merge_subtrees=True, add_lookahead_barriers=True, add_snake_case_suffixes=True,
                      add_camel_case_suffixes=True, merge_prefixes=True) -> bytearray:
    symbol_count = 0
    trie = Trie()
    map = ResultMap()
    for member in status.members.values():
        if not 'page_id' in member or not member['page_id']:  # Not documented, skip
            continue
        result = Empty()
        result.prefix = walktree.get_prefix(member['id'], status.members)
        result.name = member['name']
        result.flags = ResultFlag.from_type(ResultFlag.DEPRECATED if member['deprecated'] else ResultFlag(0),
                                            entry_type_map[member['member_type']])
        result.url = member['page_id'] + '.html'
        if member['page_id'] != member['id']:
            result.url += '#' + member['id']
        result.keywords = []  # TODO: dox++parse should output a keywords field for all members.

        # Handle function arguments
        result.name_with_args = result.name
        result.suffix_length = 0
        if 'arguments' in member and member['arguments']:
            # Some very heavily templated function parameters might cause the suffix_length to exceed 256,
            # which won't fit into the serialized search data. However that *also* won't fit in the search
            # result list so there's no point in storing so much. Truncate it to 48 chars which should fit
            # the full function name in the list in most cases, yet be still long enough to be able to
            # distinguish particular overloads.
            result.params = ', '.join([arg['typename'] +
                                       (' ' if arg['qualifiers'] and arg['qualifiers'][0] == 'c' else '') +
                                       arg['qualifiers'] for arg in member['arguments']])
            if len(result.params) > 49:
                result.params = result.params[:48] + '…'
            result.name_with_args += '(' + result.params + ')'
            result.suffix_length += len(result.params.encode('utf-8')) + 2
        if 'const' in member and member['const']:
            result.name_with_args += ' const'
            result.suffix_length += len(' const')

        # Add the symbol with all its different prefixes and suffixes and so on
        symbol_count += add_entry_to_search_data(result, '::', trie, map, add_lookahead_barriers,
                                                 add_snake_case_suffixes, add_camel_case_suffixes)

    for file in status.headers.values():
        if not 'page_id' in file or not file['page_id']:  # Not documented, skip
            continue
        result = Empty()
        result.prefix = file['name'].split('/')
        result.name = result.prefix[-1]
        result.prefix = result.prefix[:-1]
        result.flags = ResultFlag.from_type(ResultFlag(0), entry_type_map['file'])
                        # ResultFlag.DEPRECATED if file['deprecated'] else ResultFlag(0)
        result.url = file['id'] + '.html'
        result.keywords = []  # TODO: dox++parse should output a keywords field for all members.
        result.name_with_args = result.name
        result.suffix_length = 0

        # Add the symbol with all its different prefixes and suffixes and so on
        symbol_count += add_entry_to_search_data(result, '/', trie, map, add_lookahead_barriers,
                                                 add_snake_case_suffixes, add_camel_case_suffixes)

    for group in status.groups.values():
        if not 'page_id' in group or not group['page_id']:  # Not documented, skip
            continue
        result = Empty()
        result.prefix = walktree.get_prefix(group['id'], status.groups)
        result.name = group['name']
        result.flags = ResultFlag.from_type(ResultFlag(0), entry_type_map['module'])
                        # ResultFlag.DEPRECATED if group['deprecated'] else ResultFlag(0)
        result.url = group['id'] + '.html'
        result.keywords = []  # TODO: dox++parse should output a keywords field for all members.
        result.name_with_args = result.name
        result.suffix_length = 0

        # Add the symbol with all its different prefixes and suffixes and so on
        symbol_count += add_entry_to_search_data(result, ' » ', trie, map, add_lookahead_barriers,
                                                 add_snake_case_suffixes, add_camel_case_suffixes)

    for page in status.pages.values():
        result = Empty()
        result.prefix = walktree.get_prefix(page['id'], status.pages, key='title')
        result.name = page['title']
        result.flags = ResultFlag.from_type(ResultFlag(0), entry_type_map['page'])
                        # ResultFlag.DEPRECATED if page['deprecated'] else ResultFlag(0)
        result.url = page['id'] + '.html'
        result.keywords = []  # TODO: dox++parse should output a keywords field for all members.
        result.name_with_args = result.name
        result.suffix_length = 0

        # Add the symbol with all its different prefixes and suffixes and so on
        symbol_count += add_entry_to_search_data(result, ' » ', trie, map, add_lookahead_barriers,
                                                 add_snake_case_suffixes, add_camel_case_suffixes)

    # For each node in the trie sort the results so the found items have sane order by default
    log.info("Indexed %d symbols for search data", symbol_count)
    trie.sort(map)
    return serialize_search_data(trie, map, search_type_map, symbol_count)


def createhtml(input_file, output_dir, options, template_params):
    """
    Generates HTML pages for the documentation in the JSON file `input_file`.

    :param input_file: the name of the JSON file that contains the documentation to format (string)
    :param output_dir: directory where the HTML files will be written (string)
    :param options: dictionary with options for how to process things
    :param template_params: dictionary with template parameters

    Options must contain the keys:
    - 'show_private': include private members in the documentation
    - 'show_protected': include protected members in the documentation
    - 'show_undocumented': include undocumented members in the documentation
    - 'modify_include_statement': a Python function to rewrite the header ID of members
    - 'extra_files': list of extra files to copy to the output directory
    - 'templates': path to templates to use instead of default ones
    - 'source_files': list of source files (header files + markdown files), used to locate
                      image files referenced in documentation.
    - 'doc_link_class': TODO: document
    - 'add_snake_case_suffixes': TODO: document
    - 'add_camel_case_suffixes': TODO: document
    - 'search_add_lookahead_barriers': TODO: document
    - 'search_merge_subtrees': TODO: document
    - 'search_merge_prefixes': TODO: document
    """

    # Load data
    status = Status(walktree.load_data_from_json_file(input_file), options)

    # We need to have an index.html page
    if 'index' not in status.pages:
        page = members.new_page('index', template_params['PROJECT_NAME'], '')
        page['sections'] = []
        page['anchors'] = []
        status.pages['index'] = page

    # Generate fully qualified names
    generate_fully_qualified_names(status.data['members'], status)

    # Find out which pages to create, what is listed in each, and in which page
    # the detailed documentation for each member has to go
    assign_page(status)
    #print('\n\nhtml_pages', status.html_pages)
    #print('\n\nid_map', status.id_map)

    # Parse all Markdown
    parse_markdown(status)

    # Convert type name strings into HTML links if appropriate
    parse_types(status, options['doc_link_class'])

    # Create tree structure for index pages
    index = create_indices(status)

    # Navbar links
    if 'LINKS_NAVBAR1' in template_params:
        template_params['LINKS_NAVBAR1'] = process_navbar_links(template_params['LINKS_NAVBAR1'], status)
    if 'LINKS_NAVBAR2' in template_params:
        template_params['LINKS_NAVBAR2'] = process_navbar_links(template_params['LINKS_NAVBAR2'], status)

    # If no stylesheets were given, use the default one
    if not 'STYLESHEETS' in template_params or not template_params['STYLESHEETS']:
        template_params['STYLESHEETS'] = ['css/m-light-documentation.compiled.css']

    # Fill in default favicon if not given, and get type
    if not template_params['FAVICON']:
        template_params['FAVICON'] = 'html_templates/favicon-light.png'
    template_params['FAVICON'] = (template_params['FAVICON'], mimetypes.guess_type(template_params['FAVICON'])[0])

    # If custom template dir was supplied, use the default template directory as a fallback
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
    for id in status.html_pages:
        file = id + '.html'
        compound = status.html_pages[id]
        #if not compound:
        #    log.error("Generating 'compound' data structure for unknown id = %s", id)
        #    continue
        type = compound['member_type']
        if type == 'file':
            compound['breadcrumb'] = [(p, '') for p in compound['name'].split('/')]  # TODO: Make sure this works on Windows
            fixup_namespace_compound_members(compound, status)
        elif type == 'module':
            add_breadcrumb(compound, 'name', status.groups)
            fixup_namespace_compound_members(compound, status)
        elif type == 'page':
            add_breadcrumb(compound, 'title', status.pages)
            for elem in compound['breadcrumb']:
                elem.append(strip_html_tags(elem[0]))
        else:
            add_breadcrumb(compound, 'name', status.members)
            if type == 'namespace':
                fixup_namespace_compound_members(compound, status)
            else:
                fixup_class_compound_members(compound, status)
        template = env.get_template(type + '.html')
        log.debug("Rendering %s to file %s using template %s",
                  compound['fully_qualified_name'] if 'fully_qualified_name' in compound else
                  compound['title'] if 'title' in compound else compound['name'],
                  file, template.filename)
        rendered = template.render(compound=compound,
                                   FILENAME=file,
                                   SEARCHDATA_FORMAT_VERSION=searchdata_format_version,
                                   **template_params)
        with open(os.path.join(output_dir, file), 'w') as f:
            f.write(rendered)

    # Generate indexes for pages, groups (==modules), namespaces, classes/structs/unions (==classes), and headers (==files)
    for file in ['pages.html', 'modules.html', 'namespaces.html', 'classes.html', 'files.html']:
        template = env.get_template(file)
        log.debug("Rendering file %s using template %s", file, template)
        rendered = template.render(index=index,
                                   FILENAME=file,
                                   SEARCHDATA_FORMAT_VERSION=searchdata_format_version,
                                   **template_params)
        with open(os.path.join(output_dir, file), 'w') as f:
            f.write(rendered)

    # Generate search data
    if not template_params['SEARCH_DISABLED']:
        data = build_search_data(status, add_lookahead_barriers=options['search_add_lookahead_barriers'],
                                 add_snake_case_suffixes=options['add_snake_case_suffixes'], add_camel_case_suffixes=options['add_camel_case_suffixes'],
                                 merge_subtrees=options['search_merge_subtrees'], merge_prefixes=options['search_merge_prefixes'])

        if template_params['SEARCH_DOWNLOAD_BINARY']:
            log.info("Writing search data to %s", searchdata_filename)
            with open(os.path.join(output_dir, searchdata_filename), 'wb') as f:
                f.write(data)
        else:
            log.info("Writing search data to %s", searchdata_filename_b85)
            with open(os.path.join(output_dir, searchdata_filename_b85), 'wb') as f:
                f.write(base85encode_search_data(data))

        # OpenSearch metadata, if we have the base URL
        if template_params['SEARCH_BASE_URL']:
            log.info("writing OpenSearch metadata file")
            template = env.get_template('opensearch.xml')
            rendered = template.render(**template_params)
            output = os.path.join(output_dir, 'opensearch.xml')
            with open(output, 'w') as f:
                f.write(rendered)

    # Copy over all referenced files
    for i in template_params['STYLESHEETS'] + options['extra_files'] + ([template_params['PROJECT_LOGO']] if template_params['PROJECT_LOGO'] else []) + ([template_params['FAVICON'][0]] if template_params['FAVICON'][0] else []):
        if urllib.parse.urlparse(i).netloc:
            continue
        # File is either found relative to the current directory or relative to script directory
        p = i
        if not os.path.exists(p):
            p = os.path.join(doxpp_path, p)
        if not os.path.exists(p):
            log.error("File %s not found", i)
        log.info("Copying %s to output", p)
        shutil.copy(p, os.path.join(output_dir, os.path.basename(p)))
    # The images we need to search for in the input directories
    source_dirs = set()
    for s in options['source_files']:
        if ('*' in s) or ('?' in s):
            for s in glob.glob(s):
                source_dirs.add(os.path.dirname(s))
        else:
            source_dirs.add(os.path.dirname(s))
    for i in status.images:
        found = False
        for s in source_dirs:
            p = os.path.join(s,i)
            if os.path.exists(p):
                log.info("Copying %s to output", p)
                shutil.copy(p, os.path.join(output_dir, os.path.basename(i)))
                found = True
                break
        if not found:
            log.error("File %s not found", i)
    # The search.js is special, we encode the version information into its filename
    if not template_params['SEARCH_DISABLED']:
        p = os.path.join(doxpp_path, 'html_templates/search.js')
        log.info("Copying %s to output as %s", p, search_filename)
        shutil.copy(p, os.path.join(output_dir, search_filename))

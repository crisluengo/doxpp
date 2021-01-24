\page json_output JSON output of **dox++parse**

The **dox++parse** program outputs a single JSON file, which should be easy to convert into any representation
the user desires. The JSON file has the following fields:

- \ref json_output_members: members are the namespaces, classes, functions, variables, etc.
- \ref json_output_headers: the header files
- \ref json_output_groups: the groups (or modules)
- \ref json_output_pages: the pages

Each of these is a list of elements, each element is a dictionary with fields that depend on the type.


\section json_output_members "members"

This is a list of everything that is defined at the global scope, with each namespace and each
class/struct/union containing lists of its members. Thus, a hierarchical structure is formed
that mimics the declarations in the code.

Members are listed in order in which they were found in the header file.
Each member is a dictionary as described in \ref members.


\section json_output_headers "headers"

This is a list of header files. Each headers is a dictionary with the following fields:

- "id": unique identifier
- "name": file name, with path from project root
- "brief": brief description (see \ref json_output_brief_doc)
- "doc": full documentation (see \ref json_output_brief_doc)
- "sections": (ID, title, level) for sections in "doc" (see \ref json_output_sections)
- "anchors": IDs of anchors in "doc" (see \ref json_output_anchors)
- "includes": list of files included by the header

We don't list the members that are defined in a file, this information can easily be gathered
by iterating through all members and finding the ones that list a file's ID.

Any directory structure to be shown in the documentation can be reconstructed from the file names,
it is not explicitly stored here.

\subsection json_output_includes "includes"
This is a list of strings, one for each header included by the header file. If the included
header file is part of the documentation, the string will be the header file name enclosed
in double quotes, the file name being a Markdown-formatted link to the file. Otherwise,
the string will be the header file name enclosed in angled brackets.

\section json_output_groups "groups"

This is a list of defined groups. Each groups is a dictionary with the following fields:

- "id": unique identifier
- "name": group name
- "brief": brief description (see \ref json_output_brief_doc)
- "doc": full documentation (see \ref json_output_brief_doc)
- "sections": (ID, title, level) for sections in "doc" (see \ref json_output_sections)
- "anchors": IDs of anchors in "doc" (see \ref json_output_anchors)
- "parent": ID of the parent group, if any
- "subgroups": list of IDs of any child groups

Note that the "subgroups" field contains the IDs of child groups, not dictionaries defining
the groups. The group list is a flat list, the hierarchy can be reconstructed by following
the IDs of parents and children. No loops will ever be created (i.e. a group cannot be
both an ancestor and a child of another group). Groups do not need to be in the hierarchy
either.

\section json_output_pages "pages"

A list of pages. Each page is a dictionary with the following fields:

- "id": unique identifier
- "title": page title
- "doc": full documentation (see \ref json_output_brief_doc)
- "sections": (ID, title, level) for sections in "doc" (see \ref json_output_sections)
- "anchors": IDs of anchors in "doc" (see \ref json_output_anchors)
- "parent": ID of the parent page, if any
- "subpages": list of IDs of any child pages

Like with groups, pages are stored as a flat list, with the hierarchy described by
the "parent" and "subpages" fields. No loops will ever be created.

One page has the ID 'index', this is the main page. The index page doesn't need
to be the parent of the other pages though, but it can be. It cannot be a subpage,
its "parent" field will always be empty.


\section json_output_common_fields Fields common to all elements

\subsection json_output_brief_doc "brief" and "doc"
The first line of the documentation will be split off as into the "brief" field, with
the remaining text in the "doc" field. However, if the first line starts with `\brief`
then the whole first paragraph is split off into the "brief" field, see \ref command_brief.

Any Markdown in the documentation will not be parsed, this is something for the generator to do.
However, we will look for `\‍ref`, `\ingroup` and similar commands, as described in
\ref commands_inside.

Commands that create a link are replaced by the Markdown syntax for a link, linking to
`#<id>`. For example, `\‍ref foo::bar` will be replaced by `[foo::bar](#foo-bar)`, and
`\‍ref foo::bar "the bar value"` will be replaced by `[the bar value](#foo-bar)`. Note that
this is Markdown syntax to link to an anchor within the same page. The generator will have
to identify these and change them to links to another page if necessary (only the generator
will know what page the documentation for a given member is put in).

Other recognized commands will be similarly replaced with Markdown or removed, as appropriate.
Any command not listed in \ref commands_inside will be left as-is.

\subsection json_output_anchors "anchors"
Documentation can contain anchors that can be referenced in the same way that members or pages
can be referenced. These are created with \ref command_anchor. This command is replaced with
appropriate Markdown syntax to create an anchor, and the anchor ID (the string that can be used
with `\‍ref` to link to the anchor) is listed in the "anchors" field. Where these anchors are
referenced, a Markdown link is generated as described in the section above. The generator will
need to modify this link to point to the right page. The "anchor" field gives the required
information to the generator for this.

\subsection json_output_sections "sections"
In a similar fashion to anchors, documentation can also contain headers that can be referenced.
These are created with the \ref command_section, \ref command_subsection and \ref command_subsubsection.
These commands are replaced with the appropriate Markdown syntax, and the section ID, title and
level (1 for section, 2 for subsection, etc.) is stored as tuples in the "sections" field.

!!! m-default m-block "Subpages"
    - \subpage members

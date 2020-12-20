# JSON Output

This program outputs a single JSON file, which should be easy to convert into any representation
the user desires. The JSON file has the following format:
```json
{
   "members": [],
   "headers": [],
   "groups": [],
   "pages": []
}
```

## "members"

This is a list of everything that is defined at the global scope. Members are listed in order
in which they were found in the header file. Each `members[i]` is a dictionary as follows:
```json
{
   "id": "",           // this is a unique identifier used for referencing
   "name": "",         // name of the member
   "brief": "",        // brief description, in Markdown
   "doc": "",          // full documentation, in Markdown
   "sections": [],     // (ID, level) for sections in "doc"
   "anchors": [],      // IDs of anchors in "doc"
   "member_type": "",  // class/function/enum/variable/define/namespace/etc.
   "parent": "",       // ID of parent member
   "header": "",       // ID of the header file it is in (or the first one it is encountered in)
   "group": "",        // ID of the group it is in (or empty string)
   "deprecated": false // false or true

   "parameters": [],   // (if a function)
   "return_type": "",  // (if a function)
   "members": [],      // (if a class or namespace) recursively list members
   "related": [],      // (if a class) list of IDs of functions related to this class (`\relates` command)
   ...                 // other elements with additional information as needed ("virtual", "mutable", etc.)
}
```

Member IDs are not unrecognizable hash codes as Doxygen does it, but simply created from the fully
qualified name and parameters, guaranteeing uniqueness. For example:
 - `int ns::foo()`                     ⇒ `"ns-foo"`
 - `int ns::foo(int, double)`          ⇒ `"ns-foo-int--double-"`
 - `int ns::foo(int&, double const&)`  ⇒ `"ns-foo-int-L-double-CL"`
 - `class ns::bar`                     ⇒ `"ns-bar"`
 - `ns::bar::bar(float*)`              ⇒ `"ns-bar-bar-float-P"`

See `members.md` for more information on the dictionary fields for each of the types of members.

## "headers"

This is a list of files. Each `headers[i]` is a dictionary as follows:
```json
{
   "id": "",           // unique identifier
   "name": "",         // file name, with path from project root
   "brief": "",        // brief description, in Markdown
   "doc": "",          // full documentation, in Markdown
   "sections": [],     // (ID, level) for sections in "doc"
   "anchors": [],      // IDs of anchors in "doc"
   "includes": []      // list of files included by the header
}
```

We don't list what is defined in a file, this information can easily be gathered by iterating through
all members and finding the ones that list a file's ID.

Any directory structure to be shown in the documentation can be reconstructed from the file names,
it is not explicitly stored here.

## "groups"

A list of defined groups. Each `groups[i]` is a dictionary as follows:
```json
{
   "id": "",           // unique identifier
   "name": "",         // file name, with path from project root
   "brief": "",        // brief description, in Markdown
   "doc": "",          // full documentation, in Markdown
   "sections": [],     // (ID, level) for sections in "doc"
   "anchors": [],      // IDs of anchors in "doc"
   "parent": "",       // ID of the parent group, if any
   "subgroups": []     // list of IDs of child groups
}
```

Groups can be nested.

## "pages"

A list of pages. Each `pages[i]` is a dictionary as follows:
```json
{
   "id": "",           // unique identifier
   "title": "",        // file name, with path from project root
   "doc": "",          // full documentation, in Markdown
   "sections": [],     // (ID, level) for sections in "doc"
   "anchors": [],      // IDs of anchors in "doc"
   "parent": "",       // ID of the parent page, if any
   "subpages": []      // list of IDs of child pages
}
```

One page has the ID 'index', this is the main page, and the root of the hierarchy.

## The "brief" and "doc" fields

Any Markdown in the documentation will not be parsed, this is something for the generator to do.
However, we will look for `\ref`, `\ingroup` and similar commands, as described in the `commands.md`
page.

Commands that create a link are replaced by the Markdown syntax for a link, linking to
`#<id>`. For example, `\ref foo::bar` will be replaced by `[foo::bar](#foo-bar)`, and
`\ref foo::bar "the bar value"` will be replaced by `[the bar value](#foo-bar)`. Note that
this is Markdown syntax to link to an anchor within the same page. The generator will have
to identify these and change them to links to another page if necessary (only the generator
will know what page the documentation for a given member is put in).

Other recognized commands will be similarly replaced with Markdown or removed, as appropriate.
Any command not listed in in the `commands.md` page will be left as-is.

## The "anchors" field

Documentation can contain anchors that can be referenced in the same way that members or pages
can be referenced. These are created with the command `\anchor`. This command is replaced with
appropriate Markdown syntax to create an anchor, and the anchor ID (the string that can be used
with `\ref` to link to the anchor) is listed in the "anchors" field. Where these anchors are
referenced, a Markdown link is generated as described in the section above. The generator will
need to modify this link to point to the right page. The "anchor" field gives the required
information to the generator for this.

## The "sections" field

In a similar fashion to anchors, documentation can also contain headers that can be referenced.
These are created with the commands `\section`, `\subsection` and `\subsubsection`. These commands
are replaced with the appropriate Markdown syntax, and the section ID and level (1 for section,
2 for subsection, etc.) is stored as tuples in the "sections" field.
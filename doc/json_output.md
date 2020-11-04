Dox++
===

This is an alternative to Doxygen.
It uses Clang to parse headers. This is through code modified from cldoc (https://github.com/jessevdk/cldoc)
By using that code, this project must be GPL-2.0.
The comment syntax is closer to Doxygen's than cldoc's. But I don't want to copy all the Doxygen crazy, just
the useful and good bits. We can change things around if they're not suitable.

Doxygen makes a mess of its XML output.

This program outputs a single JSON file, which should be easy to convert into any representation
the user desires. A few accompanying programs demonstrate that: one produces HTML, one produces a PDF.

The JSON file has the following format:
{
   "members": [],
   "headers": [],
   "groups": [],
   "pages": []
}

## members
This is a list of everything that is defined at the global scope. Members are listed in order
in which they were found in the header file. Each `members[i]` is a dictionary as follows:
{
   "id": "",           // this is a unique identifier used for referencing
   "name": "",         // name of the member
   "brief": "",        // brief description, in Markdown
   "doc": "",          // full documentation, in Markdown
   "member_type": "",  // class/function/enum/variable/define/namespace/etc.
   "parent": "",       // ID of parent member
   "file": "",         // ID of the file it is in (for namespaces, the first one it is encountered in)
   "group": "",        // ID of the group it is in (or empty string)
   "deprecated": false // false or true

   "parameters": [],   // (if a function)
   "return": "",       // (if a function)
   "members": [],      // (if a class or namespace) recursively list members
   "related": [],      // (if a class) list of ids of functions related to this class (`\relates` command)
   ...                 // other elements with additional information as needed ("virtual", "mutable", etc.)
}

Member IDs are not unrecognizable hash codes as Doxygen does it, but simply created from the fully
qualified name and parameters, guaranteeing uniqueness. For example:
 - int ns::foo()                     => 'ns-foo'
 - int ns::foo(int, double)          => 'ns-foo-int--double-'
 - int ns::foo(int&, double const&)  => 'ns-foo-int-L-double-CL'
 - class ns::bar                     => 'ns-bar'
 - ns::bar::bar(float*)              => 'ns-bar-bar-float-P'

See `members.md` for more information on the dictionary fields for each of the types of members.

## headers
This is a list of files. Each `headers[i]` is a dictionary as follows:
{
   "id": "",           // unique identifier
   "name": "",         // file name, with path from project root
   "brief": "",
   "doc": "",
   "includes": []      // list of files included by the header
}

We don't list what is defined in a file, this information can easily be gathered by iterating through
all members and finding the ones that list a file's ID.

Any directory structure to be shown in the documentation can be reconstructed from the file names,
it is not explicitly stored here.

## groups
A list of defined groups. Each `groups[i]` is a dictionary as follows:
{
   "id": "",           // unique identifier
   "name": "",         // file name, with path from project root
   "brief": "",
   "doc": "",
   "parent": "",       // ID of the parent group, if any
   "subgroups": []     // list of ids of child groups
}

Groups can be nested.

## pages
A list of pages. Each `pages[i]` is a dictionary as follows:
{
   "id": "",           // unique identifier
   "title": "",        // file name, with path from project root
   "doc": "",
   "subpages": []      // list of ids of child pages
}

One page has the ID 'index', this is the main page, and the root of the hierarchy.

---

Any Markdown in the documentation will not be parsed, this is something for the generator to do.
However, we will look for `\ref`, `\ingroup` and similar commands, as described in the `commands.md`
page. Commands that create a link are replaced by the Markdown syntax for a link, linking to
`#<id>`. For example, `\ref foo::bar` will be replaced by `[foo::bar](#foo-bar)`, and
`\ref foo::bar "the bar value"` will be replaced by `[the bar value](#foo-bar)`. Note that

of text with a Markdown-style link: `[foo.bar](#ns.foo.bar)`. Note that this is the same formatting
used to link to Markdown headers and such. The generator will have to identify these and change
them to links to another page if necessary (only the generator will know where the documentation
for a given member is).

Also `@cmd` and `\cmd` will be found, and acted upon if necessary. For example, `\warning` will remain
unchanged, the generator needs to take care of that; but `\ingroup` will set the `group` value of the member,
and be removed from the Markdown block.

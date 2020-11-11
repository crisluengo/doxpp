# Commands

Commands can start with `\\` or `@`. Here we show the `\\` variant only.

Note that we try to keep compatibility with Doxygen, but chose to make some changes:

1. Documenting a function, variable or typedef with `\fn`, `\var`, `\typedef` doesn't
   take a declaration, only a name. The declaration is always taken from the sources.
   You cannot document non-existing things.

2. Documenting a preprocessor macro with `\def` (new better name: `\macro`) must always
   carry the macro name. Clang doesn't preserve preprocessor directives in its AST.

3. Grouping has changed: We don't recognize `\{` and `\}`. Instead, `\defgroup` and
   `\addtogroup` imply the opening `\{`. The closing `\}` must be replaced by
    `\endgroup`. Furthermore, groups are disjoint, each member can only belong to
    one group.

4. There is no "autolink", all member names must be preceded by the `\ref` command
   to create a link to the member documentation. `\ref` is used to link to anything
   in the documentation, not just pages and sections.

5. All Doxygen commands related to markup are not recognized. Any non-recognized
   command is kept in the output JSON file, so that the backend can act on it if it
   desires. It is typically simpler to use Markdown syntax for markup anyway.
   It is also possible to use HTML tags for markup, if the backend can handle it.

Note that commands are recognized and processed outside of any Markdown parsing, so
commands inside of backticks or code fences are processed the same way as outside
of them.


## At the start of a documentation block

These define what the documentation block does. The first line of the block must start
with one of these commands, otherwise it will be associated to the next declaration
(or previous if it starts with `<`).

### `\addtogroup <name>`

Sets `id` as the active group. It does not matter if the group is not yet defined or not.
If no matching `\defgroup` exists in the project, the group will not be documented, but will
exist. Must be matched by a `endgroup`.

See `defgroup` for more information on grouping.

The remainder of the comment block is ignored.

### `\alias <name>` (or `\typedef <name>`)

Documents an alias declared in the headers with `using` or `typedef`. The declaration must actually
exist. `<name>` is the fully qualified name of the alias, or, if not fully qualified, the alias
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched alias.

`\typedef` is an alias for compatibility with Doxygen.

### `\class <name>`, `\class <id>`

Documents a class declared in the headers with `class`. The declaration must actually
exist. `<name>` is the fully qualified name of the class, or, if not fully qualified, the class
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched class.

Alternatively, provide the ID for the class.

### `\defgroup <name> [<title>]`

Defines a group. Namespace members can be part of one group. A generator can sort members by group,
instead (or additionally) to sorting them by namespace or file.

Members declared after the `\defgroup` command are part of the group. The `\defgroup` makes
the newly defined group "active", and will remain so until the end of the file, or until
a `\endgroup` command.

Documentation blocks that document members declared elsewhere are also affected by the "active" group,
but only if the member declaration didn't already associate the member to a group. A `\ingroup`
command in a documentation block has priority when assigning members to groups. Only the first
such command is considered, the rest is ignored.

Groups can be nested. Each group has at most one parent, and can have any number of subgroups.
When defining a group while another group is active, the group will be a subgroup of the active
group, and then become the active group. The `\ingroup` command provides an alternative to
defining the group hierarchy. Note that cycles in the group hierarchy are prohibited. Group
A cannot be both an ancestor and a descendant of another group.

`\endgroup` causes the previously active group to become active again. It is required to
have one of these for each `defgroup` and each `addtogroup`.

`id` is the unique identifier for the group.

`name` is the name for the group, everything after the `id` and until the first newline
is considered the `name`.

The remainder of the comment block is the documentation, the first line being the "brief"
string.

A second `\defgroup` encountered with the same `id` will add documentation to the group,
but the `name` and `brief` string will be ignored. Thus, multiple `\defgroup` commands
can co-exist, but only the first one encountered can set the `name` and `brief` strings.

### `\dir [<path fragment>]`

Currently not implemented

Do we need to implement this? Is it useful?

### `\endgroup`

See `\defgroup`.

### `\endname`

See `\name`.

### `\enum <name>`, `\enum <id>`

Documents an enumerator declared in the headers with `enum` or `enum class`. The declaration must actually
exist. `<name>` is the fully qualified name of the enumerator, or, if not fully qualified, the enumerator
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched enumerator.

Alternatively, provide the ID for the enumerator.

### `\file [<name>]`

Adds documentation for the current file, or a different file if the file name is given.
The rest of the comment block is considered documentation.
```
/// \file
/// This is the brief description for the current file.
/// This is the detailed description right here.
```

### `\function <name>`, `\function <id>` (`\fn` is an alias)

Documents a function or class method declared in the headers. The declaration must actually
exist. `<name>` is the fully qualified name of the function, or, if not fully qualified, the function
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched function.

To disambiguate overloaded functions, provide in `<name>` the argument list types, for example:
```
/// \function namesp::funcname(int, double*)
```

Alternatively, provide the ID for the function.

`\fn` is an alias for compatibility with Doxygen.

### `\macro <name>` (or `\def <name>`)

The only way of documenting preprocessor macros, as Clang doesn't report on the work of
the preprocessor (well, it's possible, but it makes things a lot more complex).

If you want to show the full definition of the macro, write about it in your documentation.
We feel that usually it is not useful to show how a macro is defined.

Because Clang doesn't report where the macro is defined, we take the file where this
documentation block lives as the include file for the macro. Therefore, you should always
put this command in the same file where the macro is actually defined.

TODO: Maybe eventually `\headerfile` can be used to indicate which header the macro is defined in.

`\def` is an alias for compatibility with Doxygen.

### `\mainpage [(title)]`

Creates a page with the ID `index`, and `(title)` as the page's title. This is the start page
for the documentation. Text in this block is the page's text. See `\page` for more information.

### `\name (header)`

Similar to `\defgroup` or `\addtogroup`, but for class or struct members.  The `(header)` text
is used to label the group in the documentation. Each `\name` command closes the previous
group and starts a new one. Use `\endname` rather than `\endgroup` to close off the group.

Unlike with the `\defgroup` and `\addtogroup` commands, `\name` and `\endname` must enclose the
declaration of the class or struct members, not their documentation blocks.

These groups cannot be nested, so a `\name` command will close a previous member group. `\endname`
is only needed at the end of a class, or before the declaration of members that should not be
in any group.

The parser is not very clever, and so a class/struct member group remains active in the remainder
of the file until `\endname` is encountered, even within other classes.

It is not possible to reference these groups.
The backend can choose to group class or struct members by access (private/protected/public), or
by `\name` grouping, or both.

### `\namespace <name>`, `\namespace <id>`

Documents a namespace declared in the headers. The declaration must actually exist. `<name>` is the
fully qualified name of the namespace, or, if not fully qualified, the namespace with the "best"
match is assumed ("best" means that the fewest number of scopes have to be prepended to make the
match). In case of ambiguity, the first match is chosen. A warning is produced if `<name>` is not
the fully qualified name of the matched namespace.

Alternatively, provide the ID for the namespace.

### `\page <name> (title)`

Creates a page with `<name>` as ID and `(title)` as the title. Text in this block is the page's text.
The page can be referenced by its ID.

Use `\subpage` commands in a page to reference other pages and make those referenced pages sub-pages to
this page. Use `\ref` commands to reference other pages but not impose any hierarchy.

By default, all pages are at the same level, not subordinate to any other page.

### `\struct <name>`, `\struct <id>`

Documents a struct declared in the headers. The declaration must actually exist.
`<name>` is the fully qualified name of the struct, or, if not fully qualified, the struct
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched struct.

Alternatively, provide the ID for the struct.

### `\union <name>`, `\union <id>`

Documents a union or constant declared in the headers. The declaration must actually exist.
`<name>` is the fully qualified name of the union, or, if not fully qualified, the union
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched union.

Alternatively, provide the ID for the union.

### `\variable <name>`, `\variable <id>` (`\var` is an alias)

Documents a variable or constant declared in the headers. The declaration must actually exist.
`<name>` is the fully qualified name of the variable, or, if not fully qualified, the variable
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched variable.

Alternatively, provide the ID for the variable.

`\var` is an alias for compatibility with Doxygen.


## Inside documentation blocks

### `\anchor <name>`

Anywhere in a documentation block, adds an anchor that can be referenced elsewhere with `\ref`.

Is replaced by `{#<name>}` in the Markdown output.

### `\brief`

Used at the beginning of the first line of a comment block, turns the first paragraph into the "brief" string.
```
/// \brief This is a rather long brief descrition
/// of the member below.
///
/// This is the detailed description right here.
/// Note the empty line that separates paragraphs.
int foo;
```

### `\ingroup <name>`

If this appears in the comment block for a namespace member, the member will become part of the
group listed. It can also appear in the comment block of a group, to nest groups.

`\ingroup` overrules the group name of the enclosing `\defgroup`/`\endgroup` or
`\addtogroup`/`\endgroup`.

See `\defgroup` for more information on grouping.

This command is expected to be on its own on a line.

### `\ref <name> ["(text)"]`

Creates a link to the entity (member, header, group or page) called `<name>`. Optionally,
the link text can be set to `text`. If left out, the link text will be the tile of the page
or the name of the member referenced.

`<name>` will be looked up according to logical rules: in the documentation for `ns::foo`,
`\ref bar` will see if `ns::foo::bar` exists, otherwise it will look for `ns::bar`, or
finally `::bar`. If no match exists, `<name>` will be interpreted as an ID. Use the ID
to link to a member, a header, a group, a page, a section or an anchor. If `<name>` does not
match any IDs either, then `<name>` (or `(text)`) will be output without linking to anything.
In a page, always use the fully qualified name for members, or their ID.

If `bar` is a function with multiple overloads, then `\ref bar` will match the first function with that name.
To disambiguate overloaded functions, `<name>` should be the full function declaration,
without parameter names, and the types must match exactly. For example, `\ref bar(int, double const&)`
will match a function `bar(int, double const&)`, but not `bar(int, double const)` nor
`bar(int, double&)` nor `bar(int, double const&, int)`.

To link to a header file, give its ID, or specify the file name (optionally with a partial path)
in quotes, for example `\ref "path/header.h" "link text"`. When giving a file name, the header
with a matching name and the fewest path elements prepended will be linked to. The link text,
if not given explicitly, is the header file name with path starting at the project root
(as specified in the options).

### `\relates <name>` or `\related <name>`

Added to the documentation block of a function or variable, and with `<name>` referencing
a class, adds the function or variable to a "Related" section in the class' documentation.

Note that this command should not be placed in class, struct, union or enum members, only
in namespace members (including global scope).

This command is expected to be on its own on a line. Each member can only have one `\relates`
command.

### `\section <name> (title)`

Starts a new section within a documentation block or a page. `<name>` is the ID that can
be used with `\ref` to reference the section.

This is replaced by the Markdown code `# (title) {#name}`. The `#` represents a level 1 heading,
but this will be demoted by the backend to be a lower level than the containing block.

One can also directly write `# My Title {#my-title}`, but then the `\ref` command will not recognize
`my-title` as something that can be referenced.

### `\see <name> [, <name> [, ...]` or `\sa <name> [, <name> [, ...]`

Starts a paragraph with a "See also" header linking the given entities (members, headers, groups, pages).
See `\ref` for how `<name>` is interpreted and disambiguated.

Note that this inserts a `\par See also` command that the backend must interpret to create the heading,
and optionally box the whole paragraph.

This command is expected to be on its own on a line. Cannot occur inside the brief description.

### `\subpage <name> ["(text)"]`

This is similar to `\ref`, but for pages. It can only occur inside a page (see `\page`).
`\subpage <name>` creates a link to page `<name>` and additionally builds a hierarchy
structure, indicating that the linked page is subordinate to the current page. Only
one `\subpage` command can reference each page, such that each page has only one "parent"
page. Furthermore, these references should not form loops, the page hierarchy must form
a tree structure.

The page called `index` (see `\mainpage`) should not be made a subpage of another page.

`\subpage <name> "(text)"` uses `(text)` as the anchor text for the link.

To create links without creating hierarchical relations, use `\ref`.

### `\subsection <name> (title)`

Like `\section`, but for a level 2 heading (`##` in Markdown).

### `\subsubsection <name> (title)`

Like `\section`, but for a level 3 heading (`###` in Markdown).


## At the start of a line in Markdown files only

### `\comment`

The rest of the line is ignored. Use this to add comments not meant to be shown in the
documentation, file copyright notices, etc.


---

## Doxygen commands that will not be implemented

### Because the information is always retrieved from the code

- `\extends`
- `\implements`
- `\memberof`
- `\private`
- `\privatesection`
- `\protected`
- `\protectedsection`
- `\public`
- `\publicsection`
- `\pure`
- `\static`

### Because it doesn't apply to C++

- `\idlexcept` -> IDL only
- `\interface`
- `\package` -> Java only
- `\property`
- `\protocol` -> Objective-C only
- `\vhdlflow` -> VHDL only

### Because it doesn't make sense to me

- `\callergraph`
- `\callgraph`
- `\cond` / `\endcond` -> dude, just don't document if you don't want it documented...
- `\hidecallergraph`
- `\hidecallgraph`
- `\hideinitializer` -> this is something that the backend can do
- `\hiderefby`
- `\hiderefs`
- `\internal` / `\endinternal`
- `\link` / `\endlink` -> we're using `\ref` for everything
- `\overload [(function declaration)]`
- `\relatedalso <name>`
- `\relatesalso <name>`
- `\showinitializer` -> this is something that the backend can do
- `\showrefby`
- `\showrefs`
- `\weakgroup`
- `\{` -> is implicit in dox++
- `\}` -> we use `\endgroup` instead

### All the stuff that is related to markup, which we delegate to the backend

(There might be some other stuff in here that I missed?)

- `\a`
- `\addindex`
- `\arg`
- `\attention`
- `\author`
- `\authors`
- `\b`
- `\brief`
- `\bug`
- `\c`
- `\category`
- `\cite`
- `\code` / `\endcode`
- `\copybrief`
- `\copydetails`
- `\copydoc`
- `\copyright`
- `\date`
- `\deprecated`
- `\details`
- `\diafile`
- `\docbookinclude`
- `\docbookonly` / `\enddocbookonly`
- `\dontinclude`
- `\dot` / `\enddot`
- `\dotfile`
- `\e`
- `\em`
- `\emoji`
- `\exception`
- `\f$`
- `\f[` / `\f]`
- `\f{` / `\f}`
- `\htmlinclude`
- `\htmlonly` / `\endhtmlonly`
- `\if` / `\ifnot` / `\elseif` / `\else` / `\endif`
- `\image`
- `\include`
- `\includedoc`
- `\includelineno`
- `\invariant`
- `\latexinclude`
- `\latexonly` / `\endlatexonly`
- `\li`
- `\line`
- `\maninclude`
- `\manonly` / `\endmanonly`
- `\msc` / `\endmsc`
- `\mscfile`
- `\n`
- `\note`
- `\p`
- `\par`
- `\paragraph`
- `\param`
- `\parblock` / `\endparblock`
- `\post`
- `\pre`
- `\refitem`
- `\remark`
- `\remarks`
- `\result`
- `\return`
- `\returns`
- `\retval`
- `\rtfinclude`
- `\rtfonly` / `\endrtfonly`
- `\secreflist` / `\endsecreflist`
- `\short`
- `\since`
- `\skip`
- `\skipline`
- `\snippet`
- `\snippetdoc`
- `\snippetlineno`
- `\startuml` / `\enduml`
- `\tableofcontents`
- `\test`
- `\throw`
- `\throws`
- `\todo`
- `\tparam`
- `\until`
- `\verbatim` / `\endverbatim`
- `\verbinclude`
- `\version`
- `\warning`
- `\xmlinclude`
- `\xmlonly` / `\endxmlonly`
- `\xrefitem`
- `\$`
- `\@`
- `\\`
- `\&`
- `\~`
- `\<`
- `\=`
- `\>`
- `\#`
- `\%`
- `\"`
- `\.`
- `\::`
- `\|`
- `\--`
- `\---`

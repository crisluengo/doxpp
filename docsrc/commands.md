\page commands Documentation commands

This page describes the commands recognized by **dox++parse**. Commands can start with `\` or `@`.
Here we show the `\` variant only, but you can use the other variant if you prefer.

We try to keep only partial compatibility with Doxygen, see \ref doxygen_differences.

!!! note
    Commands are recognized and processed outside of any Markdown parsing, so
    commands inside of backticks or code blocks are processed the same way as outside
    of them.


\section commands_start_block At the start of a documentation block

These define what the documentation block does. The first line of the block must start
with one of these commands, otherwise it will be associated to the next declaration
(or previous if it starts with `<`).

\subsection command_addtogroup `\addtogroup`

    \‍addtogroup <name>

Sets `<name>` as the active group. If the group is not defined, a new group will be created
with no name and no documentation. Use `\group` to name and document the group.
Must be matched by a `endgroup`.

`\addtogroup` can also be used at the end of a `\group` documentation block. In this
case it must not have a `<name>` parameter.

See \ref grouping for more information on grouping.

The remainder of the comment block is ignored.

\subsection command_alias `\alias`

    \‍alias <name>
    \‍typedef <name>

Documents an alias declared in the headers with `using` or `typedef`. The declaration must actually
exist. `<name>` is the fully qualified name of the alias, or, if not fully qualified, the alias
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched alias.

`\typedef` is an alias for compatibility with Doxygen.

\subsection command_class `\class`

    \‍class <name>
    \‍class <id>

Documents a class declared in the headers with `class`. The declaration must actually
exist. `<name>` is the fully qualified name of the class, or, if not fully qualified, the class
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched class.

Alternatively, provide the ID for the class.

\subsection command_dir `\dir`

    \‍dir [<path fragment>]

**dox++** doesn't document directories. This Doxygen command is recognized and a warning
message is produced.

\subsection command_endgroup `\endgroup`

Closes the nearest previous `\addtogroup`.
See \ref grouping for more information.

\subsection command_endname `\endname`

See \ref command_name.

\subsection command_enum `\enum`

    \‍enum <name>
    \‍enum <id>

Documents an enumerator declared in the headers with `enum` or `enum class`. The declaration must actually
exist. `<name>` is the fully qualified name of the enumerator, or, if not fully qualified, the enumerator
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched enumerator.

Alternatively, provide the ID for the enumerator.

\subsection command_file `\file`

    \‍file [<name>]

Adds documentation for the current file, or a different file if the file name is given.
The rest of the comment block is considered documentation.
```cpp
/// \file
/// This is the brief description for the current file.
/// This is the detailed description right here.
```

\subsection command_function `\function`

    \‍function <name>
    \‍function <id>
    \‍fn <name>
    \‍fn <id>

Documents a function or class method declared in the headers. The declaration must actually
exist. `<name>` is the fully qualified name of the function, or, if not fully qualified, the function
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched function.

To disambiguate overloaded functions, provide in `<name>` the argument list types, for example:
```cpp
/// \function namesp::funcname(int, double*)
```

Alternatively, provide the ID for the function.

`\fn` is an alias for compatibility with Doxygen.

\subsection command_group `\group`

    \‍group <name> [<title>]
    \‍defgroup <name> [<title>]

Documents a group.

`<name>` is the unique identifier for the group.

`<title>` is the title for the group, everything after the `<name>` and until the first newline
is considered the title.

The remainder of the comment block is the documentation, the first line being the "brief"
string.

A second `\group` command encountered with the same `id` will add documentation to the group,
but the `name` and `brief` string will be ignored. Thus, multiple `\group` commands
can co-exist, but only the first one encountered can set the `name` and `brief` strings.

The documentation group can end with `\addtogroup`, in which case the group with ID `<name>`
will become active.

`\defgroup` is an alias for compatibility with Doxygen, even tough the command is used
somewhat differently.

See \ref grouping for more information on grouping.

\subsection command_macro `\macro`

    \‍macro <name>
    \‍def <name>

The only way of documenting preprocessor macros, as Clang doesn't report on the work of
the preprocessor (well, it's possible, but it makes things a lot more complex).

`<name>` can contain the argument list in parenthesis, but doesn't need to. For example:
```cpp
/// \macro FOO
#define FOO(a)
/// \macro BAR(b)
# define BAR(b)
```
The backend has the option of showing `b` as the argument to macro `BAR`, but will not
know anything about `a`, the argument to macro `FOO`.

Because Clang doesn't report where the macro is defined, we take the file where this
documentation block lives as the include file for the macro. Therefore, you should always
put this command in the same file where the macro is actually defined.

**TODO:** Maybe eventually `\headerfile` can be used to indicate which header the macro is defined in.

`\def` is an alias for compatibility with Doxygen.

\subsection command_mainpage `\mainpage`

    \‍mainpage [<title>]

Creates a page with the ID `index`, and `<title>` as the page's title. This is the start page
for the documentation. Text in this block is the page's text. See `\page` for more information.

\subsection command_name `\name`

    \‍name <header>

Creates a group for class or struct members.  The `<header>` text
is used to label the group in the documentation. Each `\name` command closes the previous
group and starts a new one. Use `\endname` to close off the group without starting a new one.

Any members declared in between a `\name` and the next `\name` or `\endname` belong to the
group introduced by that first `\name` command.

Unlike with the `\addtogroup` command, `\name` and `\endname` must enclose the declaration
of the class or struct members, not their documentation blocks.

The parser is not very clever, and so a class/struct member group remains active in the remainder
of the file until `\endname` is encountered, even within other classes.

It is not possible to reference these groups.
The backend can choose to group class or struct members by access (private/protected/public), or
by `\name` grouping, or both.

\subsection command_namespace `\namespace`

    \‍namespace <name>
    \‍namespace <id>

Documents a namespace declared in the headers. The declaration must actually exist. `<name>` is the
fully qualified name of the namespace, or, if not fully qualified, the namespace with the "best"
match is assumed ("best" means that the fewest number of scopes have to be prepended to make the
match). In case of ambiguity, the first match is chosen. A warning is produced if `<name>` is not
the fully qualified name of the matched namespace.

Alternatively, provide the ID for the namespace.

\subsection command_page `\page`

    \‍page <name> <title>

Creates a page with `<name>` as ID and `<title>` as the title. Text in this block is the page's text.
The page can be referenced by its ID.

Use `\‍subpage` commands in a page to reference other pages and make those referenced pages sub-pages to
this page. Use `\‍ref` commands to reference other pages but not impose any hierarchy.

By default, all pages are at the same level, not subordinate to any other page.

\subsection command_struct `\struct`

    \‍struct <name>
    \‍struct <id>

Documents a struct declared in the headers. The declaration must actually exist.
`<name>` is the fully qualified name of the struct, or, if not fully qualified, the struct
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched struct.

Alternatively, provide the ID for the struct.

\subsection command_union `\union`

    \‍union <name>
    \‍union <id>

Documents a union or constant declared in the headers. The declaration must actually exist.
`<name>` is the fully qualified name of the union, or, if not fully qualified, the union
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched union.

Alternatively, provide the ID for the union.

\subsection command_variable `\variable`

    \‍variable <name>
    \‍variable <id>
    \‍var <name>
    \‍var <id>

Documents a variable or constant declared in the headers. The declaration must actually exist.
`<name>` is the fully qualified name of the variable, or, if not fully qualified, the variable
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched variable.

Alternatively, provide the ID for the variable.

`\var` is an alias for compatibility with Doxygen.


\section commands_inside Inside documentation blocks

\subsection command_anchor `\‍anchor`

    \‍anchor <name>

Anywhere in a documentation block, adds an anchor that can be referenced elsewhere with `\‍ref`.

The `\anchor` command must happen at the end of a paragraph or in a paragraph of its own,
in either case it references the preceding paragraph. The paragraph is assigned the `#<name>`
attribute.

\subsection command_brief `\brief`

Used at the beginning of the first line of a comment block, turns the first paragraph into the "brief" string.
```cpp
/// \brief This is a rather long brief description
/// of the member below.
///
/// This is the detailed description right here.
/// Note the empty line that separates paragraphs.
int foo;
```

`\short` is an alias.

\subsection command_ingroup `\ingroup`

    \ingroup <name>

If this appears in the comment block for a namespace member, the member will become part of the
group listed. It can also appear in the comment block of a group, to nest groups.

`\ingroup` overrules the group name of the enclosing `\addtogroup`/`\endgroup`.

See \ref grouping for more information on grouping.

This command is expected to be on its own on a line.

\subsection command_n `\‍n`

Inserts a line break. The Markdown for a line break is two spaces at the end of a line.
Because many code editors automatically remove such spaces, use this command instead.
It will be replaced by two spaces, and a newline will be added if it's not there already.

\subsection command_ref `\‍ref`

    \‍ref <name> ["<text>"]
    \‍ref "<name>" ["<text>"]

Creates a link to the entity (member, header, group or page) called `<name>`. Optionally,
the link text can be set to `<text>`. If left out, the link text will be the tile of the page
or the name of the member referenced.

`<name>` will be looked up according to logical rules: in the documentation for `ns::foo`,
`\‍ref bar` will see if `ns::foo::bar` exists, otherwise it will look for `ns::bar`, or
finally `::bar`. If no match exists, `<name>` will be interpreted as an ID. Use the ID
to link to a member, a header, a group, a page, a section or an anchor. If `<name>` does not
match any IDs either, then `<name>` (or `<text>`) will be output without linking to anything.
In a page, always use the fully qualified name for members, or their ID.

If `bar` is a function with multiple overloads, then `\‍ref bar` will match the first function with that name.
To disambiguate overloaded functions, `<name>` should be the full function declaration,
without parameter names, and the types must match exactly. For example, `\‍ref bar(int, double const&)`
will match a function `bar(int, double const&)`, but not `bar(int, double const)` nor
`bar(int, double&)` nor `bar(int, double const&, int)`.

To link to a header file, give its ID, or specify the file name (optionally with a partial path)
in quotes, for example `\‍ref "path/header.h" "link text"`. When giving a file name, the header
with a matching name and the fewest path elements prepended will be linked to. The link text,
if not given explicitly, is the header file name with path starting at the project root
(as specified in the options).

Quotes around `<name>` are also required if the member is a function that overloads an operator,
since operators contain characters that are otherwise not seen as part of `<name>`. For example,
`\‍ref operator==` will see the `==` as not being part of `<name>`, and will try to find a member
called `operator` (which is an illegal member name, since it's a reserved keyword in C++). Instead,
use `\‍ref "operator=="`.

Finally, if a link must be immediately followed by a character that is considered part of `<name>`
by the parser, one can use quotes to disambiguate: `\‍ref foo--` would try to match "`foo--`" (maybe
as the ID of a function), whereas `\‍ref "foo"--` will correctly match "`foo`" and put two dashes
after the link.

When using quotes around `<name>`, the space between the closing quotes and the opening quotes
for `<text>` is mandatory. Two sequential quotes are considered part of an operator name,
such as in `\‍ref "operator""_w"`.

\subsection command_relates `\‍relates`

    \‍relates <name>
    \‍related <name>

Added to the documentation block of a function or variable, and with `<name>` referencing
a class, adds the function or variable to a "Related" section in the class' documentation.

Note that this command should not be placed in class, struct, union or enum members, only
in namespace members (including global scope).

This command is expected to be on its own on a line. Each member can only have one `\relates`
command.

\subsection command_section `\section`

    \section <name> <title>

Starts a new section within a documentation block or a page. `<name>` is the ID that can
be used with `\‍ref` to reference the section.

This is replaced by the Markdown code `# <title> {#name}`. The `#` represents a level 1 heading,
but this will be demoted by the backend to be a lower level than the containing block.

One can also directly write `# My Title {#my-title}`, but then the `\‍ref` command will not recognize
`my-title` as something that can be referenced.

\subsection command_see `\‍see`

    \‍see <name> [, <name> [, ...]
    \‍sa <name> [, <name> [, ...]

Starts a paragraph with a "See also" header linking the given entities (members, headers, groups, pages).
See `\‍ref` for how `<name>` is interpreted and disambiguated.

Note that this inserts a `\par See also` command that the backend must interpret to create the heading,
and optionally box the whole paragraph.

This command is expected to be on its own on a line. Cannot occur inside the brief description.

\subsection command_subpage `\‍subpage`

    \‍subpage <name> ["<text>"]

This is similar to `\‍ref`, but for pages. It can only occur inside a page (see `\page`).
`\‍subpage <name>` creates a link to page `<name>` and additionally builds a hierarchy
structure, indicating that the linked page is subordinate to the current page. Only
one `\‍subpage` command can reference each page, such that each page has only one "parent"
page. Furthermore, these references should not form loops, the page hierarchy must form
a tree structure.

The page called `index` (see `\mainpage`) should not be made a subpage of another page.

`\‍subpage <name> "<text>"` uses `<text>` as the anchor text for the link.

To create links without creating hierarchical relations, use `\‍ref`.

\subsection command_subsection `\subsection`

    \subsection <name> <title>

Like `\section`, but for a level 2 heading (`##` in Markdown).

\subsection command_subsubsection `\subsubsection`

    \subsubsection <name> <title>

Like `\section`, but for a level 3 heading (`###` in Markdown).

\subsection command_not_yet_implemented Not yet implemented

- `\deprecated` (might be relevant for things that cannot be marked as such in source code)
- `\example`
- `\exception` / `\throw` / `\throws`
- `\headerfile`
- `\param`
- `\parblock` / `\endparblock`
- `\return` / `\returns` / `\result`
- `\since`
- `\tparam`

\section commands_start_of_line At the start of a line in Markdown files only

\subsection command_comment `\‍comment`

The rest of the line is ignored. Use this to add comments not meant to be shown in the
documentation, file copyright notices, etc.


---

\section commands_not_implemented Doxygen commands that will not be implemented

\subsection commands_not_implemented_illegal Because the information is always retrieved from the code

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

\subsection commands_not_implemented_notcpp Because it doesn't apply to C++

- `\category` (Objective-C only)
- `\idlexcept` (IDL only)
- `\interface`
- `\package` (Java only)
- `\property`
- `\protocol` (Objective-C only)
- `\retval`
- `\vhdlflow` (VHDL only)

\subsection commands_not_implemented_latex Because they're specific to LaTeX output

- `\addindex`
- `\cite`

\subsection commands_not_implemented_nonsensical Because it doesn't make sense with the **dox++** logic

- `\bug`
- `\callergraph`
- `\callgraph`
- `\cond` / `\endcond` (use an `#ifdef` conditional compilation to exclude things from the documentation)
- `\copybrief`
- `\copydetails`
- `\copydoc`
- `\hidecallergraph`
- `\hidecallgraph`
- `\hideinitializer`
- `\hiderefby`
- `\hiderefs`
- `\internal` / `\endinternal`
- `\link` / `\endlink` (we use `\‍ref` for everything)
- `\nosubgrouping`
- `\overload [(function declaration)]`
- `\refitem`
- `\relatedalso <name>`
- `\relatesalso <name>`
- `\secreflist` / `\endsecreflist`
- `\showinitializer`
- `\showrefby`
- `\showrefs`
- `\tableofcontents` (these are automatically generated by the default templates)
- `\todo`
- `\weakgroup`
- `\xrefitem`
- `\{` (use `\addtogroup` instead)
- `\}` (use `\endgroup` instead)

\subsection commands_not_implemented_markup All the stuff that is related to markup, use Markdown instead

(There might be some other stuff in here that I missed?)

- `\a`
- `\arg`
- `\attention`
- `\author`
- `\authors`
- `\b`
- `\c`
- `\code` / `\endcode`
- `\copyright`
- `\date`
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
- `\note`
- `\p`
- `\par`
- `\paragraph`
- `\post`
- `\pre`
- `\remark`
- `\remarks`
- `\rtfinclude`
- `\rtfonly` / `\endrtfonly`
- `\short`
- `\skip`
- `\skipline`
- `\snippet`
- `\snippetdoc`
- `\snippetlineno`
- `\startuml` / `\enduml`
- `\test`
- `\until`
- `\verbatim` / `\endverbatim`
- `\verbinclude`
- `\version`
- `\warning`
- `\xmlinclude`
- `\xmlonly` / `\endxmlonly`
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

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
`<name>` is not the fully qualified name of the matched member.

`\typedef` is an alias for compatibility with Doxygen.

### `\class <name>`

Documents a class declared in the headers with `class`. The declaration must actually
exist. `<name>` is the fully qualified name of the class, or, if not fully qualified, the alias
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched member.

### `\defgroup <name> [<title>]`

Defines a group. Members can be part of one group. A generator can sort members by group,
instead (or additionally) to sorting them by namespace or file.

Members declared after the `\defgroup` command are part of the group. The `\defgroup` makes
the newly defined group "active", and will remain so until the end of the file, or until
a `\endgroup` command.

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

### `\enum <name>`

Documents an enumerator declared in the headers with `enum` or `enum class`. The declaration must actually
exist. `<name>` is the fully qualified name of the enumerator, or, if not fully qualified, the alias
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched member.

### `\file [<name>]`

Adds documentation for the current file, or a different file if the file name is given.
The rest of the comment block is considered documentation.
```
/// \file
/// This is the brief description for the current file.
/// This is the detailed description right here.
```

### `\function <name>` (or `\fn <name>`)

Documents a function or class method declared in the headers. The declaration must actually
exist. `<name>` is the fully qualified name of the function, or, if not fully qualified, the alias
with the "best" match is assumed ("best" means that the fewest number of scopes have to be prepended
to make the match). In case of ambiguity, the first match is chosen. A warning is produced if
`<name>` is not the fully qualified name of the matched member.

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

### `\name (header)`

### `\namespace <name>`

### `\page <name> (title)`

### `\struct <name>`

### `\union <name>`

### `\variable <name>` (or `\var <name>`)

`\var` is an alias for compatibility with Doxygen.


## Inside documentation blocks

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

If this appears in the comment block for a member, the member will become part of the
group listed. It can also appear in the comment block of a group, to nest groups.

`\ingroup` overrules the group name of the enclosing `\defgroup`/`\endgroup` or
`\addtogroup`/`\endgroup`.

See `\defgroup` for more information on grouping.

This command is expected to be on its own on a line.

### `\subpage <name> ["(text)"]`

This is similar to `\ref`, but for pages. It can only occur inside a page (see `\page`).
`\subpage <name>` creates a link to page `<name>` and additionally builds a hierarchy
structure, indicating that the linked page is subordinate to the current page. Only
one `\subpage` command can reference each page, such that each page has only one "parent"
page. Furthermore, these references should not form loops, the page hierarchy must form
a tree structure. The page called `index` (see `\mainpage`) is the root of the hierarchy,
by default all other pages are subordinate to it.

To create links without creating hierarchical relations, use `\ref`.

### `\ref <name> ["(text)"]`

Creates a link to the entity (member or page) called `<name>`. Optionally, the link text
can be set to `text`. If left out, the link text will be the tile of the page or the
name of the member referenced.

`<name>` will be looked up according to logical rules: in the documentation for `ns::foo`,
`\ref bar` will see if `ns::foo::bar` exists, otherwise it will look for `ns::bar`, or
finally `::bar`. If no match exists, the `<name>` (or `(text)`) will be output without
linking to anything. In a page, always use the fully qualified name.

To disambiguate overloaded functions, `<name>` should be the full function declaration,
without parameter names, and the types must match exactly. For example, `\ref bar(int, double const&)`
will match a function `bar(int, double const&)`, but not `bar(int, double const)` nor
`bar(int, double&)` nor `bar(int, double const&, int)`


## At the start of a line in Markdown files only

### `\comment`

The rest of the line is ignored. Use this to add comments not meant to be shown in the
documentation, file copyright notices, etc.


---

# Doxygen commands, and what we'll do with them

## Grouping commands

- `\addtogroup <name>`
- `\defgroup <name> (group title)`
- `\name [(header)]`

## Documenting members without using the actual declaration in the header file

These should still point to things that the parser found, though. Or maybe if they
weren't found, add an indicator that this is indeed not implemented.

- `\class <name>`
- `\def <name>` -> We'll have an alias `\macro`
- `\dir [<path fragment>]`
- `\enum <name>`
- `\file [<name>]`
- `\fn (function declaration)` -> We'll have an alias `\function`
- `\mainpage [(title)]`
- `\namespace <name>`
- `\page <name> (title)`
- `\struct <name>`
- `\typedef (typedef declaration)` -> We'll have an alias `\alias`
- `\union <name>`
- `\var (variable declaration)` -> We'll have an alias `\variable`

## Inside a member documentation block

- `\example['{lineno}'] <file-name>`
- `\headerfile <header-file> [<header-name>]`
- `\ingroup <groupname>` -> But we'll do a single group here
- `\nosubgrouping`
- `\ref <name> ["(text)"]`
- `\related <name>`
- `\relates <name>`
- `\relatedalso <name>`
- `\relatesalso <name>`
- `\sa { references }` -> same as `\see`
- `\see { references }` -> same as `\sa`
- `\subpage <name> ["(text)"]` -> but this one happens only inside a `\page` documentation block

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
- `\cond` -> dude, just don't document if you don't want it documented...
- `\endcond`
- `\endinternal`
- `\hidecallergraph`
- `\hidecallgraph`
- `\hideinitializer` -> this is something that the backend can do
- `\hiderefby`
- `\hiderefs`
- `\internal`
- `\overload [(function declaration)]`
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
- `\anchor`
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
- `\code`
- `\copybrief`
- `\copydetails`
- `\copydoc`
- `\copyright`
- `\date`
- `\deprecated`
- `\details`
- `\diafile`
- `\docbookinclude`
- `\docbookonly`
- `\dontinclude`
- `\dot`
- `\dotfile`
- `\e`
- `\else`
- `\elseif`
- `\em`
- `\emoji`
- `\endcode`
- `\enddocbookonly`
- `\enddot`
- `\endhtmlonly`
- `\endif`
- `\endlatexonly`
- `\endlink`
- `\endmanonly`
- `\endmsc`
- `\endparblock`
- `\endrtfonly`
- `\endsecreflist`
- `\endverbatim`
- `\enduml`
- `\endxmlonly`
- `\exception`
- `\f$`
- `\f[`
- `\f]`
- `\f{`
- `\f}`
- `\htmlinclude`
- `\htmlonly`
- `\if`
- `\ifnot`
- `\image`
- `\include`
- `\includedoc`
- `\includelineno`
- `\invariant`
- `\latexinclude`
- `\latexonly`
- `\li`
- `\line`
- `\link`
- `\maninclude`
- `\manonly`
- `\msc`
- `\mscfile`
- `\n`
- `\note`
- `\p`
- `\par`
- `\paragraph`
- `\param`
- `\parblock`
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
- `\rtfonly`
- `\secreflist`
- `\section`
- `\short`
- `\since`
- `\skip`
- `\skipline`
- `\snippet`
- `\snippetdoc`
- `\snippetlineno`
- `\startuml`
- `\subsection`
- `\subsubsection`
- `\tableofcontents`
- `\test`
- `\throw`
- `\throws`
- `\todo`
- `\tparam`
- `\until`
- `\verbatim`
- `\verbinclude`
- `\version`
- `\warning`
- `\xmlinclude`
- `\xmlonly`
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

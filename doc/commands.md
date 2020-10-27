# Commands

Commands can start with `\\` or `@`. Here we show the `\\` variant only.

## `\brief`

Used on the first line of a comment block, turns the first paragraph into the "brief" string.
```
/// \brief This is a rather long brief descrition
/// of the member below.
///
/// This is the detailed description right here.
/// Note the empty line that separates paragraphs.
int foo;
```

## `\addtogroup <name>`

Sets `id` as the active group. It does not matter if the group is not yet defined or not.
If no matching `\defgroup` exists in the project, the group will not be documented, but will
exist. Must be matched by a `endgroup`.

See `defgroup` for more information on grouping.

The remainder of the comment block is ignored.

## `\defgroup <name> [<title>]`

Defines a group. Members can be part of one group. A generator can sort members by group,
instead (or additionally) to sorting them by namespace or file.

Members declared after the `\defgroup` command are part of the group. The `\defgroup` makes
the newly defined group "active", and will remain so until the end of the file, or until
a `\endgroup` command.

Groups can be nested. Each group has a parent and zero or more subgroups. When defining
a group while another group is active, the group will be a subgroup of the active group,
and then become the active group. 

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

## `\endgroup`

See `\defgroup`.

## `\file [<name>]`

Adds documentation for the current file. Should be at the beginning of a comment block.
The rest of the comment block is considered documentation.
```
/// \file
/// This is the brief description for the current file.
/// This is the detailed description right here.
```

## `\ingroup <name>`

If this appears in the comment block for a member, the member will become part of the
group listed. It can also appear in the comment block of a group, to nest groups.

`\ingroup` overrules the group name of the enclosing `\defgroup`/`\endgroup` or
`\addtogroup`/`\endgroup`.

---

## Documenting members without using the actual declaration in the header file

These should still point to things that the parser found, though. Or maybe if they
weren't found, add an indicator that this is indeed not implemented.

- `\addtogroup <name>`
- `\class <name>`
- `\def <name>`
- `\defgroup <name> (group title)`
- `\dir [<path fragment>]`
- `\enum <name>`
- `\example['{lineno}'] <file-name>`
- `\file [<name>]`
- `\fn (function declaration)`
- `\mainpage [(title)]`
- `\name [(header)]` -> for member groups, we'll rename this
- `\namespace <name>`
- `\overload [(function declaration)]`
- `\page <name> (title)`
- `\struct <name>`
- `\typedef (typedef declaration)`
- `\union <name>`
- `\var (variable declaration)`

## Inside a member documentation block 

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
- `\subpage <name> ["(text)"]` -> but this one doesn't happens only inside a `\page` documentation block

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

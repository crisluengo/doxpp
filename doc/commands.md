# Commands

Commands can start with `\\` or `@`. Here we show the `\\` variant only.

## \brief 

Used on the first line of a comment block, turns the first paragraph into the "brief" string.
```
/// \brief This is a rather long brief descrition
/// of the member below.
///
/// This is the detailed description right here.
/// Note the empty line that separates paragraphs.
int foo;
```

## \file

Adds documentation for the current file. Should be at the beginning of a comment block.
The rest of the comment block is considered documentation.
```
/// \file This is the brief description for the current file.
/// This is the detailed description right here.
```
or:
```
/// \file
/// This is the brief description for the current file.
/// This is the detailed description right here.
```

## \defgroup id name

Defines a group. Members can be part of one group. A generator can sort members by group,
instead (or additionally) to sorting them by namespace or file.

Members declared after the `\defgroup` command are part of the group. The `\defgroup` makes
the newly defined group "active", and will remain so until the end of the file, or until
a `\endgroup` command.

Groups can be nested. Each group has a parent and zero or more subgroups. When defining
a group while another group is active, the group will be a subgroup of the active group,
and then become the active group. 

`\endgroup` causes the parent of the active group to become active.

`id` is the unique identifier for the group.

`name` is the name for the group, everything after the `id` and until the first newline
is considered the `name`.

The remainder of the comment block is the documentation, the first line being the "brief"
string.

A second `\defgroup` encountered with the same `id` will add documentation to the group,
but the `name` and `brief` string will be ignored. Thus, multiple `\defgroup` commands
can co-exist, but only the first one encountered can set the `name` and `brief` strings.

## \addtogroup id

Sets `id` as the active group. It does not matter if the group is not yet defined or not.
If no matching `\defgroup` exists in the project, the group will not be documented, but will
exist.

The remainder of the comment block is ignored.

Cannot be used while another group is active.

## \endgroup

See `\defgroup`.

## \ingroup id [, id [...]]

If this appears in the comment block for a member, the member will become part of the
group or groups listed. It can not appear in the comment block for a group.

Groups can only have one parent group. 

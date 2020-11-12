# Grouping namespace members

Namespace members can be assigned to one group. If assigned to a group, the
backend can choose to document those members in the group's page rather
than the namespace's page. Alternatively, the backend can index members
by their group.

Groups can be nested, forming a tree structure. That is, it is not legal
to form loops (a group being both an ancestor and a descendant of another
group) nor to assign two parent groups to one group. Groups are assigned
to a parent group just like a namespace member is.

A group can be documented using the `\defgroup` command.

Members can be assigned to a group in one of two ways:

1. Using the `\ingroup` command in the documentation block. Each documentation
block can have one of these commands (others will be ignored).

2. By enclosing the member's declaration or documentation block in between
a pair of `\addtogroup` and `\endgroup`  commands.

Method #1 has priority. That is, a member declared after a `\addtogroup` command,
but which has an `\ingroup` in its documentation, will be placed in the group
specified by the `\ingroup` command.


For example:
```cpp
/// \defgroup name This is a group
/// This is the brief description for the group.
/// This is the longer description
/// for the
/// group

/// \addtogroup

/// A function in group `name`
void function1();

/// A function in a different group `foo`
/// \ingroup foo
void function2();

/// \endgroup
```

Note that `\defgroup`, `\addtogroup` and `\endgroup` must be at the start of a
documentation block. Empty lines in between these commands in the code above is
therefore relevant.

## Differences with Doxygen

Doxygen uses the `\{` and `\}` commands to group members into a group. These are not
recognized by dox++. Left is Doxygen, right is corresponding dox++:
```none
/// \defgroup name title            /// \defgroup name title
/// \{
                                    /// \addtogroup name
void function1();
                                    void function1();
/// \}
                                    /// \endgroup
/// \addtogroup name
/// \{                              /// \addtogroup name

void function2();                   void function2();

/// \}                              /// \endgroup
```

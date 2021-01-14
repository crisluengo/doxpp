# Grouping

## Grouping namespace members

Namespace members can be assigned to one group. If assigned to a group, the
backend can choose to document those members in the group's page rather
than the namespace's page. Alternatively, the backend can index members
by their group.

Groups can be nested, forming a tree structure. That is, it is not legal
to form loops (a group being both an ancestor and a descendant of another
group) nor to assign two parent groups to one group. Groups are assigned
to a parent group just like a namespace member is.

A group can be documented using the `\group` command.

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
/// \group name This is a group
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

Note that `\group` and `\endgroup` must be at the start of a documentation block.
Empty lines in between these commands in the code above is therefore relevant.
`\addtogroup` can be in a documentation block on its own, in which case it needs
a parameter to indicate which group is being made active, or it can be at the
end of a `\group` documentation block, in which case it should not have a parameter.


## Grouping class members

For class members, the grouping system is a lot simpler. Typically class members
are grouped by access (public, protected and private). But by adding `\name` commands
inside the class definition, an alternative grouping can be established. This is
useful mostly for complex classes with many members.

The class member groups do not have documentation nor an ID (they cannot be referenced).
They only have a title, which will be used by the back end to make headers and
split up the class' table of contents.

Class member groups also cannot be nested, there is no parent/child relationship between
these groups.

Class members will be assigned to a group if their declaration (not their documentation
block) comes after the `\name` command that creates this block, and before another `\name`
or `\endname` command.

For example:
```cpp
class A {
   /// \name Group A
   int foo;
   int bar;
   /// \name Group B
   int baz;
public:
   A();
   /// \name Group C
   A(int foo);
   int getFoo() const;
   /// \endname
};
```
In this code, `foo` and `bar` are in a group called "Group A", `baz` and the default constructor
`A()` are in a group called "Group B", and `A(int)` and `getFoo()` are in a group called "Group C".

Note that the parsing of the `\name` and `\endname` commands is rather primitive,
this causes their influence to extend beyond a class declaration. If you don't put
an `\endname` at the end of a class, then in the next class' declaration, the previous
`\name` command will still be in effect. Thus:
```cpp
class A {
   /// \name Group A
   int foo;
};
class B {
   int bar;
};
```
Both classes will have a group called "Group A", and both `A::foo` and `B::bar` will be
in these respective groups.

There is always an implicit `\endname` at the end of a header file, though a warning
will be given if it is missing.


## Differences with Doxygen

Doxygen uses the `\{` and `\}` commands to group members into a group. These are not
recognized by dox++. Left is Doxygen, right is corresponding dox++:
```cpp
/// \defgroup name title            /// \group name title
/// \{                              /// \addtogroup

void function1();                   void function1();

/// \}                              /// \endgroup

/// \addtogroup name                /// \addtogroup name
/// \{

void function2();                   void function2();

/// \}                              /// \endgroup
```

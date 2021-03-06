\page documenting_code How to document your code

Put a decorated comment before the declaration of each member:
```cpp
/// documentation for foo
int foo;

//! documentation for bar
//! and more detailed stuff here
void bar(int);

/** documentation for baz
 * and more detailed stuff here
 */
int baz(double);

/*! and this is documentation for bang */
class bang{};
```

The first line of comment is the "brief" string, the rest is the "doc" string.

Stuff is copied verbatim to the output JSON file. The stuff is assumed to be valid
Markdown. Some commands will inject standard Markdown into the documentation.
But it depends on the generator that consumes the JSON file how it is interpreted.
If your generator supports HTML tags, you can use those. If you generator supports
special commands, you can use those. **dox++html** supports both.

**dox++parse** will identify certain commands, and change its behavior. See \ref commands
for details.

The `\brief` command changes the parsing so that the first paragraph, rather than
the first line, is the "brief" string. This command must be at the beginning of
the fist comment line in a block:
```cpp
/// \brief This is a rather long brief description
/// of the member below.
///
/// This is the detailed description right here.
/// Note the empty line that separates paragraphs.
int foo;
```

As an alternative, you can put documentation blocks separate from the declarations,
either in the same header file, a different header file, or a Markdown file. These
documentation blocks must start with a command such as `\class` or `\function` to
identify which member is being documented by that block. This member must actually
be declared in a documented header file.
```cpp
int foo;

void bar(int);

int baz(double);

/*! and this is documentation for bang */
class bang{};

/// \variable foo
/// documentation for foo

//! \function bar
//! documentation for bar
//! and more detailed stuff here

/** \function baz
 * documentation for baz
 * and more detailed stuff here
 */

/*! \class bang
 * and this is documentation for bang
 * */
```

!!! m-default m-block "Subpages"
    - \subpage commands
    - \subpage grouping
    - \subpage markdown

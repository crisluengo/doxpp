# Documenting Code

Put a decorated comment before the declaration of each member:
```
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
special commands, you can use those.

dox++ will identify certain commands, and change its behavior. See the
commands.md file for details.

The `\brief` command changes the parsing so that the first paragraph, rather than
the first line, is the "brief" string. This command must be at the beginning of
the fist comment line in a block:
```
/// \brief This is a rather long brief descrition
/// of the member below.
///
/// This is the detailed description right here.
/// Note the empty line that separates paragraphs.
int foo;
```

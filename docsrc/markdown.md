\page markdown Markdown markup

**TODO:** This page still needs to be formatted correctly.

dox++ expects documentation to be marked up using the common Markdown format.
dox++parse inserts Markdown formatting into the documentation for some
commands (such as `\‍ref` and `\‍see`).

dox++html uses [Python-Markdown](https://python-markdown.github.io) to convert
the Markdown-formatted text into HTML with a small set of addons:

- [admonition](https://python-markdown.github.io/extensions/admonition/)
- [attr_list](https://python-markdown.github.io/extensions/attr_list/)
- [codehilite](https://python-markdown.github.io/extensions/code_hilite/)
- [fenced_code](https://python-markdown.github.io/extensions/fenced_code_blocks/)
- [md_in_html](https://python-markdown.github.io/extensions/md_in_html/)
- [sane_lists](https://python-markdown.github.io/extensions/sane_lists/)
- [smarty](https://python-markdown.github.io/extensions/smarty/)
- [tables](https://python-markdown.github.io/extensions/tables/)
- [mdx_headdown](https://github.com/SaschaCowley/Markdown-Headdown)
- [markdown_subscript_extension](https://github.com/jambonrose/markdown_subscript_extension)
- [markdown_superscript_extension](https://github.com/jambonrose/markdown_superscript_extension)

Thus, the documentation text is parsed as
[John Gruber’s Markdown](https://daringfireball.net/projects/markdown/),
with some additions that are useful for code documentation and some modifications
that improve it. This page describes the formatting you can use, the links above
might be useful for obtain more details.

## Basic formatting

Write documentation text as you would write any comment in your code, within the
comment sections as described in [How to document your code](documenting_code.md).
Newlines are ignored within a paragraph. An empty line indicates a new paragraph.

Format your text using the following syntax:

- `*italics*`: *italics*
- `_italics_`: _italics_
- `**bold**`: **bold**
- `__bold__`: __bold__
- `but no*italics*here`: but no\*italics\*here
- `and no \*italics\* here either`: and no \*italics\* here either
- `` `code formatting` ``: `code formatting`
- ``` `` code with a backtick ` in it `` ```: `` code with a backtick ` in it ``
- `x~i~^2^`: x<sub>i</sub><sup>2</sup>
  ([markdown_subscript_extension](https://github.com/jambonrose/markdown_subscript_extension) and
  [markdown_superscript_extension](https://github.com/jambonrose/markdown_superscript_extension))
- `'quotes' and "double quotes" are automatically prettified`:
  ‘quotes’ and “double quotes” are automatically prettified
  ([smarty](https://python-markdown.github.io/extensions/smarty/))
- `create dashes with -- and ---`: create dashes with – and —
  (also [smarty](https://python-markdown.github.io/extensions/smarty/))

Note that the `\` character can be used to escape any character that might otherwise
be interpreted as Markdown formatting:

- \\   backslash
- \`   backtick
- \*   asterisk
- \_   underscore
- \{\}  curly braces
- \[\]  square brackets
- \(\)  parentheses
- \#   hash mark
- \+   plus sign
- \-   minus sign (hyphen)
- \.   dot
- \!   exclamation mark

It is possible to create headers using Markdown formatting, but this will prevent
dox++ from linking to them from other documentation blocks and from generating indexes.
You should always use `\section`, `\subsection` and `\subsubsection` instead
(see [Documentation commands](commands.md)).

Insert a line break by adding two spaces at the end of a line. Because many
code editors will remove trailing spaces, the command `\n` will be replaced
by two trailing spaces by dox++parse. (**TODO!**)

## Links

Links are inserted using the following syntax: `[link text](URL)` or `[link text](URL "title")`,
or simply `<URL>`. URL can be a full URL (`https://foo.com`), a local resource (`pages.html`)
or `#id` to reference an ID on the current page.

To link to other parts of the documentation, one would normally use the `\‍ref` command
(see [Documentation commands](commands.md)),
but it is possible to use a simple Markdown link if one knows the ID of the referenced
documentation element. For example, `[ns::foo](#ns-foo-int--double-)` would be equivalent
to `\‍ref ns::foo` if there existed a function declared as `int ns::foo(int, double)`.
Note that dox++parse inserts links like this for each `\‍ref` and each `\‍see` command.

## Code blocks

There are two ways to format code blocks: using "fences", and using indentation.

The standard method is to use 4 spaces of indentation:
```text
    // This is code
    foo(bar);
```

A fenced code block looks like this ([fenced_code](https://python-markdown.github.io/extensions/fenced_code_blocks/)):
````text
```
// This is code
foo(bar);
```
````

We use the [codehilite](https://python-markdown.github.io/extensions/code_hilite/) extension
to apply syntax highlighting to the code. This uses Pygments to identify the language and
apply highlighting. We recommend that you don't leave the language identification to chance,
and specify the language explicitly:
```text
    :::cpp
    // This is code
    foo(bar);
```
or
````text
```cpp
// This is code
foo(bar);
```
````

To identify the language (the "cpp" string in the examples above), use the "short name"
as listed [in the Pygments documentation](https://pygments.org/docs/lexers/).
Specifically, use "text" to turn off syntax highlighting.

## Lists

To create a list, start each list item with a `-`, `+` or `*`. Create numbered lists
by starting each line with a number followed by a period. The first number in the list
is meaningful, but other list items simply follow it:
```text
* list item 1
* list item 2

7. numbered list item 7
2. numbered list item 8
2. numbered list item 9
```
will be rendered as

* list item 1
* list item 2

7. numbered list item 7
8. numbered list item 8
9. numbered list item 9

It is important to separate the list items from a preceding paragraph with an empty
line.

It is not possible to mix numbered and unnumbered list items in the same list.

Note that if you separate list items with an empty line, list items will be rendered
with paragraph separation, as you would expect.

A list item can contain multiple paragraphs, code blocks, other lists, etc. Simply
indent the additional blocks by 4 spaces:
```text
* list item 1

    * sublist item 1.1
    * sublist item 1.2

* list item 2

    * sublist item 2.1

    Another paragraph in list item 2

* list item 3

        :::cpp
        // A C++ code block in list item 3
        foo(bar);
```

Note that fenced code blocks cannot be indented, so it is necessary to use the
other code block format.

We use the [sane_lists](https://python-markdown.github.io/extensions/sane_lists/)
extension to improve the standard Markdown list implementation.

## Blockquotes

Insert an `>` as the first character on the first line of a paragraph (or on
each line of the paragraph). Block quotes can be nested:
```text
> This is the first level of quoting.
>
> > This is nested blockquote.
>
> Back to the first level.
```
will be rendered as

> This is the first level of quoting.
>
> > This is nested blockquote.
>
> Back to the first level.

It is possible to put other Markdown elements inside a blockquote, including lists,
code and links.

## Tables

**TODO**
[tables](https://python-markdown.github.io/extensions/tables/)

## Admonitions

**TODO**
[admonition](https://python-markdown.github.io/extensions/admonition/)

## Equations

**TODO**

## Images

**TODO**

## Attributes

**TODO**
[attr_list](https://python-markdown.github.io/extensions/attr_list/)

## HTML tags

It is possible to include HTML code into your documentation. Everything enclosed
in HTML tags is copied as-is into the generated HTML pages. That is, the
text marked up using HTML is not parsed by the Markdown parser:
```text
This is a paragraph **with some bold text**.

<p>This is a paragraph without **any** bolding.</p>
```
will be rendered as

This is a paragraph **with some bold text**.  
This is a paragraph without \*\*any\*\* bolding.

The [md_in_html](https://python-markdown.github.io/extensions/md_in_html/) extension
allows the content of HTML blocks to be parsed by Markdown:
```text
This is a paragraph **with some bold text**.

<p markdown="1">This is a paragraph with **some** bolding.</p>
```
will be rendered as

This is a paragraph **with some bold text**.  
This is a paragraph with **some** bolding.

This can be useful to add a CSS class to a portion of the text, for example:
```html
<div markdown="1" class="m-text m-tiny">
First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell
</div>
```
will create a table with a smaller font. Since we can only add attributes to individual
cells of a table, not the table itself, this is the only way to add special styling
to a whole table. It is also the only way to add special styling to lists.

Examine the CSS style sheets as well as the generated HTML to learn what classes exist.
You can modify the default CSS style sheets as well, see [Configuring dox++](configuration.md).

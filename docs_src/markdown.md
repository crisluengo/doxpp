\page markdown Markdown markup

**dox++** expects documentation to be marked up using the common Markdown format.
**dox++parse** inserts Markdown formatting into the documentation for some
commands (such as `\‍ref` and `\‍see`).

**dox++html** uses [Python-Markdown](https://python-markdown.github.io) to convert
the Markdown-formatted text into HTML with a small set of extensions:

- Standard extensions
  [admonition](https://python-markdown.github.io/extensions/admonition/),
  [attr_list](https://python-markdown.github.io/extensions/attr_list/),
  [codehilite](https://python-markdown.github.io/extensions/code_hilite/),
  [fenced_code](https://python-markdown.github.io/extensions/fenced_code_blocks/), and
  [tables](https://python-markdown.github.io/extensions/tables/) to add features.
- Standard extensions
  [md_in_html](https://python-markdown.github.io/extensions/md_in_html/),
  [sane_lists](https://python-markdown.github.io/extensions/sane_lists/), and
  [smarty](https://python-markdown.github.io/extensions/smarty/) to improve standard formatting.
- Andrew Pinkham's
  [markdown_subscript_extension](https://github.com/jambonrose/markdown_subscript_extension), and
  [markdown_superscript_extension](https://github.com/jambonrose/markdown_superscript_extension).
- Sascha Cowley's
  [mdx_headdown](https://github.com/SaschaCowley/Markdown-Headdown) for internal purposes.
- Some **dox++**-specific extensions to allow it to correct internal links and retrieve
  information from the Markdown parser.

Thus, the documentation text is parsed as
[John Gruber’s Markdown](https://daringfireball.net/projects/markdown/),
with some modifications that improve it and some additions that are useful for code documentation.
This page describes the formatting you can use, the links above might be useful for obtain more details.

\section markdown_basic Basic formatting

Write documentation text as you would write any comment in your code, within the
comment sections as described in \ref documenting_code).
Newlines are ignored within a paragraph. An empty line indicates a new paragraph.

Format your text using the following syntax:

Markup                         | Result                       | Note
-------------------------------|------------------------------|-----------
`*italics*`                    | *italics*                    |
`_italics_`                    | _italics_                    |
`**bold**`                     | **bold**                     |
`__bold__`                     | __bold__                     |
`no_italics_here`              | no_italics_here              |
`yes*italics*here`             | yes*italics*here             |
`` `code formatting` ``        | `code formatting`            |
``` `` with backtick ` `` ```  | `` with backtick ` ``        |
`x~i~^2^`                      | x~i~^2^                      | through [markdown_subscript_extension](https://github.com/jambonrose/markdown_subscript_extension) and [markdown_superscript_extension](https://github.com/jambonrose/markdown_superscript_extension))
`'quotes' and "double quotes"` | 'quotes' and "double quotes" | through [smarty](https://python-markdown.github.io/extensions/smarty/))
`dashes -- and ---`            | dashes -- and ---            | also through [smarty](https://python-markdown.github.io/extensions/smarty/))

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
**dox++** from linking to them from other documentation blocks and from generating indexes.
You should always use `\section`, `\subsection` and `\subsubsection` instead
(see \ref commands).

Insert a line break by adding two spaces at the end of a line. Because many
code editors will remove trailing spaces, the command `\n` will be replaced
by two trailing spaces by **dox++parse**.

\section markdown_links Links

Links are inserted using the following syntax: `[link text](URL)` or `[link text](URL "title")`,
or simply `<URL>`. URL can be a full URL (`https://foo.com`), a local resource (`pages.html`)
or `#id` to reference an ID on the current page.

To link to other parts of the documentation, one would normally use the `\‍ref` command
(see \ref commands),
but it is possible to use a simple Markdown link if one knows the ID of the referenced
documentation element. For example, `[ns::foo](#ns-foo-int--double-)` would be equivalent
to `\‍ref ns::foo` if there existed a function declared as `int ns::foo(int, double)`.
Note that **dox++parse** inserts links like this for each `\‍ref` and each `\‍see` command.

\section markdown_code Code blocks

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

Both will be rendered in the same way:

!!! par
        // This is code
        foo(bar);

We use the [codehilite](https://python-markdown.github.io/extensions/code_hilite/) extension
to apply syntax highlighting to the code. This uses Pygments to identify the language and
apply highlighting. We recommend that you don't leave the language identification to chance
(we see above that identification failed for this short snipped),
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
These are rendered as

!!! par
        :::cpp
        // This is code
        foo(bar);

To identify the language (the "cpp" string in the examples above), use the "short name"
as listed [in the Pygments documentation](https://pygments.org/docs/lexers/).
Specifically, use "text" to turn off syntax highlighting:
````text
```text
// This is code
foo(bar);
```
````

\section markdown_lists Lists

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

!!! par
    * list item 1
    * list item 2

    7. numbered list item 7
    8. numbered list item 8
    9. numbered list item 9

It is important to separate the list items from a preceding paragraph with an empty
line.

It is not possible to mix numbered and unnumbered list items in the same list.

Note that if you separate list items with an empty line, list items will be rendered
with paragraph separation, as you would expect:
```text
* list item 1

* list item 2

* list item 3
```
will be rendered as

!!! par
    * list item 1

    * list item 2

    * list item 3

A list item can contain multiple paragraphs, code blocks, other lists, etc. Simply
indent the additional blocks by 4 spaces:
```text
* list item 1
    * sublist item 1.1
    * sublist item 1.2

* list item 2

    Another paragraph in list item 2

* list item 3

        :::cpp
        // A C++ code block in list item 3
        foo(bar);
```

!!! par
    * list item 1
        * sublist item 1.1
        * sublist item 1.2

    * list item 2

        Another paragraph in list item 2

    * list item 3

            :::cpp
            // A C++ code block in list item 3
            foo(bar);

Note that fenced code blocks cannot be indented, so it is necessary to use the
other code block format.

We use the [sane_lists](https://python-markdown.github.io/extensions/sane_lists/)
extension to improve the standard Markdown list implementation.

\section markdown_bockquotes Blockquotes

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

!!! par
    > This is the first level of quoting.
    >
    > > This is nested blockquote.
    >
    > Back to the first level.

It is possible to put other Markdown elements inside a blockquote, including lists,
code and links.

\section markdown_tables Tables

We use the [tables](https://python-markdown.github.io/extensions/tables/) extension to allow
producing tables. The syntax requires adding pipe characters (`|`) in between cells, and lines
formed by dashes (`-`) in between the header row and the rest of the table, as follows:
```text
First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell
```
This is rendered as

!!! par
    First Header  | Second Header
    ------------- | -------------
    Content Cell  | Content Cell
    Content Cell  | Content Cell

It is possible to add a pipe character at the beginning and end of each line as well.

Cell content can contain Markdown formatting.

To align columns add colons (`:`) at the beginning and/or end of the dashed lines that
separate the header from the rest of the column:

```text
Left aligned | Center aligned | Rigt aligned
:----------- |:--------------:| ------------:
Text         | Text           | Text
Other text   | Other text     | Other text
```
This is rendered as

!!! par
    Left aligned | Center aligned | Rigt aligned
    :----------- |:--------------:| ------------:
    Text         | Text           | Text
    Other text   | Other text     | Other text

To span columns, add a `colspan` property to the cell as described in \ref markdown_attributes.
For example,
```text
First Header  | Second Header | Third Header
------------- | ------------- | -------------
This is one long sentence that should span all cells { colspan="3" } ||
Content Cell  | Content Cell  | Content Cell
```
is rendered as

!!! par
    First Header  | Second Header | Third Header
    ------------- | ------------- | -------------
    This is one long sentence that should span all cells { colspan="3" } ||
    Content Cell  | Content Cell  | Content Cell

\section markdown_boxes Boxes

Boxes can be generated using the "admonition" syntax from reST (implemented here through the
[admonition](https://python-markdown.github.io/extensions/admonition/) extension).
```text
!!! note "Box title"
    Paragraph 1

    Paragraph 2
```
is rendered as a box like this one:

!!! note "Box title"
    Paragraph 1

    Paragraph 2

The syntax is `!!! type "optional title"`. Type indicates what the color of the box will
be, and what the default title will be. It is always possible to specify a custom title.
Using `""` for the title will cause there to not be a title at all.

These are the types and the corresponding default title and CSS classes currently implemented:

Type            | Default title | CSS class
----------------|---------------|--------------------------
`par`           | (no title)    | 'm-frame' { .m-frame }
`note`          | Note          | 'm-primary' { .m-primary }
`remark`        | Remark        | 'm-primary' { .m-primary }
`attention`     | Attention     | 'm-info' { .m-info }
`todo`          | TODO          | 'm-info' { .m-info }
`deprecated`    | Deprecated    | 'm-warning' { .m-warning }
`warning`       | Warning       | 'm-warning' { .m-warning }
`bug`           | Bug           | 'm-danger' { .m-danger }
`see`           | See also      | 'm-default' { .m-default }
`literature`    | Literature    | 'm-default' { .m-default }
`author`        | Author        | 'm-default' { .m-default }
`authors`       | Authors       | 'm-default' { .m-default }
`copyright`     | Copyright     | 'm-default' { .m-default }
`version`       | Version       | 'm-default' { .m-default }
`since`         | Since         | 'm-default' { .m-default }
`date`          | Date          | 'm-default' { .m-default }
`pre`           | Precondition  | 'm-success' { .m-success }
`post`          | Postcondition | 'm-success' { .m-success }
`invariant`     | Invariant     | 'm-success' { .m-success }
`aside`         | (no title)    | 'm-dim' { .m-dim }
(anything_else) | (capitalized) | 'anything_else'

Note that most of these correspond to Doxygen commands to generate boxes.

It is possible to add additional CSS classes after `type`: `!!! type class1 class2 "optional title"`

By default, the class 'm-note' is used for admonitions. This class renders a colored
box as shown above. If 'm-block' is added as an additional class, then that one is
used instead of 'm-note'. For example,

```text
!!! note m-block "Box title"
    Paragraph 1

    Paragraph 2
```
is rendered as a "block" like this one:

!!! note m-block "Box title"
    Paragraph 1

    Paragraph 2

\section markdown_equations Equations

**TODO** This is not yet implemented

\section markdown_images Images

To inert an image, use the syntax `![Alt text](/path/to/image_file.jpg "Optional title")`. The
"Alt text" is the text that is rendered instead of the image if the image file cannot be
opened (or if image display is disabled in the browser). The "Optional title" is the text
shown when hovering over the image. This optional title can be left out:
`![Alt text](/path/to/image_file.jpg)`. Note how the syntax is identical to a link,
but with a `!` prepended.

Images can appear inside other elements, including links. For example,
```md
[![Manuals](manuals.png "The most ridiculous offender of all is the sudoers man page,
which for 15 years has started with a 'quick guide' to EBNF, a system for defining the
grammar of a language. 'Don't despair', it says, 'the definitions below are annotated.'
")](https://xkcd.com/1343/)
```
is rendered as

!!! par
    [![Manuals](manuals.png "The most ridiculous offender of all is the sudoers man page,
    which for 15 years has started with a 'quick guide' to EBNF, a system for defining the
    grammar of a language. 'Don't despair', it says, 'the definitions below are annotated.'
    ")](https://xkcd.com/1343/)

\section markdown_attributes Attributes

One can add CSS attributes to an element by adding the following syntax:
```text
{ #someid .someclass somekey='some value' }
```
This is implemented through the
[attr_list](https://python-markdown.github.io/extensions/attr_list/) extension.
`someid` will be the ID of the element, `someclass` will be added the list of classes,
and the (`somekey`/`some value`) pair will be added directly to the element. Note that
the spaces inside the braces are required. It is allowed to add a colon right after
the opening brace, for compatibility with other Markdown parsers: `{: ... }`.

To add the CSS attributes to a block element, put them in a line by themselves at the
end of the block element:
```text
This is a paragraph.
{ .m-text .m-tiny }
```
will be rendered as

!!! par
    This is a paragraph.
    { .m-text .m-tiny }

To add the attributes to inline elements, add them right after the element, with no
space in between:
```text
This is a **paragraph**{ .m-text .m-tiny }.
```
will be rendered as

!!! par
    This is a **paragraph**{ .m-text .m-tiny }.

Note that it is not possible to assign attributes to a single word, unless it is wrapped
in an element as above.

For code blocks, use the fences syntax and apply the attributes to the opening fences:
````text
``` { .cpp .m-text .m-tiny }
// This is code
foo(bar);
```
````
The first class name is interpreted as the language, the remaining ones are CSS classes.

<aside markdown="1" class="m-note m-frame">
``` { .cpp .m-text .m-tiny }
// This is code
foo(bar);
```
</aside>

\comment    I had to fudge the example above because fenced code blocks cannot be nested
\comment    inside other blocks.

For tables cells, put the attributes after the cell contents, separated with at least one space.
Without a space, the attributes would be applied to the element they're connected to.
There is no way to apply the attributes to a table row or the whole table.

Note that there are many limitations to this system, see
[the attr_list documentation](https://python-markdown.github.io/extensions/attr_list/).
If you don't manage to set required attributes this way, use HTML instead.

\section markdown_html HTML tags

It is possible to include HTML code into your documentation. Everything enclosed
in HTML tags is copied as-is into the generated HTML pages. That is, the
text marked up using HTML is not parsed by the Markdown parser:
```text
This is a paragraph **with some bold text**.

<p>This is a paragraph without **any** bolding.</p>
```
will be rendered as

!!! par
    This is a paragraph **with some bold text**.

    This is a paragraph without \*\*any\*\* bolding.

The [md_in_html](https://python-markdown.github.io/extensions/md_in_html/) extension
allows the content of HTML blocks to be parsed by Markdown:
```text
This is a paragraph **with some bold text**.

<p markdown="1">This is a paragraph with **some** bolding.</p>
```
will be rendered as

!!! par
    This is a paragraph **with some bold text**.

    This is a paragraph with **some** bolding.

This can be useful to add a CSS class to a portion of the text, for example:
```text
<div markdown="1" class="m-text m-tiny">

First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell

</div>
```
will create a table with a very small font:

!!!par
    <div markdown="1" class="m-text m-tiny">

    First Header  | Second Header
    ------------- | -------------
    Content Cell  | Content Cell
    Content Cell  | Content Cell

    </div>

Since we can only add attributes to individual
cells of a table, not the table itself, this is the only way to add special styling
to a whole table. It is also the only way to add special styling to lists.

Examine the CSS style sheets as well as the generated HTML to learn what classes exist.
You can modify the default CSS style sheets as well, see \ref configuration.

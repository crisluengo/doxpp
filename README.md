[dox++](https://github.com/crisluengo/doxpp) is a Clang-based documentation preparation
system for C++.

Doxygen is the de-facto standard documentation system for C++. Its HTML output is not
flexible enough for many people, who resort to using the XML output and parsing that
into their own HTML. However, Doxygen's XML output has some issues and does not contain
all information present in the HTML output. For example, when using groups ("modules"),
the XML output does not have links for types documented in other groups. Doxygen also
often requires weird workarounds where its Markdown parsing is incorrect.

There are several Doxygen alternatives, but none seemed suitable for my purposes.

dox++ is yet another alternative, meant to be simple in implementation rather than feature
complete. It depends on Clang to parse the C++ header files.
It does the things I need it to do, but it might be lacking in areas that are
relevant to you. I invite you to improve on it and send a pull request. The project focus
is C++ code, not C code, and so some C features might be overlooked on purpose.

**dox++parse** produces a single JSON output for the whole project. This JSON file contains
all the information needed to produce documentation. It contains documentation for all
namespaces, classes, functions, variables, etc., even those without explicit documentation
blocks. It contains documentation for each header file and for each group, and it contains
additional pages. It links references to members across the project.
Typesetting, creating indices, etc. is left to the generator (or back-end), which keeps
the program simple.

**dox++html** produces a series of HTML files documenting the project, using the
JSON created by dox++parse. The generated HTML is based on [m.css](https://mcss.mosra.cz/),
and its fantastic Doxygen C++ theme, by Vladimír Vondruš. It is all static HTML5 with
customizable CSS, and wonderful client-side search functionality that uses JavaScript.

**TODO** Eventually we'll have other generators here, for example to generate PDF through
Pandoc.


# How code is parsed and documented

dox++ follows Doxygen syntax only partially. Full documentation is in the
[`doc/`](doc/README.md) directory.

Changes from Doxygen are as follows:

1. Markup commands are passed as-is into the output JSON file, and left to the generator
   to parse. Our current generator does not parse any of the Doxygen markup commands, and
   assumes pure Markdown. Markdown formatting works also in page and section titles.

2. Documented members can belong to one group (module) at most. Groups form a tree structure.
   Grouping commands have the same names but work slightly differently. Namespace and
   class pages link back to the group they belong to, if applicable.

3. It is meant to parse header files only, not the implementation files. It documents the API
   of a library, not all the code in a project. It documents everything declared in the header
   files, even if no documentation block is associated to the declaration. The generator can
   choose what to output. Directories are not documented, only the header files themselves.

4. Commands intended to document members cannot define non-existing members. For example,
   the `\class <name>` command adds documentation to a class. The class must be declared somewhere
   in the header files. These comment blocks cannot define properties of the documented members,
   those properties must be reflected in the code itself. For example, `\extends`, `\pure` or
   `\static` are not recognized. Some of those commands have simpler interfaces, and some have
   aliases that make more sense (for example `\macro` for `\def`, `\alias` for `\typedef`,
   `\function` for `\fn`).

5. Markdown files can contain comments with the `\comment` command. There is no empty page generated
   for Markdown files that contain member documentation.

6. Unique identifiers for members are fairly readable, and don't look like the hashes that
   Doxygen generates. This should allow the generator to create more meaningful URLs.

7. SFINAE template parameters are summarized as "<SFINAE>". Multiple definitions of a template
   with different SFINAE results (such as when one version is defined for unsigned numeric types
   and another one for signed numeric types) are collapsed into a single element.

8. There is no "autolink", all links must be explicitly made with `\ref`. Consequently, it is
    not necessary to prepend `%` to avoid turning some words into links.

9. The generator creates pages for undocumented classes, namespaces and files that have documented
   members. Thus, it is not necessary to document a file just to be able to document the functions
   that are declared in it.

## What is missing

I'm sure there are lots of things missing I'm not even aware of. Here are a few missing things
that I am aware of.

Things we'd like to add/fix/improve:

1. Template parameters that are templated types are treated a bit too simplistically.

2. Link override and overridden functions together.

3. There's no way to have the literal text "`\ref`" (and similar commands) in the documentation,
   we need to avoid matching commands inside backticks or in code blocks.

4. References to a member that is injected into a different namespace it was declared in are not
   resolved (e.g. through a `using` statement, or members of an anonymous or inline namespace).

5. Clang doesn't easily report on pre-processor macros. Instead of making things complicated,
we just require adding the `\macro` (or `\def`) command at the top of the documentation block.


# License

Copyright 2020-2021, Cris Luengo  
Most code and documentation in this project is distributed with the GPL-2.0 license.  
See the file `COPYING` for details.  
Some files have more permissive licenses.

Some code and ideas in **dox++parse** are derived from [cldoc](https://github.com/jessevdk/cldoc):  
Copyright 2013-2018, Jesse van den Kieboom  
cldoc uses the GPL-2.0 license.

Some code and most ideas in **dox++html** are derived from [m.css](https://mcss.mosra.cz/);  
CSS and HTML templates are modified from m.css:  
Copyright 2017-2020 Vladimír Vondruš  
m.css uses the MIT license.

This project includes verbatim copies `cindex.py` from the LLVM project,
and `mdx_subscript.py` and `mdx_superscript.py` by Andrew Pinkham. In the future we might install the
relevant packages from PyPI, but for now the copied files avoid some dependencies.


# Requirements

dox++ requires Python 3, and has been tested (so far) with Python 3.9. Packages required:
`jinja2`, `markdown`, `markdown-headdown`, `Pygments`

dox++ requires Clang to be installed on the system. I don't know which is the minimal
version, but there's no reason to use a very old one.

[dox++](https://github.com/crisluengo/doxpp) is a Clang-based documentation preparation
system for C++.

**This is work in progress, hold on while we complete the work**

Doxygen is the de-facto standard documentation system for C++. Its HTML output is not
flexible enough for many people, who resort to using the XML output and parsing that
into their own HTML. However, Doxygen's XML output has some issues and does not contain
all information present in the HTML output. For example, when using groups ("modules"),
the XML output does not have links for types documented in other groups.

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
JSON created by dox++parse. The generated HTML is based on [m.css](https://mcss.mosra.cz/)
by Vladimír Vondruš.

**TODO** Eventually we'll have other generators here, for example to generate PDF through
Pandoc.


# How code is parsed and documented

dox++ follows Doxygen syntax for documentation, but with some changes. Full documentation
is in the [`doc/`](https://github.com/crisluengo/doxpp/tree/main/doc) directory.

Changes from Doxygen are as follows:
1. Markup commands are passed as-is into the output JSON file, and left to the generator
to parse.
2. Documented members can belong to one group at most. Groups form a tree structure.
3. It is meant to parse header files only, not the implementation files. It documents the API
of a library, not all the code in a project.
4. It documents everything declared in the header files, even if no documentation block
is associated to the declaration. The generator can choose what to output.
5. Commands intended to document members cannot define non-existing members. For example,
the `\class <name>` command adds documentation to a class. The class must be declared somewhere
in the header files.
6. These comment blocks cannot define properties of the documented members, those properties
must be reflected in the code itself. For example, `\extends`, `\pure` or `\static` are not
recognized.
6. Some of those commands have simpler interfaces, and some have aliases that make more sense
(for example `\macro` for `\def`, `\alias` for `\typedef`, `\function` for `\fn`).
7. Markdown files can contain comments with the `\comment` command.
8. Directories are not documented, only the header files themselves.
9. Unique identifiers for members are fairly readable, and don't look like the hashes that
Doxygen generates. This should allow the generator to create more meaningful URLs.
10. There is no "autolink", all links must be explicitly made with `\ref`.
11. You can use Markdown formatting in page and section titles.
12. There is no empty page generated for Markdown files that contain member documentation.

## What is missing

I'm sure there are lots of things missing I'm not even aware of. Here are a few missing things
that I am aware of.

Things we'd like to add/fix/improve:

1. Function pointer types.
2. SFINAE template parameters are hard to parse. The current solution is to record "<SFINAE>"
   as the type of any template parameter without a name. This is obviously not right, but it
   works for me for now.
3. Types in a (partial) template specialization are not always recorded.
4. If a templated type is used as the type of a parameter or variable, it is not linked to
   the documentation for that type.
5. Link override and overridden functions together.
6. There's no way to have the literal text "`\ref`" (and similar commands) in the documentation,
   we need to avoid matching commands inside backticks or in code blocks.

Things that Clang doesn't tell us:

1. Clang doesn't easily report on pre-processor macros. Instead of making things complicated,
we just require adding the `\macro` (or `\def`) command at the top of the documentation block.
2. Clang doesn't say if an override function is `final`.
3. Clang doesn't say if a variable or function is `constexpr`, but we worked our way around that.

# License

Copyright 2020, Cris Luengo  
Most code and documentation in this project is distributed with the GPL-2.0 license.  
See the file `COPYING` for details.  
Some files have more permissive licenses.

Some code and ideas are derived from [cldoc](https://github.com/jessevdk/cldoc):  
Copyright 2013-2018, Jesse van den Kieboom  
cldoc uses the GPL-2.0 license.

Some code and ideas are derived from [m.css](https://mcss.mosra.cz/);  
CSS and HTML templates are taken (templates modified) from m.css:  
Copyright 2017-2020 Vladimír Vondruš  
m.css uses the MIT license.


# Requirements

dox++ requires Python 3, and has been tested (so far) with Python 3.9. Packages required:
`markdown`, `jinja2`.

dox++ requires Clang to be installed on the system. I don't know which is the minimal
version, but there's no reason to use a very old one.

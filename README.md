**dox++** is a Clang-based documentation preparation system for C++.

See [the project website](https://crisluengo.github.io/doxpp) for details.


# Requirements

dox++ requires Python 3, and has been tested (so far) with Python 3.9. Packages required:
`jinja2`, `markdown`, `markdown-headdown`, `Pygments`

dox++ requires Clang to be installed on the system. I don't know which is the minimal
version, but there's no reason to use a very old one.


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

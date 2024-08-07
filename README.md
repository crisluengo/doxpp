**dox++** is a Clang-based documentation preparation system for C++.

See [the project website](https://crisluengo.github.io/doxpp/) for details.


# Requirements

**dox++** requires Python 3, and has been tested (so far) with Python 3.6 on Linux, and 3.9 and 3.12 on macOS.
Required packages from PyPI:
`clang`, `jinja2`, `markdown`, `markdown-headdown`, `mdx_math_svg`, `Pygments`.

**dox++** requires Clang to be installed on the system. I don't know which is the minimal
version, but there's no reason to use a very old one.

The `mdx_math_svg` Markdown extension requires a working installation of LaTeX, but only if
you use equations in your documentation. [TeX Live](https://tug.org/texlive/) is a good choice.

# License

Copyright 2020-2021, Cris Luengo  
Most code and documentation in this project is distributed with the GPL-2.0 license.  
See the file `COPYING` for details.  
Some files have more permissive licenses.

Some code and ideas in **dox++parse** are derived from [cldoc](https://github.com/jessevdk/cldoc).  
Copyright 2013-2018, Jesse van den Kieboom  
cldoc uses the GPL-2.0 license.

Some code and most ideas in **dox++html** are derived from [m.css](https://mcss.mosra.cz/);  
CSS and HTML templates are modified from m.css; search functionality is unmodified from m.css.  
Copyright 2017-2020 Vladimír Vondruš  
m.css uses the MIT license.

This project includes copies of `mdx_subscript.py` and `mdx_superscript.py`
from the PyPI packages `MarkdownSubscript` and `MarkdownSuperscript`, updated for
the latest version of Python-Markdown.  
Copyright 2014-2018 Andrew Pinkham  
using the Simplified BSD license.

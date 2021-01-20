# Simple example project

This directory contains a simple example project to demonstrate how dox++
can be used. The `transport` subdirectory contains header files for the
project (the rest of the project is irrelevant to generating documentation
and therefore not present here), as well as a Markdown file with additional
documentation.

To parse the sources and extract all relevant information, run

    ../dox++parse

from this directory. A file `transport.json` will be created in the current
directory. Next, generate the HTML with

    ../dox++html

The HTML will be placed in `../docs/example/`

The `dox++config` file can be adjusted to change what input files are read,
the name and location of the output files, and many other options for
what to present and how.

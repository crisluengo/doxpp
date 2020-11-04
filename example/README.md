# Simple example project

This directory contains a simple example project to demonstrate how dox++
can be used. The `transport` subdirectory contains header files for the
project (the rest of the project is irrelevant to generating documentation
and therefore not present here), as well as a Markdown file with additional
documentation.

To build the documentation, run

    ../dox++parse

from this directory. The `dox++config` file can be adjusted to change what
input files are read, the name and location of the output file, and some
other options.

The output file will be `transport.json`.

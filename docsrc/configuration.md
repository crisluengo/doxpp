\page configuration Configuring **dox++**

This is the default configuration file created by `dox++parse -g`:

```ini
# Default dox++ configuration file

[clang]
compiler flags = 
include directories = 

[log]
level = warning

[input]
root directory = .
header files = *.h *.hpp
markdown files = *.md
tab size = 4

[json]
filename = dox++out.json
use typewriter font = no
formatting = compact

[project]
name = Project Name
brief = Short project description
url = 
logo = 

[html]
output directory = html
document private virtual members = yes
document private non-virtual members = yes
document protected members = yes
document undocumented members = no
modify include statement = def modify_include_statement(id): return id
theme color = #22272e
favicon = 
stylesheets = 
templates = 
documentation link class = m-doc
extra files = 
html header = 
page header = 
fine print = [default]
navigation bar 1 = [('', '#pages', []),('', '#modules', []),('', '#namespaces', [])]
navigation bar 2 = [('', '#classes', []),('', '#files', [])]
file index expand levels = 1
class index expand levels = 1
class index expand inner = no

[search]
enable = True
download binary = False
base url = 
external url = 
add snake case suffixes = yes
add camel case suffixes = yes
```

\section clang Section clang

Options to configure Clang.

**compiler flags**: Flags to pass to Clang when parsing the project header files. Specify
the C++ standard used (e.g. `-std=c++17`), preprocessor macro definitions (e.g. `-DFOO`),
and options such as `-xc++` (ensures sources are interpreted as C++, not C). 

**include directories**: Directories to add to the include search path. Separate them with
spaces. If a directory name has a space in it, enclose the name in double quotes. For
example,
```ini
include directories = include/ "/opt/my thing/include/"
```

\section log Section log

Options to configure the logger.

**level**: 'error', 'warning', 'info' or 'debug'. 'error' provides the lowest level of
diagnostic output (only errors are shown). 'warning' (the default) shows also warnings.
'info' gives some additional information about what the program is doing. 'debug' should
only be used to debug the **dox++** programs, and shouldn't be necessary to debug your
documentation sources; it produces a huge amount of output, we recommend only using it
with very small test projects.


\section input Section input

Options to describe the input to be parsed.

**root directory**: The root directory for the header files. This is the directory that
you would pass to the compiler with `-I` when using the library. Header file names
will be shown in the documentation relative to this directory.

**header files**: List of header file names to parse for documentation. Separate names
with a space, enclose names with spaces in quotes. Names can contain wildcards. Paths
are relative to the current directory at the time of running the tools, not relative
to the configuration file's directory or to the **root directory** option.

**markdown files**: List of Markdown files with additional documentation, provided in the
same way as the header files.

**tab size**: Integer value for how many spaces each tab character advances. If the source code
uses tabs, they will be converted to spaces according to this value. It is important to match
this value correctly so that Markdown indenting is interpreted as intended.
This does not affect the Markdown parsing, which always assumes 4 spaces indentation. 


\section json Section json

Options to configure the intermediate JSON file.

**filename**: Name of the intermediate JSON file. Defaults to `dox++out.json`. The path
given is relative to the current directory at the time of running **dox++parse** or
**dox++html**, not relative to the directory containing the configuration file.

**use typewriter font**: 'yes' or 'no' (defaults to 'no'),
indicating whether to use "`<name>`" or "<name>" when writing the name of members when processing
the `\‍ref` command. The \`\` is Markdown for code formatting. Note that member names elsewhere
are formatted by the generator, not by **dox++parse** which processes the `\‍ref` command.
Note that a member name in the documentation text not preceded by the `\‍ref` command will not
be recognized as a member name, and not typeset accordingly. Instead, manually add \`\` around
member names if not referenced.

**formatting**: 'compact' (default) or 'readable'. Set to 'readable' to pretty-format the
JSON file.


\section project Section project

Options describing the project.

**name**: Project name, shown in the header of each HTML page.

**brief**: Project short description, shown in the header of each HTML page.

**url**: Project homepage URL, the project's name will be a link to the homepage.

**logo**: Project logo, shown in the header of each HTML page.


\section html Section html

Options to configure how the HTML pages are generated and what is shown in them.

**output directory**:

**document private virtual members**:

**document private non-virtual members**:

**document protected members**:

**document undocumented members**:

**modify include statement**:

**theme color**:

**favicon**:

**stylesheets**:

**templates**:

**documentation link class**:

**extra files**:

**html header**:

**page header**:

**fine print**:

**navigation bar 1**:

**navigation bar 2**:

**file index expand levels**:

**class index expand levels**:

**class index expand inner**:


\section search Section search

Options to configure the search functionality on the generated website.

**enable**:

**download binary**:

**base url**:

**external url**:

**add snake case suffixes**:

**add camel case suffixes**:

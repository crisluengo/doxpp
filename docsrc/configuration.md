\page configuration Configuring the **dox++** tools

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
enable = yes
download binary = no
base url = 
external url = 
add snake case suffixes = yes
add camel case suffixes = yes
```

Each line is formatted as `key = value`, where "value" can be just about anything. If including
line breaks, indent subsequent lines to indicate continuation. Lines starting with a semicolon (`;`)
or a hash (`#`) are ignored. Keys are grouped into sections, indicated with `[name]`. These
sections are relevant, a key with the same name in a different section is not the same option.

\section config_section_clang Section clang

Options to configure Clang.

\subsection config_clang_compilerflags compiler flags
Flags to pass to Clang when parsing the project header files. Specify
the C++ standard used (e.g. `-std=c++17`), preprocessor macro definitions (e.g. `-DFOO`),
and options such as `-xc++` (ensures sources are interpreted as C++, not C). 

\subsection config_clang_includedirectories include directories
Directories to add to the include search path. Separate them with
spaces. If a directory name has a space in it, enclose the name in double quotes. For
example,
```ini
include directories = include/ "/opt/my thing/include/"
```

\section config_section_log Section log

Options to configure the logger.

\subsection config_clang_log_level level
'error', 'warning', 'info' or 'debug'. 'error' provides the lowest level of
diagnostic output (only errors are shown). 'warning' (the default) shows also warnings.
'info' gives some additional information about what the program is doing. 'debug' should
only be used to debug the **dox++** programs, and shouldn't be necessary to debug your
documentation sources; it produces a huge amount of output, we recommend only using it
with very small test projects.


\section config_section_input Section input

Options to describe the input to be parsed.

\subsection config_input_rootdirectory root directory
The root directory for the header files. This is the directory that
you would pass to the compiler with `-I` when using the library. Header file names
will be shown in the documentation relative to this directory.

\subsection config_input_headerfiles header files
List of header file names to parse for documentation. Separate names
with a space, enclose names with spaces in quotes. Names can contain wildcards. Paths
are relative to the current directory at the time of running the tools, not relative
to the configuration file's directory or to the **root directory** option.

\subsection config_input_markdownfiles markdown files
List of Markdown files with additional documentation, provided in the
same way as the header files.

\subsection config_input_tabsize tab size
Integer value for how many spaces each tab character advances. If the source code
uses tabs, they will be converted to spaces according to this value. It is important to match
this value correctly so that Markdown indenting is interpreted as intended.
This does not affect the Markdown parsing, which always assumes 4 spaces indentation. 


\section config_section_json Section json

Options to configure the intermediate JSON file.

\subsection config_json_filename filename
Name of the intermediate JSON file. Defaults to `dox++out.json`. The path
given is relative to the current directory at the time of running **dox++parse** or
**dox++html**, not relative to the directory containing the configuration file.

\subsection config_json_usetypewriterfont use typewriter font
'yes' or 'no' (defaults to 'no'),
indicating whether to use "`` `<name>` ``" or "`<name>`" when writing the name of members when processing
the `\‍ref` command. The `` `.` `` is Markdown for code formatting. Note that member names elsewhere
are formatted by the generator, not by **dox++parse** which processes the `\‍ref` command.
Note that a member name in the documentation text not preceded by the `\‍ref` command will not
be recognized as a member name, and not typeset accordingly. Instead, manually add `` `.` `` around
member names if not referenced.

\subsection config_json_formatting formatting
'compact' (default) or 'readable'. Set to 'readable' to pretty-format the
JSON file.


\section config_section_project Section project

Options describing the project.

\subsection config_project_name name
Project name, shown in the header of each HTML page.

\subsection config_project_brief brief
Project short description, shown in the header of each HTML page.

\subsection config_project_url url
Project homepage URL, the project's name will be a link to the homepage.

\subsection config_project_logo logo
Project logo, shown in the header of each HTML page.


\section config_section_html Section html

Options to configure how the HTML pages are generated and what is shown in them.

\subsection config_html_outputdirectory output directory
The directory where the HTML files and search data are written to.
Used CSS files, image files, etc. are copied there as well.

\subsection config_html_documentprivatevirtualmembers document private virtual members
'yes' (default) or 'no'. Whether to include class
members that are private and virtual in the documentation.
Some C++ coding practices require private virtual members as part of the public API,
as clients can override those virtual members to implement functionality.

\subsection config_html_documentprivatenonvirtualmembers document private non-virtual members
'yes' (default) or 'no'. Whether to include
the remaining private class members in the documentation. Turn on both this and the previous
option to document all private members.

\subsection config_html_documentprotectedmembers document protected members
'yes' (default) or 'no'. Whether to include the protected
class members in the documentation.

\subsection config_html_documentundocumentedmembers document undocumented members
'yes' or 'no' (default). Whether to include the undocumented
members in the documentation (this includes files and namespaces and so on, but not macros because
those are not reported by **dox++parse** if they're not explicitly documented).
If 'no', undocumented members that have documented child members will still be shown.

\subsection config_html_modifyincludestatement modify include statement
A Python function to modify include statements. The default is
a no-op function:
```ini
modify include statement = def modify_include_statement(id): return id
```
The input to the function is the ID of the include file, the output is the ID for the
include file to report instead.
The DIPlib project uses the following function:
```ini
modify include statement = def modify_include_statement(id): return 'file--diplib-h' if id.startswith('file--diplib--library--') else id
```
This causes all functions and classes documented in files under the `diplib/library/` directory to
report the `diplib.h` file as their include file (which is a dummy file that includes other headers,
and is considered the "standard" include file for the library).

The reason we use a function like this for this modification, rather than having the user
modify the JSON file before generating HTML, is that in this way, the header files are still properly
documented and still show the members declared in them, but the members themselves show a different
header to be used. If one were to modify the JSON file, the dummy `diplib.h` file would be
shown to declare a lot of library functionality, which might be misleading.

\subsection config_html_themecolor theme color
'#hhhhhh'. The 6-digit hexadecimal representation of a color, sets the
`<meta name="theme-color">` tag in the header of each HTML file. Defaults to '#22272e'.

\subsection config_html_favicon favicon
Name of icon file. Sets the `<link rel="icon">` tag in the header of each HTML file.

\subsection config_html_stylesheets stylesheets


\subsection config_html_templates templates

\subsection config_html_documentationlinkclass documentation link class
Defaults to 'm-doc'.

\subsection config_html_extrafiles extra files

\subsection config_html_htmlheader html header

\subsection config_html_pageheader page header

\subsection config_html_fineprint fine print
Defaults to: `[default]`.

\subsection config_html_navigationbar1 navigation bar 1
Defaults to: `[('', '#pages', []),('', '#modules', []),('', '#namespaces', [])]`.

\subsection config_html_navigationbar2 navigation bar 2
Defaults to: `[('', '#classes', []),('', '#files', [])]`.

\subsection config_html_fileindexexpandlevels file index expand levels
Defaults to '1'.

\subsection config_html_classindexexpandlevels class index expand levels
Defaults to '1'.

\subsection config_classindexexpandinner class index expand inner
'yes' or 'no' (default).


\section config_section_search Section search

Options to configure the search functionality on the generated website.

\subsection config_search_enable enable
'yes' (default) or 'no'.

\subsection config_search_downloadbinary download binary
'yes' or 'no' (default). If 'yes', the client automatically downloads a tightly
packed binary containing search data and performs search directly on it. However, in some
browsers (Chormium, Safari) this does not work when reading from a local file system
(i.e. when you're testing your site before deployment). For this case, set the option to 'no'.
This creates a base85-encoded representation of the search binary, which can be loaded asynchronously
as a plain JavaScript file. The search data will be 25% larger. Set to 'yes' for deployment.

\subsection config_search_baseurl base url
When set, enables OpenSearch. Set to the URL where the documentation website is deployed.

\subsection config_search_externalurl external url
When set, the search box will suggest to perform an full-text search using an
external search engine if nothing matches. The substring `{query}` will be replaced with the
word typed into the search box. For example, for this site it is set to:
```ini
external url = https://google.com/search?q=site:crisluengo.github.io+{query}
```

\subsection config_search_addsnakecasesuffixes add snake case suffixes
'yes' (default) or 'no'. If 'yes', will add entries into the
search data for each of the parts of names of functions, classes, variables, etc. that use
snake case. This allows more flexible search, but it also increases the size of the search data.
Note that there is a limit to the number of search symbols that can be included, if this limit
is exceeded, turn off this option.

\subsection config_search_addcamelcasesuffixes add camel case suffixes
'yes' (default) or 'no'. If 'yes', will add entries into the
search data for each of the parts of names of functions, classes, variables, etc. that use
camel case. This allows more flexible search, but it also increases the size of the search data.
Note that there is a limit to the number of search symbols that can be included, if this limit
is exceeded, turn off this option.

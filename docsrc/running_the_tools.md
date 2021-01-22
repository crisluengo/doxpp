\page running_the_tools Running **dox++parse** and **dox++html**

**dox++parse** parses the sources and creates a single JSON file containing
all the information extracted (see \ref json_output). **dox++html** takes
this JSON file and produces a web site for the documentation.

First, create a configuration file, see \ref configuration for options.
```bash
dox++parse -g [<config_file>]
```
If `<config_file>` is left out, a file named `dox++config` will be created in the
current directory. Specifying a configuration file name could be useful for
example if multiple different web sites are created for the same project.
Paths in the configuration file are relative to the current
directory, not the configuration file (**TODO:** should we change that?).

The configuration file indicates the source files, the name and location
of the intermediate JSON file, and the location for the output HTML files.
After completing the configuration,
```bash
dox++parse [<config_file>]
```
will create the JSON data file. Next,
```bash
dox++html [<config_file>]
```
will create the website.


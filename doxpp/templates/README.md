These HTML templates are modified from [m.css](https://mcss.mosra.cz/).

Copyright 2020, Cris Luengo.

Copyright © 2017, 2018, 2019, 2020 Vladimír Vondruš <mosra@centrum.cz>

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

---

# Changes

The biggest changes to these templates are:
- Removed dir.html and entry-dir.html
- Renamed annotated.html -> classes.html
- Renamed group.html -> module.html
- Renamed details-define.html -> details-macro.html and entry-define.html -> entry-macro.html
- Renamed details-func.html -> details-function.html and entry-func.html -> entry-function.html
- Renamed details-typedef.html -> details-alias.html and entry-typedef.html -> entry-alias.html
- Renamed details-var.html -> details-variable.html and entry-var.html -> entry-variable.html
- ... and of course some changes to the templates themselves.

TODO:
- In class documentation, we want to document private stuff just as well as public and protected stuff.
    - base_classes
    - derived_classes
    - typeless_funcs (public, protected and private)
    - groups (move these here, instead of at the bottom)
    - public_types
    - public_funcs
    - public_vars
    - public_static_funcs
    - public_static_vars
    - protected_types
    - protected_funcs
    - protected_vars
    - protected_static_funcs
    - protected_static_vars
    - private_types (to add)
    - private_funcs
    - private_vars (to add)
    - private_static_funcs (to add)
    - private_static_vars (to add)
    - friend_funcs (should we remove this?)
    - related
    -- I think friend functions and classes should automatically be labeled "related", unless they have an explicit `\relates` command.

Note:
sections contains the section headers, used only to generate the table of contents for classes/structs, files, namespaces and modules.

---

# Templates

Index pages:
- `classes.html`
- `files.html`
- `modules.html`
- `namespaces.html`
- `pages.html`

Reference pages:
- `class.html`
- `example.html` -> this is the only one we don't yet implement here
- `file.html`
- `module.html`
- `namespace.html`
- `page.html`
- `struct.html`
- `union.html` -> do we want to keep these inline?

TODO: If we keep unions inline, then we should also put structs and classes that only have public
member variables inline.

---

# Variables

All pages can define:
- `PROJECT_NAME`
- `PROJECT_BRIEF`
- `MAIN_PROJECT_URL`
- `PROJECT_LOGO`
- `STYLESHEETS`
- `FAVICON`
- `SEARCH_DISABLED`
- `SEARCH_BASE_URL`
- `SEARCH_EXTERNAL_URL`
- `SEARCH_HELP`
- `SEARCH_DOWNLOAD_BINARY`
- `SEARCHDATA_FORMAT_VERSION` (required)
- `THEME_COLOR`
- `HTML_HEADER`
- `LINKS_NAVBAR1`
- `LINKS_NAVBAR2`
- `PAGE_HEADER`
- `FILENAME` (required)
- `FINE_PRINT`

All reference pages define:
- `compound`
File/module/namespace reference pages, `compound` contains:
- `prefix_wbr`
- `brief`
- `sections`
- `modules`
- `files`
- `namespaces`
- `classes`
- `aliases`
- `variables`
- `variables`
- `macros`
- `description`
- `has_enum_details`
- `has_alias_details`
- `has_func_details`
- `has_var_details`
- `has_macro_details`
Class/struct/union reference pages, `compound` contains:
- `breadcrumb`
- `prefix_wbr`
- `kind`
- `templates`
- `include`
- `is_final`
- `since`
- `brief`
- `has_template_details`
- `sections`
- `public_types`
- `public_static_funcs`
- `typeless_funcs`
- `public_funcs`
- `public_static_vars`
- `public_vars`
- `protected_types`
- `protected_static_funcs`
- `protected_funcs`
- `protected_static_vars`
- `protected_vars`
- `private_funcs`
- `groups`
- `friend_funcs`
- `related`
- `base_classes`
- `derived_classes`
- `description`
- `has_enum_details`
- `has_alias_details`
- `has_func_details`
- `has_var_details`
- `has_macro_details`
Page reference pages, `compound` contains:
- `breadcrumb`
- `footer_navigation`
- `since`
- `brief`
- `sections`
- `description`

All index pages define:
- `index`
Classes/Namespaces index pages, `index` contains:
- `symbols`
Files index pages, `index` contains:
- `files`
Modules index pages, `index` contains:
- `modules`
Pages index pages, `index` contains:
- `pages`

For Entries:

alias.has_details
alias.base_url
alias.id
alias.templates
alias.name
alias.type
alias.args
alias.deprecated
alias.is_protected
alias.since
alias.brief
alias.include
alias.is_using
alias.has_template_details
alias.description

class.templates
class.kind
class.url
class.name
class.is_protected
class.is_final
class.is_virtual
class.deprecated
class.since
class.brief

enum.has_details
enum.base_url
enum.id
enum.is_strong
enum.name
enum.type
enum.values
enum.deprecated
enum.is_protected
enum.since
enum.brief
enum.include
enum is inside
enum.description
enum.has_value_details

file.url
file.name
file.deprecated
file.since
file.brief

function.has_details
function.base_url
function.id
function.templates
function.prefix
function.type
function.name
function.params
function.suffix
function.deprecated
function.is_protected
function.is_slot
function.is_private
function.is_signal
function.is_defaulted
function.is_deleted
function.is_explicit
function.is_final
function.is_override
function.is_pure_virtual
function.is_virtual
function.is_constexpr
function.is_conditional_noexcept
function.is_noexcept
function.since
function.brief
function.include
function.has_template_details
function.has_param_details
function.return_value
function.return_values
function.exceptions
function.description

macro.has_details
macro.base_url
macro.id
macro.name
macro.params
macro.deprecated
macro.since
macro.brief
macro.include
macro.has_param_details
macro.return_value
macro.description

module.url
module.name
module.deprecated
module.since
module.brief

namespace.url
namespace.name
namespace.is_inline
namespace.deprecated
namespace.since
namespace.brief

variable.has_details
variable.base_url
variable.id
variable.templates
variable.is_static
variable.type
variable.name
variable.deprecated
variable.is_protected
variable.is_constexpr
variable.since
variable.brief
variable.include
variable.has_template_details
variable.description

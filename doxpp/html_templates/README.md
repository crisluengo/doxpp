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
- `enums`
- `aliases`
- `functions`
- `variables`
- `macros`
- `doc`
- `has_enum_details`
- `has_alias_details`
- `has_function_details`
- `has_variable_details`
- `has_macro_details`
Class/struct/union reference pages, `compound` contains:
- `breadcrumb`
- `prefix_wbr`
- `kind`
- `templates`
- `include`
- `final`
- `since`
- `brief`
- `has_template_details`
- `sections`
- `base_classes`
- `derived_classes`
- `typeless_functions`
- `groups`
- `public_types`
- `public_functions`
- `public_vars`
- `public_static_functions`
- `public_static_vars`
- `protected_types`
- `protected_functions`
- `protected_vars`
- `protected_static_functions`
- `protected_static_vars`
- `private_types`
- `private_functions`
- `private_vars`
- `private_static_functions`
- `private_static_vars`
- `related`
- `doc`
- `has_enum_details`
- `has_alias_details`
- `has_function_details`
- `has_variable_details`
- `has_macro_details`
Page reference pages, `compound` contains:
- `breadcrumb`
- `footer_navigation` # TODO
- `since` # TODO
- `brief`
- `sections`
- `doc`
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

index.symbols.member_type
index.symbols.page_id
index.symbols.name
index.symbols.is_inline # TODO
index.symbols.deprecated
index.symbols.since # TODO
index.symbols.brief
index.symbols.children
index.symbols.final
index.files.name
index.files.children # iff directory
index.files.page_id
index.files.deprecated # TODO
index.files.since # TODO
index.files.brief
index.modules.page_id
index.modules.name
index.modules.deprecated # TODO
index.modules.since # TODO
index.modules.brief
index.modules.children
index.pages.children
index.pages.page_id
index.pages.title
index.pages.deprecated # TODO
index.pages.since # TODO
index.pages.brief

Note:
- `sections` contains the section headers, used only to generate the table of contents for classes/structs, files, namespaces and modules.

For Entries:

alias.has_details
alias.page_id
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
alias.is_using # TODO
alias.has_template_details
alias.doc

class.templates
class.kind
class.page_id
class.name
class.is_protected
class.final
class.is_virtual
class.deprecated
class.since
class.brief

enum.has_details
enum.page_id
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
enum.doc
enum.has_value_details

file.page_id
file.name
file.deprecated
file.since
file.brief

function.has_details
function.page_id
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
function.final
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
function.doc

macro.has_details
macro.page_id
macro.id
macro.name
macro.params
macro.deprecated
macro.since
macro.brief
macro.include
macro.has_param_details
macro.return_value
macro.doc

module.page_id
module.name
module.deprecated
module.since
module.brief

namespace.page_id
namespace.name
namespace.is_inline
namespace.deprecated
namespace.since
namespace.brief

variable.has_details
variable.page_id
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
variable.doc

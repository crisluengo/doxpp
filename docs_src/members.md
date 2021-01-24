\page members Detailed description of fields for C++ members

Each member is a dictionary with the following fields:

- \ref members_common_id: unique identifier
- \ref members_common_name: member name, with path from project root
- "brief": brief description (see \ref json_output_brief_doc)
- "doc": full documentation (see \ref json_output_brief_doc)
- \ref json_output_sections: (ID, title, level) for sections in "doc"
- \ref json_output_anchors: IDs of anchors in "doc"
- \ref members_common_member_type: member type 
- "parent": ID of the parent member
- \ref members_common_relates: ID of a class/struct that the member relates to
- \ref members_common_header: ID of the header file where the member is declared
- \ref members_common_group: group ID or name 
- "deprecated": `true` or `false` depending on if the member has a `[[deprecated]]` attribute

Additionally, the dictionary will contain other fields that depend on the "member_type"
value:

- \ref member_alias
- \ref member_class
- \ref member_enum
- \ref member_enumvalue
- \ref member_function
- \ref member_function_member
- \ref member_macro
- \ref member_namespace
- \ref member_union
- \ref member_variable
- \ref member_variable_field
- \ref member_variable_bitfield

\section members_common Common fields

\subsection members_common_id "id"
This is a unique identifier. When the member is referenced, a link to its ID is used.

Member IDs are not unrecognizable hash codes as Doxygen does it, but simply created from the fully
qualified name and parameters, guaranteeing uniqueness. For example:

- `int ns::foo()`                     ⇒ `"ns-foo"`
- `int ns::foo(int, double)`          ⇒ `"ns-foo-int--double-"`
- `int ns::foo(int&, double const&)`  ⇒ `"ns-foo-int-L-double-CL"`
- `class ns::bar`                     ⇒ `"ns-bar"`
- `ns::bar::bar(float*)`              ⇒ `"ns-bar-bar-float-P"`


\subsection members_common_name "name"
Name of the member. The fully qualified name can be obtained by iterating through the
"parent" links and prepending their names.

\subsection members_common_member_type "member_type"
The type of the member, one of:

- `"alias"`
- `"class"`
- `"enum"`
- `"enumvalue"`
- `"function"`
- `"macro"`
- `"namespace"`
- `"struct"`
- `"union"`
- `"variable"`

\subsection members_common_relates "relates"
ID of a class/struct that the member relates to. The class/struct will list this member in its "related"
list. This value can only be set in functions, variables, enums, aliases and macros.

\subsection members_common_header "header"
ID of the header file where the member is declared. If the declaration appears in multiple files, the first
one it was encountered in will be used.

\subsection members_common_group "group"
For namespace members, ID of the group that this member belongs to. If an empty string,
the member doesn't belong to any groups.

For class or struct members, the header text for the group. Can be an empty string if no
grouping is used.

For members of type `"enumvalue"` (enum members), the group is always the empty string.


\section member_alias Alias-specific fields

If the member is an alias (`using` or `typedef` declaration), then it additionally has the
following fields:

- "templated": `true` if this is an alias template.
- "type": the type being aliased, see \ref member_type_dictionary.
- "oldfashioned": `true` if this is a `typedef` declaration, `false` if it is a `using` declaration.


\section member_class Class- or struct-specific fields

If the member is a class or struct, it additionally has the following fields:

- "templated": `true` if this is a class template
- "abstract": `true` if this is an abstract class (has a pure virtual member function)
- \ref member_class_bases: a list of base classes
- "derived": a list of strings, the IDs of derived classes
- "members": a list of dictionaries for the child members
- \ref member_class_related: a list of strings, the IDs of related members

The "members" list contains dictionaries of members. These members can be of type
alias, enum, function, variable, class, struct or union.

\subsection member_class_bases "bases"
A list of dictionaries listing the base classes. It contains the following fields:

- "typename": the fully qualified name of the base class.
- "id": ID of the type, if declared in the project being documented.
- "access": set to a string `"public"`, `"protected"` or `"private"`.

\subsection member_class_related "related"
A list of strings, the IDs of related members. These are not child members, but are related
to the class and their documentation could be shown together with that of the class' members.

The members listed here will have the ID of this class as their \ref members_common_relates field.


\section member_enum Enum-specific fields

If the member is an enum, it additionally has the following fields:

- "scoped": `true` if scoped enum (declared as `enum class`), or `false` if unscoped (a plain `enum`)
- "type": the type underlying the enumerator (`"int"`, `"short"`, `"char"`, etc.)
- "members": member dictionaries, these members should all be of type `"enumvalue`


\section member_enumvalue Enumvalue-specific fields

If the member is an enumvalue (a child of an enum), it additionally has the following field:

- "value": the integer value of the enumerator constant


\section member_function Function-specific fields

If the member is a function, it additionally has the following fields:

- "templated": `true` if this is a function template
- "constexpr": `true` if this is a `constexpr` function
- "noexcept": `true` if the function is marked `noexcept`
- "return_type": the function's return type, see \ref member_type_dictionary
- \ref member_function_arguments: the function's arguments

For constructors, destructors and conversion functions (see the field "method_type"), "return_type" is empty.

\subsection member_function_arguments "arguments"
A list of dictionaries listing the input arguments. It contains the standard "type" fields
(see \ref member_type_dictionary) as well as the following fields:

- "name": the name of the argument
- "default": the default value for the argument (as a string)


\section member_function_member Function-specific fields, if class or struct member

If the function is a class or struct member, it additionally has the following fields:

- "static": `true` or `false` depending on if the function is declared static or not
- "virtual": `true` or `false` depending on if the function is declared virtual or not
- "pure_virtual": `true` or `false` depending on if the function is pure virtual or not
- "final": `true` or `false` depending on if the function is marked `final`
- "override": `true` or `false` depending on if the function is marked `override`
- "const": `true` or `false` depending on if the function is declared const or not
- "access": set to a string `"public"`, `"protected"` or `"private"`
- "method_type": set to a string `"method"`, `"conversionfunction"`, `"assignmentoperator"`,
  `"constructor"` or `"destructor"`
- "explicit": `true` or `false` depending on if the function is marked `explicit`
  (exists only if "method_type" is either `"conversionfunction"` or `"constructor"`)

\section member_macro Macro-specific fields

If the member is a macro, it additionally has the following field:

- "macro_params": list of strings containing macro parameters, if given

For a macro, the `"parent"` field is always the empty string.


\section member_namespace Namespace-specific fields

If the member is a namespace, it additionally has the following fields:

- "inline": `true` for inline namespaces
- "members": a list of dictionaries for the child members

Child members can be anything except macros.


\section member_union Union-specific fields

If the member is a union, it additionally has the following fields:

- "templated": `true` if this is a union template.
- "members": a list of dictionaries for the child members
- \ref member_class_related: a list of strings, the IDs of related members

The "members" list contains dictionaries of members. These members can be of type
alias, enum, function, variable, class, struct or union.


\section member_variable Variable-specific fields

If the member is a variable, it additionally has the following field:

- "type": the variable's type, see \ref member_type_dictionary
- "static": `true` or `false` depending on if the variable is declared `static` or not
- "constexpr": `true` if this is a `constexpr` value


\section member_variable_field Variable-specific fields, if class, struct or union member

If the variable is a class or struct or union member, it additionally has the following fields:

- "mutable": `true` or `false` depending on if the member is declared `mutable` or not
- "access": set to a string `"public"`, `"protected"` or `"private"`


\section member_variable_bitfield variable-specific fields, if bitfield

If the variable is a bitfield, it additionally has the following field:

- "width": The bitfield width (an integer)


\section member_template Template-specific fields

For members that are a class template, struct template, union template, function template or alias template,
the following field is additionally present:

- \ref member_template_parameters

\subsection member_template_parameters "template_parameters"
A list of dictionaries, one for each template parameter. Each of these dictionaries
contains the following fields:

- `"name"`: name of template parameter
- `"type"`: type of template parameter: the string `"type"`, or a dictionary encoding
  the type in case of a non-type template parameter, see \ref member_type_dictionary
- `"default"`: a type dictionary for type parameters, a string for non-type parameters,
  or `null` (translates to `None` in Python) if no default is given

For example, for `template<typename A>`, "type" will be equal to `"type"`, whereas
for `template<int A>`, "type" will be a dictionary `{"typename": "int", "id": "", "qualifiers": ""}`.

\section member_type_dictionary The type dictionary

Types are encoded as a dictionary with the following fields:

- "typename": name of the type
- "id": ID of the type, if declared in the project being documented
- "qualifiers": qualifiers (as a string)

The type could be rendered in Markdown as follows: `[<typename>](#<id>) <qualifiers>`.

If the type represents a function prototype, "typename" is a full representation,
but the dictionary will additionally contain the following fields:

- "retval": type dictionary for the function's return value
- "arguments": list of type dictionaries for the function arguments

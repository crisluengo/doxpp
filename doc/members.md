# Members

These are the member types that will be output by dox++, and how they nest.

- `namespace`
    - can contain anything except `macro`
- `class` or `struct`
    - `function`
    - `variable`
    - Can also contain `class`, `struct`, `union`, `enum`, `alias`.
- `union`
    - `variable`
- `enum`
    - `enumvalue`
- `alias` (identical for `using` and `typedef` style aliases, we don't distinguish them)
- `function`
- `variable`
- `macro`

Below we give a description of all the dictionary fields for each of these types of member.


## Common fields

### "id" (string)

This is a unique identifier. When the member is referenced, a link to its ID is used.

### "name" (string)

Name of the member. The fully qualified name can be obtained by iterating through the
"parent" links and prepending their names.

### "brief" (string)

A brief description, typically the first line of the documentation block for the member.
Should be rendered through a Markdown processor.

This description can be shown in a list of members.

### "doc" (string)

The full documentation, excluding the first line, which is in `"brief"`.['derived-class-member-id', 'derived-class-member-id', ...]
Should be rendered through a Markdown processor.

### "sections" (list)

List of tuples: (ID, level) for all sections present in the "doc" string.

### "anchors" (list)

List of strings with anchor IDs present in the "doc" string.

### "member_type" (string)

One of:
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

### "parent" (string)

ID of the parent member.

### "relates" (string)

ID of a class/struct that this member relates to. The class/struct will list this member in its "related"
list. This value can only be set in functions, variables, enums, aliases and macros.

### "header" (string)

ID of the header file where the member is declared. If the declaration appears in multiple files, the first
one it was encountered in will be used.

### "group" (string)

For namespace members, ID of the group that this member belongs to. If an empty string,
the member doesn't belong to any groups.

For class or struct members, the header text for the group. Can be an empty string if no
grouping is used.

For members of type `"enumvalue"` (enum members), the group is always the empty string.

### "deprecated" (boolean)

`true` or `false` depending on if the member has a `[[deprecated]]` attribute.


## alias-specific fields

### "type" (dictionary)

See below under "The type dictionary".


## class- or struct-specific fields

### "templated" (boolean)

`true` if this is a class template.

### "abstract" (boolean)

`true` if this is an abstract class (has a pure virtual member function).

### "bases" (list)

A list of dictionaries listing the base classes. It contains the following fields:
- `"typename"` (string): the fully qualified name of the base class.
- `"id"` (string): ID of the type, if declared in the project being documented.
- `"access"` (string): set to a string `"public"`, `"protected"` or `"private"`.

### "derived" (list)

A list of strings, the IDs of derived classes.

### "members" (list)

The list of dictionaries for the child members.

### "related" (list)

A list of strings, the IDs of related members. These are not child members, but are related
to the class and their documentation could be shown together with that of the class' members.


## enum-specific fields

### "scoped" (boolean)

`true` if scoped enum (declared as `enum class`), or `false` if unscoped (a plain `enum`).

### "type" (string)

The type underlying the enumerator (`"int"`, `"short"`, `"char"`, etc.)

### "members" (list)

Member dictionaries. These members should all be of type `"enumvalue`.


## enumvalue-specific fields

### "value" (integer)

The value of the enumerator constant.


## function-specific fields

### "templated" (boolean)

`true` if this is a function template.

### "constexpr" (boolean)

`true` if this is a `constexpr` function.

### "noexcept" (boolean)

`true` if the function is marked `noexcept`.

### "return_type"  (dictionary)

The function's return type. See below under "The type dictionary".

### "arguments" (list)

A list of dictionaries listing the input arguments. It contains the standard "type" fields
(see below under "The type dictionary") as well as the following fields:
- `"name"` (string): The name of the argument.
- `"default"` (string): The default value for the argument.


## function-specific fields, if class or struct member

If the function is a class or struct member, it additionally has the following fields:

### "static" (boolean)

`true` or `false` depending on if the function is declared static or not.

### "virtual" (boolean)

`true` or `false` depending on if the function is declared virtual or not.

### "pure_virtual" (boolean)

`true` or `false` depending on if the function is pure virtual or not.

### "const" (boolean)

`true` or `false` depending on if the function is declared const or not.

### "access" (string)

Set to a string `"public"`, `"protected"` or `"private"`.

### "method_type" (string)

Set to a string `"method"`, `"conversionfunction"`, `"constructor"` or `"destructor"`.


## macro-specific fields

For a macro, the `"parent"` field is always the empty string.

### "macro_params" (list)

List of strings containing macro parameters, if given.


## namespace-specific fields

### "members" (list)

The list of dictionaries for the child members.


## union-specific fields

### "members" (list)

The list of dictionaries for the child members.


## variable-specific fields

### "type" (dictionary)

The variable's type. See below under "The type dictionary".

### "static" (boolean)

`true` or `false` depending on if the variable is declared static or not.

### "constexpr" (boolean)

`true` if this is a `constexpr` value.


## variable-specific fields, if class, struct or union member

If the variable is a class or struct or union member, it additionally has the following fields:

### "mutable" (boolean)

`true` or `false` depending on if the member is declared mutable or not.

### "access"

Set to a string `"public"`, `"protected"` or `"private"`.


## variable-specific fields, if bitfield

If the variable is a bitfield, it additionally has the following field:

### "width" (integer)

The bitfield width.


## template-specific fields

For members that are a class template, struct template, or function template, the following
field is additionally present:

### "template_parameters" (list)

A list of dictionaries, one for each template parameter. It contains the following
fields:
- `"name"` (string): name of template parameter.
- `"type"`: Type of template parameter: `"type"` or a dictionary encoding
  the type in case of a non-type template parameter, see below under "The type dictionary".
- `"default"`: A type dictionary for type parameters, a string for non-type parameters,
  or `null` (translates to `None` in Python) if no default is given.

For example, for `template<typename A>`, `"type"` will be equal to `"type"`, whereas
for `template<int A>`, `"type"` will be `"int"`.

## The type dictionary

Types are encoded as a dictionary with the following fields:
- `"typename"` (string): name of the type.
- `"id"` (string): ID of the type, if declared in the project being documented.
- `"qualifiers"` (string): qualifiers.

The type could be rendered in Markdown as follows: `[typename](#id) qualifiers`.

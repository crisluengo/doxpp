# Members

These are the member types that will be output by dox++, and how they nest.

- `namespace`
    - can contain anything
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

### "member_type" (string)

One of:
- `"alias"`
- `"class"`
- `"enum"`
- `"enumvalue"`
- `"function"`
- `"namespace"`
- `"struct"`
- `"union"`
- `"variable"`

### "parent" (string)

ID of the parent member.

### "file" (string)

File where the member is declared. If the declaration appears in multiple files, the first
file it was encountered will be used.

### "group" (string)

ID of the group that this member belongs to. If an empty string, the member doesn't belong
to any groups.

### "deprecated" (boolean)

`true` or `false` depending on if the member has a `[[deprecated]]` attribute.


## alias-specific fields

### "type" (dictionary)

The type dictionary encoding the type aliased, see below.


## class- or struct-specific fields

### "templated" (boolean)

`true` if this is a class template.

### "bases" (list)

A list of dictionaries listing the base classes. It contains the following fields:
- `"typename"` (string): the fully qualified name of the base class.
- `"access"` (string): set to a string `"public"`, `"protected"` or `"private"`.

### "derived" (list)

A list of strings, the IDs of derived classes.

### "members" (list)

The list of dictionaries for the child members.


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

### "return_type" (dictionary)

The type dictionary encoding the function's return type, see below.

### "arguments" (list)

A list with the type dictionaries encoding the input arguments, see below.

These dictionaries carry an additional `"name"` field, for the argument name.


## function-specific fields, if class or struct member

If the function is a class or struct member, it additionally has the following fields:

### "static"

### "virtual"

### "pure_virtual"

### "const"

### "access" (string)

Set to a string `"public"`, `"protected"` or `"private"`.

### "method_type"


## namespace-specific fields

### "members" (list)

The list of dictionaries for the child members.


## union-specific fields

### "members" (list)

The list of dictionaries for the child members.


## variable-specific fields

### "type" (dictionary)

The type dictionary encoding the variable's type, see below.

### "static" (boolean)

`true` or `false` depending on if the variable is declared static or not.


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
- `"name"`: (string) name of template parameter
- `"brief"`: (string) the short description of the parameter
- `"doc"`: (string) the documentation for the parameter
- `"type"`: (string) type of template parameter: `"type"` or `"nontype"`
- `"default_type"`: A type dictionary

## The "type" dictionary

The two elements of this dictionary can be combined to form the full type specification:
```
full_type = type['typename'] + ' '.join(type['qualifiers'])
```
The resulting string might have some superfluous spaces that can be removed if one is so inclined.

## "typename" (string)

The name of the type. Can contain a link in Markdown format (linking to the ID of the type,
if it is described in the documentation).

## "qualifiers" (list)

A list of strings, specifying the type's qualifiers. Strings can be one of:
- `'const'`
- `'*'`
- `'&'`
- `'&&'`
- `'[]'`

# JSON Remediator

JSON Remediator traverses a target JSON and visits each element while
applying user supplied functions. As JSON remediator visits each element
in the target (recall that JSON elements may contain sub-elements), it
executes user supplied functions before visiting sub-elements and/or after.
JSON Remediator can be implemented in any programming language. In this
guide, we use the Python implementation.

## Quick Start
Let's say you have a target JSON ("sample-target.json") such as
```json
{
  "k1": 30,
  "k2": 40,
  "h": {
    "k3": 15,
    "j": 20
  }
}
```
and you want to take the sum of all key values with key names starting with
`k` . To accomplish this task using JSON Remediator, you can write a user function
```python
def sum_k(target, companion, params, workspace):
    workspace["_output"] += target
```
and define remediation descriptors in a "sample-descriptors.json" file as,
```json
[
  {
    "path": ".*/k[0-9]*",
    "descriptor": {
      "@after": "sum_k"
    }
  }
]
```
With the proper PYTHONPATH settings, the remediation can be done by calling,
```shell script
python -m jsonreme.remediator -r sample-descriptors.json sample-target.json
...
85
```
where 85 is the sum. It is that simple. The remediation descriptor simply says that - when encountering a JSON element which JSON
pointer matches the `path` pattern, apply `sum_k` function after visiting the element.
## Target and Companion
JSON Remediator only traverses the target JSON. If a companion is given, it
should have the same layout as the target JSON and may have different values.
While JSON Remediator traverses the target, it tries to traverse the companion
simultaneously and pass the corresponding sub-element to user supplied functions.

For example, if the target is
```json
{
  "a": "x",
  "b": "y"
}
```
and the companion is
```json
{
  "a": "t",
  "c": "s"
}
```
when JSON Remediator visits `/a`, in addition to `"x"` in the target JSON,
`"t"` in the companion is also passed to user supplied
functions. However, when JSON Remediator visits `/b`, no sub-element from
the companion is passed to user supplied functions because the companion does
not have a corresponding `/b`.

## User Supplied Remediation Functions
Remediation functions must have the signature as follows,
```python
def <function name>(target, companion, params, workspace):
```
where `target` is a sub-element of the target JSON, `companion` is the corresponding
sub-element of the companion if exists or None, `params` is some parameters provided
through a remdiation descriptor (see below), and `workspace` is a dictionary for
user functions to store any data.
## Remediation Descriptors
A remediation descriptor contains two entries. The `path` entry specifies a regex
pattern and the `descriptor` entry specifies a user supplied functions. When JSON
Remediator traverse the target JSON, the current element is identified by its JSON
pointer (see [RFC 6901](https://tools.ietf.org/html/rfc6901)). The JSON pointer
format is similar to a partial URI path.
JSON Remediator attempts to match the current element JSON pointer to `path` regex
pattern. If there is a match, the corresponding `descriptor` functions are applied
to this element. A remediation descriptor has the form of,
```text
{
  "path": "<regex pattern|required>",
  "descriptor": {
    "@before": "<module_name.function_name|optional>",
    "@after": "<module_name.function_name|optional>",
    "@params": {<descriptor parameters|optional>},
  }
}
```
where `@before` function is applied before the sub-elements of the current element
are traversed and `@after` function is applied after the sub-elements of the
current element are traversed. `@params` is a dictionary of descriptor defined
parameters that are passed to `@before` and `@after` functions.

JSON Remediator uses a list of remediation descriptors,
```text
[
  {<remediation descriptor 1>},
  {<remediation descriptor 2>},
  ...
]
```
If the current element JSON pointer matches multiple remediation descriptors, all
matched descriptors are applied to the element in the order of their positions in
the remediation descriptor list.
## Convenient Format of Remediation Descriptors
Although the remediation descriptor format described above is the canonical format,
there is a convenient format that may be more visually pleasing to some users. The
convenient format tries to match the remediation descriptors to the layout of the
target JSON. For example, the quick-start target,
```json
{
  "k1": 30,
  "k2": 40,
  "h": {
    "k3": 15,
    "j": 20
  }
}
```
has a convenient format of its remediation descriptors as
```json
{
  "@descriptors": {
    "k1": {
      "@after": "sum_k"
    },
    "k2": {
      "@after": "sum_k"
    },
    "h": {
      "k3": {
        "@after": "sum_k"
      }
    }
  }
}
```
The convenient format may help organizing descriptors in some applications. The
convenient format is converted to the canonical format internally in JSON
Remediator.
## Workspace
A workspace is provided for user supplied functions to store data. JSON Remediator
also stores data in the workspace. User supplied functions may use this workspace
for data sharing.

Any key name starts with "\_\_" (double underscore) is
reserved for JSON Remediator. User supplied functions may read them, but not update
them. Any key name starts with "\_" (single underscore) is defined by JSON
Remediator. User supplied functions may update them. JSON Remediator may read them.

| Parameter Name | Description |
| ---------------|-------------|
| \_\_crp | JSON pointer to the current element|
| _output | CLI prints out this value after remediation |
In addition to above predefined parameters, the return value of every user supplied
function call is stored in the workspace. The key's format is
```text
<current element JSON pointer>.<@before|@after>$<function module name>.<function name>
```
For example, `/k1.@after$sample_sum.sum_k`. Later function calls may query earlier function return values through these keys.
## Embedded Usage
When used as a library, JSON Remediator can be called as
```python
    remediator = jsonreme.remediator.JsonRemediator(descriptors)
    workspace = remediator.remediate(target, companion, env)
```
After the remediation, the workspace is returned for further processing if needed.
## CLI Usage
When used as a standalone CLI, JSON Remediator can be called as
```shell script
usage: python3 -m jsonreme.remediator [-h] [-r REMEDIATION_DESCRIPTORS] [-c COMPANION] [-d] target

JSON remediation engine.

positional arguments:
  target

optional arguments:
  -h, --help            show this help message and exit
  -r REMEDIATION_DESCRIPTORS, --remediation-descriptors REMEDIATION_DESCRIPTORS
                        Remediation descriptors in the form of a list of a
                        dictionary.
  -c COMPANION, --companion COMPANION
                        Companion JSON.
  -e ENV, --env ENV     Global parameter JSON file.
  -d, --drift           show drifts between the target and the companion
```
## Supported Programming Language
Currently supported programming is Python 3.x.
## Use JSON Remediator in Desired State Drift Detection and Remediation
Desired state management is an approach used in complex and large scale computer systems. It is
centered around defining a desired state of the system and maintaining the system to stay at
the desired state. When there is an intention change to the system, the change is first made to
the desired state. Then remediation is applied to the system so that the system is consistent to
the new desired state.

In utilizing JSON Remediator in desired state management, a desired state is represented by
the target JSON. The remediation steps are represented by remediation descriptors. Optionally,
the current state can be represented by the companion JSON. The current state is generally not
needed as it can be obtained by user supplied functions in remediation descriptors.
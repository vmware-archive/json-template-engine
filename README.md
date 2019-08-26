# json-template-engine

## Overview
JSON template engine is an embeddable tool for parameterizing JSON (or equivalant) data. JSON template engine takes
a parameterized template and binding data with parameter value assignments and resolve them to
a new JSON data with parameters substituted by their values. Both templates and binding data are valid
JSON data. JSON template engine is not a general purpose text transformation engine. It can only
transform JSON data to new JSON data. JSON template engine can be used as a library or CLI. JSON
template engine is programming language independent. Currently we support Python 3.x and Java.
Throughout this guide, we use Python whenever we show examples. We only call out Java when there are
significant differences.

## Getting started
- Download a language specific template engine distribution.
- For Python, add the path of the library to PYTHONPATH environmental variable.
- For Java, add the path of the library to the class path of a JVM.
- For C++, use the header files directly or use it as a CLI.

## Try it out
Make copies of samples/getting_started/hello_world_template.json and samples/getting_started/hello_world_binding_data.json or save
```
  {
    "message": "${greetings}"
  }
```
as "hello_world_template.json" and 
```
  {
    "greetings": "Hello World!"
  }
```
as "hello_world_bidning_data.json".

For Python, run the following CLI command
```
    python -m jsonteng.template_engine -b hello_world_binding_data.json hello_world_template.json
```
The output should be
```
  {
    "message": "Hello World!"
  }
```
## Build

- Clone the git repository <code>git clone git@github.com:vmware/json-template-engine.git </code>
- Change directory to `json-template-engine/templating/core`.
- For Python, run <code>build_py.sh</code>.
- For Java, run <code>gradlew clean build publishToMavenLocal</code>.
- Python wheel output is located in `build/dist`.
- Java jar file is located in `build/libs`.
- For C++, run <code>make clean cli</code>. The header files can be included directly.
- Additional tags are in `json-template-engine/templating/tag_contributions.
- To build everything, run <code> =./build_all.sh</code>.


## Documentation
### CLI Support

CLI syntax for Python
```
usage: template_engine.py [-h] -b BINDING_DATA_RESOURCES [-e ENV] [-v] [-s] [-d] [-r] [-t TAGS] main_template

JSON template engine.

positional arguments:
  main_template

optional arguments:
  -h, --help            show this help message and exit
  -b BINDING_DATA_RESOURCES, --binding-data-resources BINDING_DATA_RESOURCES
                        a comma separated list of binding data resource
                        locators
  -e ENV, --env ENV     global binding data
  -v, --verbose         increase output verbosity
  -s, --stats           show stats
  -d, --debug           show debug info
  -r, --raw             unformatted output
  -t TAGS, --tags TAGS
                        common separated tag list
```

Resource locators could be JSON data. The implementation first tries to locate JSON data through resource locators. If not successful, it treates resource locators as JSON data. Global binding data is a JSON object with parameter assignments. "--tags" are for advanced usage when extending JSON template engine functionalities is needed through custom tags. Each tag is specified by a canonical class path to the tag implementation class.

### Template Specification

Templates are valid JSON values. They are parameterized JSON data. Likewise, binding data are also
valid JSON values. They specify parameter values. In binding data, parameter values may contain references to other parameters. The indirect references enable us to write concise binding data JSON.

A parameter reference has the format of
```
parameter reference = "${", paramter name, "}" ;
parameter name      = { [ parameter name ] parameter reference [ parameter name ]  } ;
parameter name      = identifier, { ., identifer} ;
identifier          = string ;
identifier          = string, "[", unsigned integer, "]" ;
```

Referencing a binding data value is similar to referencing a JSON value in JavaScript. For example, the following binding data,

```
{
  "x": [{
    "y": {
      "z": 1
    }
  }]
}
```

<code>${x[0].y.z}</code> returns 1.

With the indirect and nested references, we need to be specific on how parameter references are resolved. Parameter references are resolved in an eager manner. For example, with

```
{
  "x": [{
    "y.z": 2,
    "y": {
      "z": 1
    }
  }]
}
```
the same parameter reference would return 2 and "z" becomes shawdowed and not reachable.

Parameter references are always resolved in a late binding fasion. Intermediate resolved parameters are not stored.

As shown in CLI syntax, it is possible to specify a list of binding data. When resolving parameter
references, the list is searched from index 0 until the first satisfied match. As shown later, some
tags tempoarily alters the list to achieve the desired result.

Although simple parameter substitutions are useful, it is often that we need to manipulate templates
beyond simple parameter substitutions. Many template engines have powerful features in tags and other
means for generating arbitrary text stream. However, we restrict this template engine to only generate
JSON for simplicity and readability. We use "tags" to archieve features that simple parameter
substitutions cannot achieve. Tags are special JSON arrays and objects. If a tag is in the form of a JSON list,
the first element of the list must be a string and the first character of the string must be a "#". If the tag is in the form of a JSON object, the object key must be a string and the first character of the string must be a "#". The object value must be a list. The tag name is the character sequence after the "#". The rest of the array elements are tag parameters. When a tag is resolved, the result could be one of valid JSON values. A special internal return value is used to indicate that the tag resolves to nothing and therefore, the JSON value where the tag occupies is removed. A tag name may optionally contain a label. This allows the same same tag is used in different keys in a JSON object. The tag name has a format of "#<tag>:<label>". For example, "#one-of:first" and "#one-of:second". Only the <tag> part is significant for mapping the tag to its function. In above example, both "#one-of:first" and "#one-of:second" are processed by the same tag processor.

Supported Tags

| TAG  | Usage | Example |
| ---- | ----- | ------- |
| #at  | Return a value at an index or name depending the object. | ["#at", [10, 11, 12], 1]|
| #exists | Check if a parameter is set. Returns True if a parameter is assigned a value.| ["#exists", "${x}"] |
| #for-each | Loop through an array and use the array element as the first binding data and apply it to a template.| ["#for-each", [{"x": 1}, {"x": 2}], "template.json"]|
| #len | Retun the length of a JSON value. | ["#at", [1, 2, 3]]|
| #one-of | Select a JSON value when condition is True. | ["#one-of", ["${x} == 1", "one"], "other"] |


## Contributing

The json-template-engine project team welcomes contributions from the community. If you wish to contribute code and you have not
signed our contributor license agreement (CLA), our bot will update the issue when you open a Pull Request. For any
questions about the CLA process, please refer to our [FAQ](https://cla.vmware.com/faq). For more detailed information,
refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## License
The Apache 2.0 license

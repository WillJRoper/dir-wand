# WAND: WAND Automates Nested Directories

[![workflow](https://github.com/WillJRoper/dir-wand/actions/workflows/python-app.yml/badge.svg)](https://github.com/WillJRoper/dir-wand/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

WAND is a Python CLI tool for creating a large number of directories from a single template and executing commands globally throughout every directory.

## Installation

To install WAND simply run

``` sh
pip install dir-wand
```

in the root directory of WAND. This will install the `dir-wand` CLI. 

## Using WAND to make arbitrarily many directories

To use WAND you first need have a template directory structure you want to make copies of. A template directory can include any number of subdirectories and files. WAND will correctly handle the copying of:

- Empty directories.
- Executables with the correct permissions.
- Softlinks.
- Human readable text files (e.g. `.txt`, `.yaml`, `.csv`, `.html`, etc.).
- Binary files.
- And many more...

Templates can include any number of "placeholder" values in file paths and inside text files. A placeholder is defined by a set of curly braces containing the place holder label (e.g. `{value1}`).

For example, your template directory might be:

```
└── simple_example_{num}/
    ├── simple_example_{num}.yaml
    ├── nested_dir/
    │   ├── some_text.txt
    │   └── another_nested_dir/
    │       └── another_another_dir/
    │           └── nested_file.txt
    └── empty_dir/
```

where `num` is one of the placeholders and we have a mixture of directories and files with and without placeholders in their name. 

To include placeholders in a file we can again use the curly brace notation. For instance, in this example we have `simple_example_{num}.yaml` which could contain:

``` yaml
PlaceHolders:
  run_number:       {num}
  run_directory:    simple_example_{num}
  variable:         {x}
  another_variable: {y}
  some_flag:        {flag}
```

To make copies of this template directory we can use the `dir-wand` CLI tool. `dir-wand` needs a set of values for each placeholder along with the path to the template directory, e.g.:

``` sh
dir-wand simple_example_{num}/ --root /where/to/put/copies/ --num 0-2 --x 1-3 --y 2-4 -flag 0 1 0
```

Here we've passed the filepath to the template directory (which can be an absolute or relative path), an optional root for the copies (if not given the copies will be made in the directory the command was run in) and a set of key-value pairs for each placeholder (of the form --key value). These values can be:

- The definition of an inclusive range using 2 dashes (e.g. `--num 0-2` will replace `num` with values of 0, 1, and 2).
- A list of values using 1 dash (e.g. `-flag 0 1 0` will replace `flag` with 0, 1, and 0).
- The path to a file containing a list of strings (Coming soon...).

NOTE: The number of values for each placeholder must be the same. If not, WAND will raise an error.

This will create 3 directories in `/where/to/put/copies/`:

```
├── simple_example_0/
│   ├── simple_example_0.yaml
│   ├── nested_dir/
│   │   ├── some_text.txt
│   │   └── another_nested_dir/
│   │       └── another_another_dir/
│   │           └── nested_file.txt
│   └── empty_dir/
├── simple_example_1/
│   ├── simple_example_1.yaml
│   ├── nested_dir/
│   │   ├── some_text.txt
│   │   └── another_nested_dir/
│   │       └── another_another_dir/
│   │           └── nested_file.txt
│   └── empty_dir/
└── simple_example_2/
    ├── simple_example_2.yaml
    ├── nested_dir/
    │   ├── some_text.txt
    │   └── another_nested_dir/
    │       └── another_another_dir/
    │           └── nested_file.txt
    └── empty_dir/
```

and `simple_example_0.yaml` will contain:

``` yaml
PlaceHolders:
  run_number:       0
  run_directory:    simple_example_0
  variable:         1
  another_variable: 2
  some_flag:        0
```

with the other files made accordingly.

## Running commands

Coming soon...

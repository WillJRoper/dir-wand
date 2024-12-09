# WAND: WAND Automates Nested Directories

[![workflow](https://github.com/WillJRoper/dir-wand/actions/workflows/python-app.yml/badge.svg)](https://github.com/WillJRoper/dir-wand/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/dir-wand.svg)](https://badge.fury.io/py/dir-wand)

<p align="center">
  <img src="https://github.com/WillJRoper/dir-wand/assets/40025495/8ad6d775-c7e8-45df-88bd-21511d6ce6f1" alt="wand-logo" height="300">
</p>

WAND is a Python CLI tool for creating a large number of directories from a single template and executing commands globally throughout every directory.

## Installation

To install WAND simply run

```sh
pip install dir-wand
```

in the root directory of WAND. This will install the `dir-wand` CLI.

## Using WAND to make arbitrarily many directories

WAND can efficiently make an arbitrary number of complex directory structures from a single template directory. This can be useful for creating a large number of directories with similar structures, such as for running many simulations, performance testing, or experiments. In the sections below we'll show how to create a template directory structure and use WAND to make copies of this structure with placeholders populated by a set of values.

### Creating a template

A template directory can include any number of subdirectories and files. WAND will correctly handle the copying of:

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

```yaml
PlaceHolders:
  run_number: { num }
  run_directory: simple_example_{num}
  variable: { x }
  another_variable: { y }
  some_flag: { flag }
```

where `num`, `x`, `y`, and `flag` are placeholders that will be replaced by values when making copies of the template directory.

### Making copies

To make copies of this template directory we can use the `dir-wand` CLI tool. `dir-wand` needs a set of values for each placeholder along with the path to the template directory, e.g.:

```sh
dir-wand --template simple_example_{num}/ --root /where/to/put/copies/ --num 0-2 --x 1-3 --y 2-4 -flag 0 1 0
```

Here we've passed the filepath to the template directory (which can be an absolute or relative path), an _optional_ root directory to contain the copies (if not given the copies will be made in the current working directory) and a set of key-value pairs for each placeholder (of the form --key value). These values can be:

- The definition of an inclusive range using 2 dashes (e.g. `--num 0-2` will replace `num` with values of 0, 1, and 2).
- A list of values using 1 dash (e.g. `-flag 0 1 0` will replace `flag` with 0, 1, and 0).
- The path to a file containing a list of strings using 2 dashes (for details see below).

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

```yaml
PlaceHolders:
  run_number: 0
  run_directory: simple_example_0
  variable: 1
  another_variable: 2
  some_flag: 0
```

with the other files made accordingly.

#### Using a file for values

Rather than explicitly stating the values for a placeholder, you can pass the path to a file containing a list of values. For example, if we have a file `values.txt` containing values split by newlines,

```
0
1
0
```

we could instead pass this file to the flag argument,

```sh
dir-wand --template simple_example_{num}/ --root /where/to/put/copies/ --num 0-2 --x 1-3 --y 2-4 --flag values.txt
```

which will create the same directories as before.

### Using a swap file

If you have a large number of placeholders or a large number of values for placeholders, it could be cumbersome to pass them all as arguments. Instead, you can pass a "swapfile", a yaml file defining the values to swap with each placeholder. If we have a swapfile `swapfile.yaml` containing:

```yaml
num:
  range: 0-2
x:
  list:
    - 1
    - 2
    - 3
y:
  range: 2-4
flag:
  file: values.txt
```

we can pass this file to the `--swapfile` argument like so,

```sh
dir-wand --template simple_example_{num}/ --root /where/to/put/copies/ --swapfile swapfile.yaml
```

ignoring the need to pass the placeholders as arguments explictly to get the same result as the calls detailed above.

### Creating a swap file

Of course, if we do have a lot of place holders, its still tedious to write out the swapfile. WAND streamlines this process by providing a method to create swapfiles containing all possible combinations of input swaps.

If we pass only the `--swapfile` argument alongisde and the swaps we want combined in our file. For instance:

```sh
dir-wand --swapfile swapfile.yaml --num 0-1 --num2 0-1
```

Will create a swapfile containing 4 sets of swaps (0, 0), (0, 1), (1, 0), and (1, 1) for `num` and `num2` respectively. The swaps defined here can also come from a file as shown above.

### Running commands after a copy

When making copies of a template directory, WAND can also run commands in each directory. This can be done by passing the `--run` argument followed by the command to run wrapped by `"`. For example:

```sh
dir-wand --template simple_example_{num}/ --root /where/to/put/copies/ --num 0-2 --x 1-3 --y 2-4 -flag 0 1 0 --run "echo 'Hello from simple_example_{num}'"
```

will create the directories as before and run the command `echo 'Hello from simple_example_{num}'` in each directory. This will output:

```
Hello from simple_example_0
Hello from simple_example_1
Hello from simple_example_2
```

These commands can be any valid shell command or even a script. The commands will be run on concurrent threads to ensure the main thread making the copies is not blocked so the world is your oyster!

## Using WAND to run commands in existing directories

WAND can also be used to run commands in existing directories with identical structures and "placeholder compliant" naming.

This can be done by passing the `--run` argument including placeholders and any required swaps (which can be defined in any of the ways detailed above including a swapfile). For example, if we assume the example template directory above is already made, where we have the directories (including all their contents):

```
├── simple_example_0/
├── simple_example_1/
└── simple_example_2/
```

Then we can run a command in each directory using:

```sh
dir-wand --run "cd simple_example_{num}; head -2 simple_example_{num}.yaml" --num 0-2
```

This will output the first 2 lines of each `simple_example_{num}.yaml` file in each directory. Note that any command passed to `--run` will be run in the current working directory.

## Runtime arguments

Invoking `dir-wand` with the `--help` flag (or not arguments at all) will display all possible options:

```
usage: dir-wand [-h] [--template TEMPLATE] [--root ROOT] [--run RUN] [--swapfile SWAPFILE] [--silent] [-- VALUE] [- VALUE [VALUE ...]]

Wave your Directory WAND and make magic happen.

options:
  -h, --help           show this help message and exit
  --template TEMPLATE  The template to use for the model.
  --root ROOT          The root directory for the outputs.
  --run RUN            A command to run in each copy once the copy is complete. The command will be run in the current working directory.
  --swapfile SWAPFILE  A yaml file defining the swaps for each placeholder.
  --silent             Suppress all WAND prints.
  -- VALUE             A key-value pair for a placeholder replacement. Should be in the form --key value, where key is the name ({name}) to replace in directory paths and files, and value is an inclusive range (1-5), or a filepath to a file contain a list.of values.
  - VALUE [VALUE ...]  A key-value pair for a placeholder replacement. Should be in the form -key value1 value2 value3, where key is the name ({name}) to replace in directory paths and files, and value is a list.
```

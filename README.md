# pymv

CLI wrapper of rope's module moving functionality. Depends on a slightly forked (hacked up) version of Rope - https://github.com/Ridecell/rope.


## Usage

```
usage: pymv [-h] [--dry-run] [--project-root-directory PROJECT_DIR]
            source_path destination_path [scoped_global_variable]

Move python files and folders, automatically updating import statements in dependent files.

positional arguments:
  source_path
  destination_path
  scoped_global_variable
                        Provide a Global variable/class/function name in source file to move to
                        destination. Allows for greater granularity when moving overscoped modules
                        that need to be split into 2 (or more) modules

optional arguments:
  -h, --help            show this help message and exit
  --dry-run
  --project-root-directory PROJECT_DIR
                        Root directory of the python project in which the files are being moved.
                        This defines the scope for which to search for affected import statements.
```

## Install

```
pip install git+https://github.com/Ridecell/rope pymv
```

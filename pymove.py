import argparse
import sys


def move(project_dir, src, dest, scoped_name=None, dry_run=False):
    pass


def main():
    arg_parser = argparse.ArgumentParser(description='Move python files and folders, automatically updating import '
                                                     'statements in dependent files.')
    arg_parser.add_argument('source_path', type=str)
    arg_parser.add_argument('destination_path', type=str)
    arg_parser.add_argument('scoped_global_variable', type=str, nargs='?', default=None,
                            help='Provide a Global variable/class/function name in source file to move to destination.'
                                 ' Allows for greater granularity when moving overscoped modules that need to be split '
                                 'into 2 (or more) modules')
    arg_parser.add_argument('--dry-run', action='store_true', dest='dry_run')
    arg_parser.add_argument('--project-root-directory', type=str, default='.', dest='project_dir',
                            help='Root directory of the python project in which the files are being moved. This defines'
                                 ' the scope for which to search for affected import statements.')
    args = arg_parser.parse_args(sys.argv[1:])

    if args.project_dir != '.':
        raise NotImplementedError('Support for a --project-root-directory other than the current working directory '
                                  '(specified as ".") is pending.')

    move(args.project_dir, args.source_path, args.destination_path, scoped_name=args.scoped_global_variable,
         dry_run=args.dry_run)


if __name__ == '__main__':
    main()

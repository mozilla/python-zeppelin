import os
import argparse
import json
import sys
from .new_converter import NewConverter
from .legacy_converter import LegacyConverter

def check_version(text, args, directory):
    if 'results' in text['paragraphs'][0]:
        return NewConverter(args.in_filename, args.out_filename,
                            directory)
    else:
        return LegacyConverter(args.in_filename, args.out_filename,
                               directory)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='in_filename', required=True,
                        help='Zeppelin notebook input file (.json)')
    parser.add_argument('-o', dest='out_filename',
                        help='Markdown output file (.md) (optional)')
    args = parser.parse_args()
    directory = ''

    if args.out_filename:
        directory = os.path.dirname(args.out_filename)
        args.out_filename = os.path.basename(args.out_filename)
        args.out_filename = os.path.splitext(args.out_filename)[0]
        args.out_filename = args.out_filename if args.out_filename else 'knowledge'
    else:
        args.out_filename = 'knowledge'

    try:
        with open(args.in_filename, 'rb') as raw:
            t = json.load(raw)
            full_path = os.path.join(directory, args.out_filename + '.md')
            with open(full_path, 'w') as fout:
                zeppelin_converter = check_version(t, args, directory)
                zeppelin_converter.convert(t, fout)

    except ValueError as err:
        print('ERROR: Invalid JSON format')
        sys.exit(1)


if __name__ == '__main__':
    main()

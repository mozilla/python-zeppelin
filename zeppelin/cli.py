import os
import argparse
import json
import sys
from .new_converter import NewConverter as nc
from .legacy_converter import LegacyConverter as lc


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
                if 'results' in t['paragraphs'][0]:
                    zeppelin_converter = nc(args.in_filename, args.out_filename,
                                            directory, 'anonymous', 'N/A', 'N/A')
                else:
                    zeppelin_converter = lc(args.in_filename, args.out_filename,
                                            directory, 'anonymous', 'N/A', 'N/A')

                zeppelin_converter.convert(t, fout)

    except ValueError as err:
        print(err)
        sys.exit(1)


if __name__ == '__main__':
    main()

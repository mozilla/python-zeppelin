import os
import argparse
from .converter import ZeppelinConverter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='in_filename', required=True,
                        help='Zeppelin notebook input file (.json)')
    parser.add_argument('-o', dest='out_filename', help='Markdown output file (.md) (optional)')
    args = parser.parse_args()
    directory = ''

    if args.out_filename:
        directory = os.path.dirname(args.out_filename)
        args.out_filename = os.path.basename(args.out_filename)
        args.out_filename = os.path.splitext(args.out_filename)[0]
        args.out_filename = args.out_filename if args.out_filename else 'knowledge'
    else:
        args.out_filename = 'knowledge'

    zeppelin_converter = ZeppelinConverter(args.in_filename, args.out_filename,
                                           directory, 'anonymous', 'N/A', 'N/A')
    zeppelin_converter.convert()


if __name__ == '__main__':
    main()

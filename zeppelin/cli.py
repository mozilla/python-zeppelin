from converter import ZeppelinConverter
import argparse

"""
Main entry point

"""
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='filename', required=True,
                        help='Zeppelin notebook input file (.json)')
    args = parser.parse_args()

    zeppelin_converter = ZeppelinConverter(args.filename, 'anonymous', 'N/A', 'N/A')
    zeppelin_converter.convert()


if __name__ == '__main__':
    main()

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import argparse
import json
import sys
from ..executors.notebook_executor import NotebookExecutor


def main():
    """Entry point.

    - Execute notebook
    - Save output to either file or display it in stderr
    - Display errors during the run if they exist
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='path_to_notebook_json', required=True,
                        help='Zeppelin notebook input file (.json)')
    parser.add_argument('-o', dest='output_path', default=sys.stdout,
                        help='Path to save rendered output file (.json) (optional)')
    parser.add_argument('-u', dest='zeppelin_url', default='localhost:8890',
                        help='Zeppelin URL (optional)')
    args = parser.parse_args()

    with open(args.path_to_notebook_json, 'rb') as notebook:
        try:
            t = json.load(notebook)
            notebook_id = t['id']

            if args.output_path is sys.stdout:
                args.output_path = ''
            elif not os.path.isdir(args.output_path):
                raise ValueError('Output path given is not valid directory.')

            output_path = os.path.join(args.output_path, '')
            notebook_executor = NotebookExecutor(notebook_id, output_path,
                                                 args.zeppelin_url)
            notebook_executor.execute_notebook()
        except ValueError as err:
            print(err)
            sys.exit(1)


if __name__ == '__main__':
    main()

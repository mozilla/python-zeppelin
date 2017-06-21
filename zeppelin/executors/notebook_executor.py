# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import requests
import sys
import json
import time


class NotebookExecutor():
    """NotebookExecutor is a command line tool to execute a Zeppelin notebook."""

    def __init__(self, notebook_id, output_path, zeppelin_url):
        """Initialize class object with attributes based on CLI inputs."""
        self.notebook_id = notebook_id
        self.output_path = output_path
        self.zeppelin_url = zeppelin_url

    def run_notebook(self):
        """Call API to execute notebook."""
        requests.post('http://{0}/api/notebook/job/{1}'.format(
                      self.zeppelin_url, self.notebook_id))

    def wait_for_notebook_to_execute(self):
        """Wait for notebook to finish executing before continuing."""
        while True:
            r = requests.get('http://{0}/api/notebook/job/{1}'.format(
                             self.zeppelin_url, self.notebook_id))
            data = r.json()['body']
            if all(paragraph['status'] in ['FINISHED', 'ERROR'] for paragraph in data):
                break
            time.sleep(1)

    def get_executed_notebook(self):
        """Return the executed notebook."""
        r = requests.get('http://{0}/api/notebook/{1}'.format(
                         self.zeppelin_url, self.notebook_id))
        if r.status_code == 200:
            return r.json()['body']
        else:
            print('ERROR: Could not get executed notebook.', file=sys.stderr)
            sys.exit(1)

    def save_notebook(self, body):
        """Save notebook depending on user provided output path."""
        directory = os.path.dirname(self.output_path)
        full_path = os.path.join(directory, 'note.json')
        try:
            with open(full_path, 'w') as fh:
                fh.write(json.dumps(body, indent=2))
        except ValueError:
            print('ERROR: Could not save executed notebook to path: ' +
                  self.output_path +
                  ' -- Please provide a valid absolute path.')

    def execute_notebook(self):
        """Execute input notebook and save it to file.

        If no output path given, the output will be printed to stdout.

        If any errors occur from executing the notebook's paragraphs, they will
        be displayed in stderr.
        """
        self.run_notebook()
        self.wait_for_notebook_to_execute()
        body = self.get_executed_notebook()

        err = False
        for paragraph in body['paragraphs']:
            if 'results' in paragraph and paragraph['results']['code'] == 'ERROR':
                print(paragraph['results']['msg'][0]['data'], file=sys.stderr)
                err = True

        if err:
            sys.exit(1)

        if not self.output_path:
            print(json.dumps(body, indent=2))
        else:
            self.save_notebook(body)

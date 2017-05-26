import sys
import json
import re
import os
import base64
import abc
from datetime import datetime
from .converter import ZeppelinConverter


class NewConverter(ZeppelinConverter):
    """NewConverter class.

    NewConverter converts Zeppelin version 0.7.1 notebooks to Markdown.
    """

    MD_EXT = '.md'

    def build_image(self, msg):
        """Convert base64 encoding to png.

        Strips msg of the base64 image encoding and outputs
        the images to the specified directory.
        """
        result = re.search('base64,(.*?)"', msg['data'])

        if result is None:
            return

        self.index += 1
        images_path = 'images'

        if self.directory:
            images_path = self.directory + '/' + images_path

        if not os.path.isdir(images_path):
            os.makedirs(images_path)

        with open('{0}/output_{1}.png'.format(images_path, self.index), 'wb') as fh:
            fh.write(base64.b64decode(result.group(1).encode('utf-8')))

        self.out.append(
            '\n![png]({0}/output_{1}.png)\n'.format(images_path, self.index))

    def build_text(self, msg):
        """Add text to output array."""
        self.out.append(msg['data'])

    def build_table(self, msg):
        """Format each row of the table."""
        rows = msg['data'].split('\n')
        if rows:
            header_row = rows[0]
            body_rows = rows[1:]
            self.create_md_row(header_row, True)
            for row in body_rows:
                self.create_md_row(row)

    def process_results(self, paragraph):
        """Output options.

        Routes Zeppelin output types to corresponding
        functions for it to be handled. To add support for other output
        types, add the file type to the dictionary and create the necessary
        function to handle it.
        """
        output_options = {
            'HTML': self.build_image,
            'TEXT': self.build_text,
            'TABLE': self.build_table
        }

        if 'editorMode' in paragraph['config']:
            mode = paragraph['config']['editorMode'].split('/')[-1]
            if paragraph['results']['msg']:
                msg = paragraph['results']['msg'][0]
                if mode not in ('text', 'markdown'):
                    output_options[msg['type']](msg)

    def build_markdown_body(self, text):
        """Generate the body for the Markdown file.

        - processes each json block one by one
        - for each block
            - process the input by detecting the editor language
            - print the input
            - process the output by detecting the output format
            - print the output
        """
        for paragraph in text['paragraphs']:
            if 'user' in paragraph:
                self.user = paragraph['user']
            if 'dateCreated' in paragraph:
                self.process_date_created(paragraph['dateCreated'])
            if 'dateUpdated' in paragraph:
                self.process_date_updated(paragraph['dateUpdated'])
            if 'title' in paragraph:
                self.process_title(paragraph['title'])
            if 'text' in paragraph:
                self.process_input(paragraph['text'])
            if 'results' in paragraph:
                self.process_results(paragraph)

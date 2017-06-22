# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import abc
import os
import cairosvg
import re
import base64
from dateutil.parser import parse


class MarkdownConverter(abc.ABC):
    """ZeppelinConverter is a utility to convert Zeppelin raw json into Markdown."""

    @abc.abstractproperty
    def _RESULT_KEY(self):
        pass

    def __init__(self, input_filename, output_filename, directory, user='anonymous',
                 date_created='N/A', date_updated='N/A'):
        """Initialize class object with attributes based on CLI inputs."""
        self.index = 0
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.directory = directory
        self.user = user
        self.date_created = date_created
        self.date_updated = date_updated
        self.out = []

        # To add support for other output types, add the file type to
        # the dictionary and create the necessary function to handle it.
        self.output_options = {
            'HTML': self.build_image,
            'TEXT': self.build_text,
            'TABLE': self.build_table
        }

    def build_header(self, title):
        """Generate the header for the Markdown file."""
        header = ['---',
                  'title: ' + title,
                  'author(s): ' + self.user,
                  'tags: ',
                  'created_at: ' + str(self.date_created),
                  'updated_at: ' + str(self.date_updated),
                  'tldr: ',
                  'thumbnail: ',
                  '---']

        self.out = header + self.out

    def build_markdown(self, lang, body):
        """Append paragraphs body to output string."""
        if body is not None:
            self.out.append(body)

    def build_code(self, lang, body):
        """Wrap text with markdown specific flavour."""
        self.out.append("```" + lang)
        self.build_markdown(lang, body)
        self.out.append("```")

    def process_input(self, paragraph):
        """Parse paragraph for the language of the code and the code itself."""
        try:
            lang, body = paragraph.split(None, 1)
        except ValueError:
            lang, body = paragraph, None

        if not lang.strip().startswith('%'):
            lang = 'scala'
            body = paragraph.strip()

        else:
            lang = lang.strip()[1:]

        if lang == 'md':
            self.build_markdown(lang, body)
        else:
            self.build_code(lang, body)

    def create_md_row(self, row, header=False):
        """Translate row into markdown format."""
        if not row:
            return
        cols = row.split('\t')
        if len(cols) == 1:
            self.out.append(cols[0])
        else:
            col_md = '|'
            underline_md = '|'

            if cols:
                for col in cols:
                    col_md += col + '|'
                    underline_md += '-|'

            if header:
                self.out.append(col_md + '\n' + underline_md)
            else:
                self.out.append(col_md)

    def process_date_created(self, text):
        """Set date_created to the oldest date (date created)."""
        date = parse(text)
        if self.date_created == 'N/A':
            self.date_created = date
        if date < self.date_created:
            self.date_created = date

    def process_date_updated(self, text):
        """Set date_updated to the most recent date (updated date)."""
        date = parse(text)
        if self.date_updated == 'N/A':
            self.date_updated = date
        if date > self.date_updated:
            self.date_updated = date

    def process_title(self, text):
        """Append hashtags before the title.

        This is done to bold the title in markdown.
        """
        self.out.append('#### ' + text)

    def build_output(self, fout):
        """Squash self.out into string.

        Join every line in self.out with a new line and write the
        result to the output file.
        """
        fout.write('\n'.join([s for s in self.out]))

    def convert(self, json, fout):
        """Convert json to markdown.

        Takes in a .json file as input and convert it to Markdown format,
        saving the generated .png images into ./images.
        """
        self.build_markdown_body(json)  # create the body
        self.build_header(json['name'])  # create the md header
        self.build_output(fout)  # write body and header to output file

    def build_markdown_body(self, text):
        """Generate the body for the Markdown file.

        - processes each json block one by one
        - for each block, process:
            - the creator of the notebook (user)
            - the date the notebook was created
            - the date the notebook was last updated
            - the input by detecting the editor language
            - the output by detecting the output format
        """
        key_options = {
            'dateCreated': self.process_date_created,
            'dateUpdated': self.process_date_updated,
            'title': self.process_title,
            'text': self.process_input
        }

        for paragraph in text['paragraphs']:
            if 'user' in paragraph:
                self.user = paragraph['user']

            for key, handler in key_options.items():
                if key in paragraph:
                    handler(paragraph[key])

            if self._RESULT_KEY in paragraph:
                self.process_results(paragraph)

    def build_text(self, msg):
        """Add text to output array."""
        self.out.append(msg)

    def build_table(self, msg):
        """Format each row of the table."""
        rows = msg.split('\n')
        if rows:
            header_row, *body_rows = rows
            self.create_md_row(header_row, True)
            for row in body_rows:
                self.create_md_row(row)

    def build_image(self, msg):
        """Convert base64 encoding to png.

        Strips msg of the base64 image encoding and outputs
        the images to the specified directory.
        """
        result = self.find_message(msg)

        if result is None:
            return

        self.index += 1
        images_path = 'images'

        if self.directory:
            images_path = os.path.join(self.directory, images_path)

        if not os.path.isdir(images_path):
            os.makedirs(images_path)

        with open('{0}/output_{1}.png'.format(images_path, self.index), 'wb') as fh:
            self.write_image_to_disk(msg, result, fh)

        self.out.append(
            '\n![png]({0}/output_{1}.png)\n'.format(images_path, self.index))

    @abc.abstractmethod
    def find_message(self, msg):
        """Use regex to find encoded image."""

    @abc.abstractmethod
    def write_image_to_disk(self, msg, result, fh):
        """Decode message to PNG and write to disk."""

    @abc.abstractmethod
    def process_results(self, paragraph):
        """Route Zeppelin output types to corresponding handlers."""


class LegacyConverter(MarkdownConverter):
    """LegacyConverter converts Zeppelin version 0.6.2 notebooks to Markdown."""

    _RESULT_KEY = 'result'

    def find_message(self, msg):
        """Use regex to find encoded image."""
        return re.search('xml version', msg)

    def write_image_to_disk(self, msg, result, fh):
        """Decode message to PNG and write to disk."""
        cairosvg.svg2png(bytestring=msg.encode('utf-8'), write_to=fh)

    def process_results(self, paragraph):
        """Route Zeppelin output types to corresponding handlers."""
        if 'result' in paragraph and paragraph['result']['msg']:
            msg = paragraph['result']['msg']
            self.output_options[paragraph['result']['type']](msg)


class NewConverter(MarkdownConverter):
    """NewConverter converts Zeppelin version 0.7.1 notebooks to Markdown."""

    _RESULT_KEY = 'results'

    def find_message(self, msg):
        """Use regex to find encoded image."""
        return re.search('base64,(.*?)"', msg)

    def write_image_to_disk(self, msg, result, fh):
        """Decode message to PNG and write to disk."""
        fh.write(base64.b64decode(result.group(1).encode('utf-8')))

    def process_results(self, paragraph):
        """Routes Zeppelin output types to corresponding handlers."""
        if 'editorMode' in paragraph['config']:
            mode = paragraph['config']['editorMode'].split('/')[-1]
            if 'results' in paragraph and paragraph['results']['msg']:
                msg = paragraph['results']['msg'][0]
                if mode not in ('text', 'markdown'):
                    self.output_options[msg['type']](msg['data'])

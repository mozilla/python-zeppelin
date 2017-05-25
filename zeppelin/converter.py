import sys
import json
import re
import os
from datetime import datetime


class ZeppelinConverter:
    """ZeppelinConverter class.

    ZeppelinConverter is a utility to convert Zeppelin raw json into Markdown.
    """

    MD_EXT = '.md'

    def __init__(self, ifn, ofn, dire, user, date_created, date_updated):
        self.index = 0
        self.input_filename = ifn
        self.output_filename = ofn
        self.directory = dire
        self.user = user
        self.date_created = date_created
        self.date_updated = date_updated
        self.out = []

    def build_header(self, text):
        """Generate the header for the Markdown file."""
        header = ['---',
                  'title: ' + text['name'],
                  'author(s): ' + self.user,
                  'tags: ',
                  'created_at: ' + self.date_created,
                  'updated_at: ' + self.date_updated,
                  'tldr: ',
                  'thumbnail: ',
                  '---']

        self.out = header + self.out

    def build_markdown(self, lang, body):
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

        if lang.strip().startswith('%'):
            lang = 'scala'
            body = paragraph

        else:
            lang = lang[1:]

        if lang == 'md':
            self.build_markdown(lang, body)
        else:
            self.build_code(lang, body)

    def build_image(self, msg):
        """Convert base64 encoding to png.

        Strips msg of the base64 image encoding and outputs
        the images to the specified directory.
        """
        result = re.search('base64,(.*?)"', msg['data'])

        if result is None:
            return

        self.index += 1
        images_path = self.directory + '/images'
        if not os.path.isdir(images_path):
            os.makedirs(images_path)

        with open('{0}/output_{1}.png'.format(images_path, self.index), 'wb') as fh:
            fh.write(result.group(1).encode('utf-8').decode('base64'))

        self.out.append('\n![png]({0}/output_{1}.png\n'.format(images_path, self.index))

    def build_text(self, msg):
        """Add text to output array."""
        self.out.append(msg['data'])

    def create_md_row(self, row, header=False):
        """Translate row into markdown format."""
        cols = row.split('\t')
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

    def parse_date(self, date):
        """Convert string to date object.

        A sample string with this format is 'Feb 29, 2017 04:39:59 pm'.
        """
        return datetime.strptime(date, '%b %d, %Y %I:%M:%S %p')

    def process_date_created(self, text):
        """Set date_created to the oldest date (date created)."""
        if self.date_created == 'N/A':
            self.date_created = text
        if self.parse_date(text) < self.parse_date(self.date_created):
            self.date_created = text

    def process_date_updated(self, text):
        """Set date_updated to the most recent date (updated date)."""
        if self.date_updated == 'N/A':
            self.date_updated = text
        if self.parse_date(text) > self.parse_date(self.date_updated):
            self.date_updated = text

    def process_title(self, text):
        """Append hashtags before the title.

        This is done to bold the title in markdown.
        """
        self.out.append('#### ' + text)

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

    def build_output(self, fout):
        """Squash self.out into string.

        Join every line in self.out with a new line and write the
        result to the output file.
        """
        fout.write('\n'.join([s.encode('utf-8') for s in self.out]))

    def convert(self):
        """Convert json to markdown.

        Takes in a .json file as input and convert it to Markdown format,
        saving the generated .png images into ./images.
        """
        try:
            with open(self.input_filename, 'rb') as raw:
                t = json.load(raw)
                full_path = os.path.join(self.directory, self.output_filename + self.MD_EXT)
                with open(full_path, 'w') as fout:
                    self.build_markdown_body(t)  # create the body
                    self.build_header(t)  # create the md header
                    self.build_output(fout)  # write body and header to output file

        except ValueError as err:
            print err
            sys.exit(1)

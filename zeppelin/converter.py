import sys
import json
import re
import os
import base64
import abc
from datetime import datetime


class ZeppelinConverter(metaclass=abc.ABCMeta):
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

    def build_header(self, title):
        """Generate the header for the Markdown file."""
        header = ['---',
                  'title: ' + title,
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

    def build_output(self, fout):
        """Squash self.out into string.

        Join every line in self.out with a new line and write the
        result to the output file.
        """
        fout.write('\n'.join([s for s in self.out]))

    def convert(self, t, fout):
        """Convert json to markdown.

        Takes in a .json file as input and convert it to Markdown format,
        saving the generated .png images into ./images.
        """
        self.build_markdown_body(t)  # create the body
        self.build_header(t['name'])  # create the md header
        self.build_output(fout)  # write body and header to output file

    @abc.abstractmethod
    def build_table(self, msg):
        """Format each row of the table."""

    @abc.abstractmethod
    def process_results(self, paragraph):
        """Output options."""

    @abc.abstractmethod
    def build_markdown_body(self, text):
        """Generate the body for the Markdown file."""

    @abc.abstractmethod
    def build_image(self, msg):
        """Convert base64 encoding to png."""

    @abc.abstractmethod
    def build_text(self, msg):
        """Add text to output array."""

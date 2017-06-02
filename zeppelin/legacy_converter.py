import re
import os
import cairosvg
from .converter import MarkdownConverter


class LegacyConverter(ZeppelinConverter):
    """LegacyConverter converts Zeppelin version 0.6.2 notebooks to Markdown."""

    def build_image(self, msg):
        """Convert svg encoding to png.

        Uses CairoSVG to convert svg image to a png and outputs
        the images to the specified directory.
        """
        result = re.search('xml version', msg)
        if result is None:
            return

        self.index += 1
        images_path = 'images'

        if self.directory:
            images_path = os.path.join(self.directory, images_path)

        if not os.path.isdir(images_path):
            os.makedirs(images_path)

        with open('{0}/output_{1}.png'.format(images_path, self.index), 'wb') as fh:
            cairosvg.svg2png(bytestring=msg.encode('utf-8'), write_to=fh)

        self.out.append(
            '\n![png]({0}/output_{1}.png)\n'.format(images_path, self.index))

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

    def process_results(self, paragraph):
        """Routes Zeppelin output types to corresponding handlers.

        To add support for other output types, add the file type to
        the dictionary and create the necessary function to handle it.
        """
        output_options = {
            'HTML': self.build_image,
            'TEXT': self.build_text,
            'TABLE': self.build_table
        }

        if paragraph['result']['msg']:
            msg = paragraph['result']['msg']
            output_options[paragraph['result']['type']](msg)

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
            if 'result' in paragraph:
                self.process_results(paragraph)

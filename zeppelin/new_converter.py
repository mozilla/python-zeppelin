import re
import base64
from .converter import MarkdownConverter


class NewConverter(MarkdownConverter):
    """NewConverter converts Zeppelin version 0.7.1 notebooks to Markdown."""

    RESULT_KEY = 'results'

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
            if paragraph['results']['msg']:
                msg = paragraph['results']['msg'][0]
                if mode not in ('text', 'markdown'):
                    self.output_options[msg['type']](msg['data'])

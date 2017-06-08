import re
import cairosvg
from .converter import MarkdownConverter


class LegacyConverter(MarkdownConverter):
    """LegacyConverter converts Zeppelin version 0.6.2 notebooks to Markdown."""

    RESULT_KEY = 'result'

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

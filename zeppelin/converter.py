import sys
import json
import re
import os
from datetime import datetime

"""
ZeppelinConverter is a utility to convert Zeppelin raw json into Markdown

"""


class ZeppelinConverter:

    def __init__(self, filename, user, date_created, date_updated):
        self.index = 0
        self.filename = filename
        self.user = user
        self.date_created = date_created
        self.date_updated = date_updated
        self.out = []

    def gen_header(self, t):

        """ Generate the header for the Markdown file

        """
        header = ['---',
                  'title: ' + t['name'],
                  'author(s): ' + self.user,
                  'tags: ',
                  'created_at: ' + self.date_created,
                  'updated_at: ' + self.date_updated,
                  'tldr: ',
                  'thumbnail: ',
                  '---']

        self.out = header + self.out

    def gen_markdown_body(self, t):

        """ Generate the body for the Markdown file

        - processes each json block one by one
        - for each block
            - process the input by detecting the editor language
            - print the input
            - process the output by detecting the output format
            - print the output

        """
        def gen_md(l, b):
            if b is not None:
                self.out.append(b)

        def gen_code(l, b):
            self.out.append("```" + l)
            gen_md(l, b)
            self.out.append("```")

        """ Input options -- for now we don't need them
        input_options = {
            'md' : gen_md,
            'python' : gen_code,
            'pyspark' : gen_code,
            'sql' : gen_code
        }
        """
        def process_input(p):
            try:
                lang, body = p.split(None, 1)
                # print lang
            except:
                lang, body = p, None

            if lang.strip()[0] != '%':
                lang = 'scala'
                body = p

            else:
                lang = lang[1:]

            if lang == 'md':
                gen_md(lang, body)
            else:
                gen_code(lang, body)

            # input_options[lang](lang, body)

        def gen_image(m):
            result = re.search('base64,(.*?)"', m['data'])

            if result is None:
                return

            self.index += 1

            if os.path.isdir('images') is False:
                os.makedirs('images')

            with open("images/output_" + str(self.index) + ".png", "wb") as fh:
                fh.write(result.group(1).encode('utf-8').decode('base64'))

            self.out.append("\n![png](images/output_" +
                            str(self.index) + ".png)\n")

        def gen_text(m):
            self.out.append(m['data'])

        def create_md_row(r, header=False):
            cols = r.split('\t')
            col_md = '|'
            underline_md = '|'

            if cols != []:
                for col in cols:
                    col_md += col + '|'
                    underline_md += '-|'

            if header:
                self.out.append(col_md + '\n' + underline_md)
            else:
                self.out.append(col_md)

        def gen_table(m):
            rows = m['data'].split('\n')
            if rows:
                header_row = rows[0]
                body_rows = rows[1:]
                create_md_row(header_row, True)
                for row in body_rows:
                    create_md_row(row)

        """ Output options

        Routes Zeppelin output types to corresponding
        functions for it to be handled. To add support for other output
        types, add the file type to the dictionary and create the necessary
        function to handle it.

        """
        output_options = {
            'HTML': gen_image,
            'TEXT': gen_text,
            'TABLE': gen_table
        }

        def process_output(p):
            if 'editorMode' in p['config']:
                mode = p['config']['editorMode'].split('/')[-1]
                if p['results']['msg']:
                    msg = p['results']['msg'][0]
                    if mode not in ('text', 'markdown'):
                        output_options[msg['type']](msg)

        def parse_date(d):
            return datetime.strptime(d, '%b %d, %Y %I:%M:%S %p')

        def process_date_created(t):
            if self.date_created == 'N/A':
                self.date_created = t
            if parse_date(t) < parse_date(self.date_created):
                self.date_created = t

        def process_date_updated(t):
            if self.date_updated == 'N/A':
                self.date_updated = t
            if parse_date(t) > parse_date(self.date_updated):
                self.date_updated = t

        def process_title(t):
            self.out.append('#### ' + t)

        for paragraph in t['paragraphs']:
            if 'user' in paragraph:
                self.user = paragraph['user']
            if 'dateCreated' in paragraph:
                process_date_created(paragraph['dateCreated'])
            if 'dateUpdated' in paragraph:
                process_date_updated(paragraph['dateUpdated'])
            if 'title' in paragraph:
                process_title(paragraph['title'])
            if 'text' in paragraph:
                process_input(paragraph['text'])
            if 'results' in paragraph:
                process_output(paragraph)

    def gen_output(self, fout):
        fout.write('\n'.join([s.encode('utf-8') for s in self.out]))

    def convert(self):

        """
        Takes in a .json file as input and convert it to Markdown format,
        saving the generated .png images into ./images.

        """

        try:
            with open(self.filename, 'rb') as raw:
                t = json.load(raw)
                with open('knowledge.md', 'w') as fout:
                    self.gen_markdown_body(t)   # create the body
                    self.gen_header(t)          # create the md header
                    self.gen_output(fout)       # write to file

        except ValueError as err:
            print err
            sys.exit(1)

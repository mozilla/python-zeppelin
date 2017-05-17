import sys
import json
import re
import os
from datetime import datetime

"""
ZeppelinConverter is a utility to convert Zeppelin raw json into Markdown

"""
class ZeppelinConverter:

	def __init__(self):
		self.index = 0
		self.user = 'anonymous'
		self.date_updated = 'N/A'
		self.date_created = 'N/A'
		self.out = ''

	def print_line(self, s):
		self.out += s.encode('utf-8') + '\n'
	
	"""
	Step 1: generate the header for the Markdown file

	"""
	def gen_header(self, t):

		header = ('---\ntitle: ' + t['name'] +
				 '\nauthor(s): ' + self.user +
				 '\ntags: ' + 
				 '\ncreated_at: ' + self.date_created +
				 '\nupdated_at: ' + self.date_updated +
				 '\ntldr: ' +
				 '\nthumbnail: ' +
				 '\n---\n')

		self.out = header.encode('utf-8') + self.out

	"""
	Step 2: generate the body for the Markdown file
	
	- processes each json block one by one
	- for each block
		- process the input by detecting the editor language
		- print the input
		- process the output by detecting the output format
		- print the output

	"""
	def gen_body(self, t):
		def gen_md(l, b):
			if b is not None:
				self.print_line(b)

		def gen_code(l, b):
			self.print_line("```" + l)
			gen_md(l, b)
			self.print_line("```")

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
			except:
				lang, body = p, None

			lang = lang[1:]
			
			if lang == 'md':
				gen_md(lang, body)
			else:
				gen_code(lang, body)

			# input_options[lang](lang, body)

		def gen_image(m):
			result = re.search('base64,(.*)style', m['data'])
			if result == None:
				return

			self.index += 1

			if os.path.isdir('images') is False:
				os.makedirs('images')

			with open("images/output_" + str(self.index) + ".png", "wb") as fh:
				fh.write(result.group(1).decode('base64'))

			self.print_line("\n![png](images/output_" + str(self.index) + ".png)\n")

		def gen_text(m):
			self.print_line(m['data'])

		def create_md_row(r, header=False):
			cols = r.split('\t')
			col_md = '|'
			underline_md = '|'

			if cols != []: 
				for col in cols:
					col_md += col + '|'
					underline_md += '-|' 

			if header:
				self.print_line(col_md + '\n' + underline_md)
			else:
				self.print_line(col_md)

		def gen_table(m):
			rows = m['data'].split('\n')
			if rows != []:
				header_row = rows[0]
				body_rows = rows[1:]
				create_md_row(header_row, True)
				for row in body_rows:
					create_md_row(row)

		""" 
		Output options routes Zeppelin output types to corresponding
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
				if p['results']['msg'] != []:
					msg = p['results']['msg'][0]
					if mode != 'text' and mode != 'markdown':
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

		for paragraph in t['paragraphs']:
			if 'user' in paragraph.keys():
				self.user = paragraph['user']
			if 'dateCreated' in paragraph.keys():
				process_date_created(paragraph['dateCreated'])
			if 'dateUpdated' in paragraph.keys():
				process_date_updated(paragraph['dateUpdated'])
			if 'text' in paragraph.keys():
				process_input(paragraph['text'])
			if 'results' in paragraph.keys():
				process_output(paragraph)

	"""
	Takes in a .json file as input and convert it to Markdown format,
	saving the generated .png images into ./images.

	"""
	def convert(self):
		if len(sys.argv) != 2:
			raise ValueError('ERROR: No input file specified or too many arguments')

		f = sys.argv[1]

		try:
			with open(f, 'rb') as raw:
				t = json.load(raw)
				with open('knowledge.md', 'w') as fout:
					self.gen_body(t) # Step 1: create the body
					self.gen_header(t) # Step 2: create the md header
					fout.write(self.out) # Step 3: write to file

		except ValueError as err:
			print err.args

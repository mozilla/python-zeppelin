# Zeppelin Converter

### Usage

To convert a Zeppelin .json file into Markdown (.md), run `python -m zeppelin.cli -i <<INPUT>> -o <<OUTPUT>>` in the main directory.

- `<<INPUT>>` is the file name. This is a required field.
- `<<OUTPUT>>` is the output file name. This is optional. If this is not provided, the output file name will be called `knowledge.md` and it will be stored in the current directory. You can also provide a path before the filename to specify a location to save the file `path/to/file/filename`.

If there are png outputs, they will be stored under `/images` in the same location as the output file. 

### Testing

To execute the tests under `/tests`, run `pytest -v`. 

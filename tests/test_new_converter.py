import pytest
from zeppelin.new_converter import NewConverter


@pytest.fixture
def zc():
    zc = NewConverter('in', 'out', '', 'anonymous', 'N/A', 'N/A')
    return zc


def test_header(zc):
    zc.user = 'tester'
    zc.build_header('title')
    assert zc.out == ['---',
                      'title: title',
                      'author(s): tester',
                      'tags: ',
                      'created_at: ' + zc.date_created,
                      'updated_at: ' + zc.date_updated,
                      'tldr: ',
                      'thumbnail: ',
                      '---']


def test_build_markdown(zc):
    zc.build_markdown('scala', None)
    assert zc.out == []
    zc.build_markdown('scala', 'sample body')
    assert zc.out == ['sample body']


def test_build_code(zc):
    zc.build_code('scala', None)
    assert zc.out == ['```scala', '```']
    zc.build_code('scala', 'sample body')
    assert zc.out == ['```scala', '```',
                      '```scala', 'sample body', '```']


@pytest.mark.parametrize('test_input, expected', [
                         ('%md', []),
                         ('%md text', ['text']),
                         (' %md   text', ['text']),
                         (' sample text', ['```scala', 'sample text', '```']),
                         ('s%ample', ['```scala', 's%ample', '```'])])
def test_process_input(zc, test_input, expected):
    zc.process_input(test_input)
    assert zc.out == expected


def test_build_text(zc):
    msg = {
        'data': 'sample text'
    }
    zc.build_text(msg)
    assert zc.out == ['sample text']


def test_title(zc):
    assert zc.out == []
    zc.process_title('title')
    assert zc.out == ['#### title']


@pytest.mark.parametrize('test_input, expected', [
                         ('', []),
                         ('test', ['test']),
                         ('test\ttest2', ['|test|test2|']),
                         ('test\t\ttest2', ['|test||test2|'])
                         ])
def test_create_md_row(zc, test_input, expected):
    zc.create_md_row(test_input)
    assert zc.out == expected


def test_create_md_row_header(zc):
    zc.create_md_row('test\ttest2', True)
    assert zc.out == ['|test|test2|\n|-|-|']

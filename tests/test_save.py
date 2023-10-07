from io import StringIO

import ujson
import yaml

from qq_chat_history import parse

lines = '''
1883-03-07 11:22:33 A<someone@example.com>
Text A

1883-03-07 12:34:56 B(123123)
Text B
'''.strip().splitlines()

expected_dicts = [
    {
        'date': '1883-03-07 11:22:33',
        'id': 'someone@example.com',
        'name': 'A',
        'content': 'Text A',
    },
    {
        'date': '1883-03-07 12:34:56',
        'id': '123123',
        'name': 'B',
        'content': 'Text B',
    },
]


def do_format(fmt: str) -> StringIO:
    fp = StringIO()
    parse(lines).save(fp, fmt, indent=2)
    fp.seek(0)
    return fp


def test_formatters() -> None:
    with do_format('json') as f:
        assert ujson.load(f) == expected_dicts

    with do_format('yaml') as f:
        assert yaml.load(f, Loader=yaml.CLoader) == expected_dicts

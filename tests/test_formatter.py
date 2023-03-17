import yaml
import ujson
from io import StringIO
from qq_chat_history import parse


lines = '''
=========
假装我是 QQ 自动生成的文件头
=========

1883-03-07 11:22:33 A<someone@example.com>
关注永雏塔菲喵
关注永雏塔菲谢谢喵

1883-03-07 12:34:56 B(123123)
TCG
'''.strip().splitlines()

expected_dicts = [
    {
        'date': '1883-03-07 11:22:33',
        'id': 'someone@example.com',
        'name': 'A',
        'content': '关注永雏塔菲喵\n关注永雏塔菲谢谢喵',
    },
    {
        'date': '1883-03-07 12:34:56',
        'id': '123123',
        'name': 'B',
        'content': 'TCG',
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

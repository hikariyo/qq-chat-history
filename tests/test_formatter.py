import yaml
import ujson
from io import StringIO
from qq_chat_history import parse, format_json, format_yaml


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


def test_json() -> None:
    fp = StringIO()
    format_json(fp, parse(lines))
    fp.seek(0)
    assert ujson.load(fp) == expected_dicts


def test_yaml() -> None:
    fp = StringIO()
    format_yaml(fp, parse(lines))
    fp.seek(0)
    assert yaml.safe_load(fp) == expected_dicts

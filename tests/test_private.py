from qq_chat_history import Parser


lines = '''
1883-03-07 11:22:33 A
关注永雏塔菲喵
关注永雏塔菲谢谢喵

1883-03-07 12:34:56 B
TCG

1883-03-07 22:00:51 A
塔菲怎么你了
'''.strip().splitlines()

expected_lines = [
    {'date': '1883-03-07 11:22:33', 'id': 'A', 'name': 'A', 'content': '关注永雏塔菲喵\n关注永雏塔菲谢谢喵'},
    {'date': '1883-03-07 12:34:56', 'id': 'B', 'name': 'B', 'content': 'TCG'},
    {'date': '1883-03-07 22:00:51', 'id': 'A', 'name': 'A', 'content': '塔菲怎么你了'}
]


def test_group():
    parser = Parser.get_instance('private')
    parsed_lines = list(parser.parse(lines))
    assert parsed_lines == expected_lines


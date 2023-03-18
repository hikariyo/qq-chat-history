from qq_chat_history import Message, parse

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


def test_group() -> None:
    body = parse(lines)

    assert body.find_first_by_name('A') == Message(
        date='1883-03-07 11:22:33', id='someone@example.com', name='A', content='关注永雏塔菲喵\n关注永雏塔菲谢谢喵',
    )

    assert body.find_first_by_id('123123') == Message(
        date='1883-03-07 12:34:56', id='123123', name='B', content='TCG',
    )

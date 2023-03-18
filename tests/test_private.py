from qq_chat_history import Message, parse

lines = '''
=========
假装我是 QQ 自动生成的文件头
=========

1883-03-07 12:34:56 B
你说得对

1883-03-07 22:00:51 A
2006-01-02 15:04:05




2006-01-02 15:04:05
'''.strip().splitlines()


def test_private() -> None:
    body = parse(lines)

    assert body.find_first_message_by_name('B') == Message(
        date='1883-03-07 12:34:56', id='B', name='B', content='你说得对',
    )

    # Blank lines will be omitted.
    assert body.find_first_message_by_id('A') == Message(
        date='1883-03-07 22:00:51', id='A', name='A', content='2006-01-02 15:04:05\n2006-01-02 15:04:05',
    )

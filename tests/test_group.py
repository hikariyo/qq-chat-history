from qq_chat_history import Message, parse

lines = '''
1883-03-07 11:22:33 A<someone@example.com>
Text A1
Text A2

1883-03-07 12:34:56 B(123123)
Text B
'''.strip().splitlines()


def test_group() -> None:
    body = parse(lines)

    assert body.find_first_message_by_name('A') == Message(
        date='1883-03-07 11:22:33', id='someone@example.com', name='A', content='Text A1\nText A2',
    )

    assert body.find_first_message_by_id('123123') == Message(
        date='1883-03-07 12:34:56', id='123123', name='B', content='Text B',
    )

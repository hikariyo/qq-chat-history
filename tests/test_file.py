from pathlib import Path

from qq_chat_history import Message, parse

file = Path(__file__).parent / 'file.txt'


def test_file() -> None:
    body = parse(file)

    assert body.find_first_message_by_id('123123') == Message(
        id='123123', name='A', content='A', date='1883-03-07 11:22:33',
    )

    assert body.find_first_message_by_name('B') == Message(
        id='456456', name='B', content='B', date='1883-03-07 12:34:56',
    )

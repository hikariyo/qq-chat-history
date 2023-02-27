from qq_chat_history import parse, Message


date_lines = '''
=========
假装我是 QQ 自动生成的文件头
=========


1883-03-07 11:22:33 A
1883-03-07 11:22:33

1883-03-07 22:00:51 A
2006-01-02 15:04:05




2006-01-02 15:04:05
'''.strip().splitlines()


date_expected_messages = [
    Message(date='1883-03-07 11:22:33', id='A', name='A', content='1883-03-07 11:22:33'),
    # Blank lines will be omitted.
    Message(date='1883-03-07 22:00:51', id='A', name='A', content='2006-01-02 15:04:05\n2006-01-02 15:04:05'),
]

name_lines = '''
=========
假装我是 QQ 自动生成的文件头
=========


1883-03-07 11:22:33 (A(123123)
TEST

1883-03-07 22:00:51 (B)(456456)
TEST

1883-03-07 23:23:33 (o´・ω・`)σ<mail@someaddress.com>
TEST
'''.strip().splitlines()

name_expected_messages = [
    Message(date='1883-03-07 11:22:33', name='(A', content='TEST', id='123123'),
    Message(date='1883-03-07 22:00:51', name='(B)', content='TEST', id='456456'),
    Message(date='1883-03-07 23:23:33', name='(o´・ω・`)σ', content='TEST', id='mail@someaddress.com'),
]


def test_pure_date_message() -> None:
    messages = list(parse(date_lines))
    assert messages == date_expected_messages


def test_name_with_brackets() -> None:
    messages = list(parse(name_lines))
    assert messages == name_expected_messages

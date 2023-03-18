from qq_chat_history import Message, parse

date_lines = '''
=========
假装我是 QQ 自动生成的文件头
=========


1883-03-07 11:22:33 A
1883-03-07 11:22:33

1883-03-07 22:00:51 B
2006-01-02 15:04:05




2006-01-02 15:04:05
'''.strip().splitlines()

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


def test_pure_date_message() -> None:
    body = parse(date_lines)

    assert body.find_first_by_id('A') == Message(
        date='1883-03-07 11:22:33', id='A', name='A', content='1883-03-07 11:22:33',
    )

    # Blank lines will be omitted.
    assert body.find_first_by_name('B') == Message(
        date='1883-03-07 22:00:51', id='B', name='B', content='2006-01-02 15:04:05\n2006-01-02 15:04:05',
    )


def test_name_with_brackets() -> None:
    body = parse(name_lines)

    assert body.find_first_by_name('(A') == Message(
        date='1883-03-07 11:22:33', name='(A', content='TEST', id='123123',
    )

    assert body.find_first_by_id('456456') == Message(
        date='1883-03-07 22:00:51', name='(B)', content='TEST', id='456456',
    )

    assert body.find_first_by_id('mail@someaddress.com') == Message(
        date='1883-03-07 23:23:33', name='(o´・ω・`)σ', content='TEST', id='mail@someaddress.com',
    )

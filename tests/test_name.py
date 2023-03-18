from qq_chat_history import parse

lines = """
1883-03-07 11:22:33 (o´・ω・`)σ(123123)
可爱捏

1883-03-07 11:22:34 (A)(123123)
加个括号

1883-03-07 11:22:35 (B(123123)
半括号
""".strip().splitlines()


def test_name() -> None:
    body = parse(lines)
    assert body.find_latest_name('123123') == '(B'
    assert body.find_names('123123') == [
        '(o´・ω・`)σ', '(A)', '(B',
    ]

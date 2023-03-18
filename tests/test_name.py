from qq_chat_history import parse


lines = """
=========
假装我是 QQ 自动生成的文件头
=========

1883-03-07 11:22:33 A(123123)
我现在叫A

1883-03-07 11:22:34 B(123123)
我现在叫B

1883-03-07 11:22:35 C(123123)
变成C了捏
""".strip().splitlines()


def test_name() -> None:
    body = parse(lines)
    assert body.get_latest_name('123123') == 'C'
    assert body.get_names('123123') == [
        'A', 'B', 'C'
    ]

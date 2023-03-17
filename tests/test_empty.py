from qq_chat_history import parse


lines = '''
===
假装我是文件头
===

其实只要不是时间开头，是什么都无所谓

关注永雏塔菲喵，关注永雏塔菲谢谢喵

嘻嘻喵
'''.strip().splitlines()


def test_empty() -> None:
    assert len(parse(lines)) == 0

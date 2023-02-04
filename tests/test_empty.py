from qq_chat_history import Parser


lines = '''
===
假装我是文件头
===

其实只要不是时间开头，是什么都无所谓

关注永雏塔菲喵，关注永雏塔菲谢谢喵

嘻嘻喵
'''.strip().splitlines()


def test_empty() -> None:
    parser_group = Parser.get_instance('group')
    parser_private = Parser.get_instance('private')

    assert not list(parser_group.parse(lines))
    assert not list(parser_private.parse(lines))

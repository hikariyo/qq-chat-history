# QQ 聊天记录提取器

## 简介

从 QQ 聊天记录文件中提取聊天信息，仅支持 `txt` 格式的聊天记录。


## 安装

使用 `pip` 安装，要求 `Python 3.9` 或以上版本。

```bash
> pip install -U qq-chat-history
```

## 使用

最简单的启动方式如下，它会自动在当前目录下创建 `output.json` 进行输出（如果安装到虚拟环境请确保已激活）。

```bash
> qq-chat-history /path/to/file.txt
```

启动时输入 `--help` 参数查看更多配置项。

```bash
> qq-chat-history --help
```

或者，可以作为一个第三方库使用，如下：

```python
import qq_chat_history

lines = '''
=========
假装我是 QQ 自动生成的文件头
=========

1883-03-07 11:22:33 A<someone@example.com>
关注永雏塔菲喵
关注永雏塔菲谢谢喵

1883-03-07 12:34:56 B(123123)
TCG

1883-03-07 13:24:36 C(456456)
TCG

1883-03-07 22:00:51 A<someone@example.com>
塔菲怎么你了
'''.strip().splitlines()

# 这里的 lines 也可以是文件对象或者以字符串或者 Path 对象表示的文件路径。
for msg in qq_chat_history.parse(lines):
    print(msg.date, msg.id, msg.name, msg.content)
```

注意 `parse` 方法返回的是一个 `Body` 对象，一般以 `Iterable[Message]` 的形式使用。当然 `Body` 也提供了几个函数，~虽然一般也没什么用~。

## Tips

+ 如果当作一个第三方库来用，例如 `find_xxx` 方法，可以从数据中查找指定 `id` 或 `name` 的消息；`save` 方法可以将数据以 `yaml` 或 `json` 格式保存到文件中，虽然这个工作一般都直接以 `CLI` 模式启动来完成。

+ 函数 `parse` 可以处理多样的类型。

  + `Iterable[str]`：迭代每行的可迭代对象，如 `list` 或 `tuple` 等。
  + `TextIOBase`：文本文件对象，如用 `open` 打开的文本文件，或者 `io.StringIO` 都属于文本文件对象。
  + `str`, `Path`：文件路径，如 `./data.txt`。

  这些参数都将以对应的方法来构造 `Body` 对象。

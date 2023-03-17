# QQ 聊天记录提取器

## 简介

从 QQ 聊天记录文件中提取聊天信息，仅支持 `txt` 格式的聊天记录。


## 安装

使用 `pip` 安装，要求 `Python 3.9` 或以上版本。

```bash
> pip install -U qq-chat-history
```

## 使用

你可以直接在终端中使用，如下（如果安装到虚拟环境请确保已激活）：

```bash
> qq-chat-history --help
```

按照提示传入指定参数，你也可以**不带参数启动**，按照提示输入参数。

或者，你可以在代码中使用，如下：

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

for msg in qq_chat_history.parse(lines):
    print(msg.date, msg.id, msg.name, msg.content)
```

注意 `parse` 方法返回的是一个 `Body` 对象，一般以 `Iterable[Message]` 的形式使用。除外，`Body` 也提供了几个函数，~虽然一般也没什么用~。

## Tips

+ 在 `0.3.0+` 版本中，对于 `parse` 方法的实现进行了大调整，它将返回一个 `Body` 类，原先是 `Iterable[Message]`。但这并**不会导致兼容性问题**，因为 `Body` 也是一个 `Iterable[Message]`。

  不同的是，`Body` 类相对于原先单纯的生成器**提供更多功能**，例如`find_xxx` 方法，可以从数据中查找指定 `id` 或 `name` 的消息；`save` 方法可以将数据以 `yaml` 或 `json` 格式保存到文件中，虽然这个工作一般都直接以 `CLI` 模式启动来完成。

+ 在 `0.3.0+` 版本中，你可以向 `parse` 中传入多种多样的类型。

  + `Iterable[str]`：迭代每行的可迭代对象，如 `list` 或 `tuple` 等。
  + `TextIOBase`：文本文件对象，如用 `open` 打开的文本文件，或者 `io.StringIO` 都属于文本文件对象。
  + `str`, `Path`：文件路径，如 `./data.txt`。

  这些参数都将被调用合适的工厂方法来构造 `Body` 对象。

+ 由于 `parse` 这个名字的含义比较不清晰，推荐与不推荐的使用方式如下：

  ```python
  # Not recommended 👎
  from qq_chat_history import parse
  parse(...)
  
  
  # Recommended 👍
  import qq_chat_history
  qq_chat_history.parse(...)
  
  
  from qq_chat_history import parse as parse_qq
  parse_qq(...)
  ```


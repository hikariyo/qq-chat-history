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

按照提示传入指定参数，你也可以不带参数直接启动，然后按照提示输入参数。

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

注意 `parse` 方法返回的是一个生成器。

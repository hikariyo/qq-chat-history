import re
from collections import deque
from functools import lru_cache
from io import TextIOBase
from itertools import dropwhile
from pathlib import Path
from typing import Iterable, Iterator, Optional, TextIO, Union, cast

import ujson
import yaml

from .message import Message, MessageBuilder

BRACKETS_REGEX = re.compile(r'[(<]([^()<>]*?)[>)]$')
DATE_HEAD_REGEX = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d\d?:\d{2}:\d{2})\s+')


class Body:
    """The parsed chat-history file body containing messages."""

    def __init__(self, messages: list[Message]) -> None:
        """Initializes the body with messages.

        It is not recommended to construct a body directly.
        Instead, you should use `from_xxx`, which are class methods.
        """
        self._messages = messages

    @staticmethod
    def _make_builder_from_head(line: str) -> Optional[MessageBuilder]:
        """Parses a message head, returns None if given line is not a message head."""
        if (date_matcher := DATE_HEAD_REGEX.search(line)) is None:
            return None
        date = date_matcher.group().strip()

        if matcher := BRACKETS_REGEX.findall(line):
            group_user_id = cast(str, matcher[-1])
            name = DATE_HEAD_REGEX.sub('', BRACKETS_REGEX.sub('', line)).strip()
            return MessageBuilder(date=date, id=group_user_id, name=name)

        if not (private_user_id := DATE_HEAD_REGEX.sub('', line)):
            return None
        return MessageBuilder(date=date, id=private_user_id, name=private_user_id)

    @staticmethod
    def _gen_from_builder(builder: Optional[MessageBuilder], content_lines: deque[str]) -> Iterable[Message]:
        """Generates a message from given builder, or nothing if the builder itself is None."""
        if builder is None:
            return

        yield builder.build_message(
            '\n'.join(
                content_lines.popleft() for _ in range(len(content_lines))
            ),
        )

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Body':
        """Creates a message group from lines."""
        messages: list[Message] = []
        builder: Optional[MessageBuilder] = None
        content_lines: deque[str] = deque()

        for line in dropwhile(lambda li: cls._make_builder_from_head(li) is None, lines):
            if next_builder := cls._make_builder_from_head(line):
                messages.extend(cls._gen_from_builder(builder, content_lines))
                builder = next_builder
            elif line:
                # Omit blank lines.
                content_lines.append(line)

        messages.extend(cls._gen_from_builder(builder, content_lines))
        return cls(messages)

    @classmethod
    def from_path(cls, path: Union[str, Path]) -> 'Body':
        """Creates a message group from path to certain file."""
        if isinstance(path, str):
            path = Path(path)
        return cls.from_lines(path.read_text('utf8'))

    def save(self, fp: TextIO, fmt: str, indent: int) -> None:
        """Saves the body to file, supporting `yaml` and `json` files."""
        data = [m.__dict__ for m in self._messages]

        if fmt == 'json':
            ujson.dump(
                data, fp,
                ensure_ascii=False,
                indent=indent,
            )
            return

        if fmt == 'yaml':
            yaml.dump(
                data, fp,
                allow_unicode=True,
                indent=indent,
                Dumper=yaml.CDumper,
            )
            return

        raise NameError(f'unknown format name {fmt}')

    def __iter__(self) -> Iterator[Message]:
        """Iterates over the messages."""
        yield from self._messages

    def __len__(self) -> int:
        """Counts the messages."""
        return len(self._messages)

    def find_names(self, id_: str) -> list[str]:
        """Gets all names used by given id."""
        return [msg.name for msg in self._messages if msg.id == id_]

    @lru_cache()
    def find_latest_name(self, id_: str) -> Optional[str]:
        """Gets the latest name used by given id."""
        if names := self.find_names(id_):
            return names[-1]
        return None

    def find_messages_by_id(self, id_: str) -> list[Message]:
        """Finds all messages by given id."""
        return [msg for msg in self._messages if msg.id == id_]

    def find_messages_by_name(self, name: str) -> list[Message]:
        """Finds all messages by given name."""
        return [msg for msg in self._messages if msg.name == name]

    def find_first_message_by_id(self, id_: str) -> Optional[Message]:
        """Finds first message by given id."""
        for msg in self._messages:
            if msg.id == id_:
                return msg
        return None

    def find_first_message_by_name(self, name: str) -> Optional[Message]:
        """Finds first message by given name."""
        for msg in self._messages:
            if msg.name == name:
                return msg
        return None


def parse(data: Union[Iterable[str], TextIOBase, str, Path]) -> Body:
    """Parses given data in a message group."""
    if isinstance(data, (str, Path)):
        return Body.from_path(data)

    if isinstance(data, TextIOBase):
        data = data.read().splitlines()

    return Body.from_lines(data)

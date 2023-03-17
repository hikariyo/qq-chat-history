import re
import yaml
import ujson
from pathlib import Path
from itertools import dropwhile
from collections import deque
from typing import Iterable, Iterator, Optional, cast, Union, TextIO
from .message import Message, MessageBuilder


BRACKETS_REGEX = re.compile(r'[(<]([^()<>]*?)[>)]$')
DATE_HEAD_REGEX = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d\d?:\d{2}:\d{2})\s+')


class Body:
    def __init__(self, messages: list[Message]) -> None:
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

        yield builder.build_message('\n'.join(
            content_lines.popleft() for _ in range(len(content_lines))
        ))

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
        """Saves the body to file."""

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


def parse(data: Union[Iterable[str], str, Path]) -> Body:
    """Parses given data in a message group."""

    if isinstance(data, (str, Path)):
        return Body.from_path(data)
    return Body.from_lines(data)

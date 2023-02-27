import re
from itertools import dropwhile
from collections import deque
from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, cast

from .message import Message


@dataclass()
class MessageBuilder:
    """
    Internal message without content, used when building messages.
    """

    date: str
    id: str
    name: str

    def build_message(self, content: str) -> Message:
        return Message(**self.__dict__, content=content)


BRACKETS_REGEX = re.compile(r'[(<]([^()<>]*?)[>)]$')
DATE_HEAD_REGEX = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d\d?:\d{2}:\d{2})\s+')


def _parse_message_head(line: str) -> Optional[MessageBuilder]:
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


def parse(lines: Iterable[str]) -> Iterable[Message]:
    """
    Parses given lines and returns a generator of messages.
    The id and name will always be the same for private messages.

    :param lines: lines from QQ chat history file.
    :return: a generator of messages.
    """

    builder: Optional[MessageBuilder] = None
    content_lines: deque[str] = deque()

    def generate_prev() -> Iterator[Message]:
        if builder is None:
            return

        yield builder.build_message('\n'.join(
            content_lines.popleft() for _ in range(len(content_lines))
        ))

    for line in dropwhile(lambda li: _parse_message_head(li) is None, lines):
        if next_builder := _parse_message_head(line):
            yield from generate_prev()
            builder = next_builder
        elif line:
            # Omit blank lines.
            content_lines.append(line)

    yield from generate_prev()

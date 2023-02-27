import re
from abc import ABC, abstractmethod
from collections import deque
from itertools import dropwhile
from typing import Type, Iterable, Iterator, Callable, Optional, cast

from .message import Message


BRACKETS_REGEX = re.compile(r'[(<]([^()<>]*?)[>)]$')
DATE_HEAD_REGEX = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d\d?:\d{2}:\d{2})\s+')


# The first one is date, and the second one is id.
MessageHead = tuple[str, str]


class Parser:
    """
    The parser to parse lines from a chat history file exported from QQ.
    >>> parser = Parser()
    >>> for line in parser.parse(...):
    >>>     ...
    """

    def __init__(self) -> None:
        self._names: dict[str, str] = {}

    @abstractmethod
    def _parse_message_head(self, line: str) -> Optional[MessageHead]:
        if not (date := DATE_HEAD_REGEX.search(line)):
            return None
        date = date.group().strip()

        if match := BRACKETS_REGEX.findall(line):
            group_id = cast(str, match[-1])
            self._names[group_id] = DATE_HEAD_REGEX.sub('', line[:-len(group_id) - 2]).strip()
            return date, group_id

        if not (private_id := DATE_HEAD_REGEX.sub('', line)):
            return None
        return date, private_id

    def parse(self, lines: Iterable[str]) -> Iterator[Message]:
        """
        Parses given lines and returns a generator of messages.
        The id and name will always be the same for private messages.

        :param lines: lines from QQ chat history file.
        :return: a generator of messages.
        """

        date = ''
        extracted_id = ''

        content_lines: deque[str] = deque()

        # Pops the elements while iterating the deque.
        def get_and_pop_lines() -> Iterator[str]:
            while content_lines:
                yield content_lines.popleft()

        # Generates only when extracted_id is not an empty string.
        def generate_prev() -> Iterator[Message]:
            if not extracted_id:
                return

            yield Message(
                date=date, id=extracted_id,
                content='\n'.join(get_and_pop_lines()),
                name=self._names.get(extracted_id, extracted_id),
            )

        for line in dropwhile(lambda li: self._parse_message_head(li) is None, lines):
            if message_head := self._parse_message_head(line):
                yield from generate_prev()
                date, extracted_id = message_head
            elif line:
                # Omit blank lines.
                content_lines.append(line)

        yield from generate_prev()


def parse(lines: Iterable[str]) -> Iterable[Message]:
    """
    Parses given lines and returns a generator of messages.
    The id and name will always be the same for private messages.

    :param lines: lines from QQ chat history file.
    :return: a generator of messages.
    """

    yield from Parser().parse(lines)

import re
from abc import ABC, abstractmethod
from collections import deque
from itertools import dropwhile
from typing import Type, Iterable, Iterator, Callable, Optional, cast

from .message import Message


ANGLE_BRACKETS_REGEX = re.compile(r'<([^<>]*?)>$')
BRACKETS_REGEX = re.compile(r'[(]([^()]*?)[)]$')
DATE_HEAD_REGEX = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d\d?:\d{2}:\d{2})\s+')


# The first one is date, and the second one is id.
MessageHead = tuple[str, str]


class Parser(ABC):
    """
    The parser to parse lines from a chat history file exported from QQ.
    >>> parser = Parser.get_instance('group')  # or private
    >>> for line in parser.parse(...):
    >>>     ...
    """

    @abstractmethod
    def _parse_message_head(self, line: str) -> Optional[MessageHead]:
        raise NotImplementedError()

    @abstractmethod
    def _get_display_name(self, extracted_id: str) -> str:
        raise NotImplementedError()

    def parse(self, lines: Iterable[str]) -> Iterator[Message]:
        """
        Parses given lines and returns a generator of messages.
        The id and name will always be the same for private parsers.
        :param lines: the lines from QQ chat history file.
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
                name=self._get_display_name(extracted_id),
            )

        for line in dropwhile(lambda li: self._parse_message_head(li) is None, lines):
            if message_head := self._parse_message_head(line):
                yield from generate_prev()
                date, extracted_id = message_head
            elif line:
                content_lines.append(line)

        yield from generate_prev()

    @staticmethod
    def get_instance(name: str) -> 'Parser':
        """
        Gets a parser by name, either "private" or "group".
        It is not cached because parsers may contain certain data after parsing.
        :param name: the name of the parser, private or group.
        :return: the parser.
        """

        if parser := parser_types.get(name):
            return parser()
        raise NameError(f'unknown parser name: {name}')


parser_types: dict[str, Type[Parser]] = {}


def register_parser(name: str) -> Callable[[Type[Parser]], Type[Parser]]:
    def inner(parser: Type[Parser]) -> Type[Parser]:
        parser_types[name] = parser
        return parser
    return inner


@register_parser('group')
class GroupParser(Parser):
    def __init__(self) -> None:
        super().__init__()
        self._names: dict[str, str] = {}

    def _parse_message_head(self, line: str) -> Optional[MessageHead]:
        if not (date := DATE_HEAD_REGEX.search(line)):
            return None

        for brackets in (BRACKETS_REGEX, ANGLE_BRACKETS_REGEX):
            if groups := brackets.findall(line):
                extracted_id = cast(str, groups[-1])
                self._names[extracted_id] = DATE_HEAD_REGEX.sub('', line[:-len(extracted_id) - 2]).strip()
                return date.group().strip(), extracted_id

        return None

    def _get_display_name(self, extracted_id: str) -> str:
        return self._names[extracted_id]


@register_parser('private')
class PrivateParser(Parser):
    def _parse_message_head(self, line: str) -> Optional[MessageHead]:
        if not (date := DATE_HEAD_REGEX.search(line)):
            return None
        if not (extracted_id := DATE_HEAD_REGEX.sub('', line)):
            return None
        return date.group().strip(), extracted_id

    def _get_display_name(self, extracted_id: str) -> str:
        return extracted_id

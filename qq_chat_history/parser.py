import re
import abc
from collections import deque
from itertools import dropwhile
from typing import Any, Type, Iterable, Iterator, cast

from .message import Message


ANGLE_BRACKETS_REGEX = re.compile(r'<([^<>]*?)>$')
BRACKETS_REGEX = re.compile(r'[(]([^()]*?)[)]$')
DATE_HEAD_REGEX = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d\d?:\d{2}:\d{2}\s*)')


class Parser(abc.ABC):
    """
    The parser to parse lines from a chat history file exported from QQ.
    >>> parser = Parser.get_instance('group')  # or private
    >>> for line in parser.parse(...):
    >>>     ...
    """

    @abc.abstractmethod
    def _extract_id(self, line: str) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
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
        def generate_one() -> Iterator[Message]:
            if not extracted_id:
                return

            yield Message(
                date=date, id=extracted_id,
                content='\n'.join(get_and_pop_lines()),
                name=self._get_display_name(extracted_id),
            )

        # Search for the date only after a blank line.
        encountered_blank = True
        for line in dropwhile(lambda li: not DATE_HEAD_REGEX.search(li), lines):
            if encountered_blank and (d := DATE_HEAD_REGEX.search(line)):
                yield from generate_one()
                extracted_id = self._extract_id(line)
                date = d.group().strip()
                encountered_blank = False
            elif line:
                content_lines.append(line)
            else:
                encountered_blank = True

        yield from generate_one()

    @staticmethod
    def get_instance(name: str) -> 'Parser':
        """
        Gets a parser by name, either "private" or "group".
        It is not cached because parsers may contain certain data after parsing.
        :param name: the name of the parser, private or group.
        :return: the parser.
        """

        return ParserMeta.get_parser_type(name)()


class ParserMeta(abc.ABCMeta):
    _parsers: dict[str, Type[Parser]] = {}

    def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> Type[Parser]:
        assert Parser in bases
        assert '__parser_name__' in attrs

        t = cast(Type[Parser], super().__new__(mcs, name, bases, attrs))
        mcs._parsers[attrs['__parser_name__']] = t
        return t

    @classmethod
    def get_parser_type(mcs, name: str) -> Type[Parser]:
        if parser := mcs._parsers.get(name):
            return parser
        raise NameError(f'unknown parser name: {name}')


class GroupParser(Parser, metaclass=ParserMeta):
    __parser_name__ = 'group'

    def __init__(self) -> None:
        super().__init__()
        self._names: dict[str, str] = {}

    def _extract_id(self, line: str) -> str:
        for brackets in (BRACKETS_REGEX, ANGLE_BRACKETS_REGEX):
            if groups := brackets.findall(line):
                extracted_id = cast(str, groups[-1])
                self._names[extracted_id] = DATE_HEAD_REGEX.sub('', line[:-len(extracted_id) - 2]).strip()
                return extracted_id

        raise LookupError(f'cannot find id in line {line}')

    def _get_display_name(self, extracted_id: str) -> str:
        return self._names[extracted_id]


class PrivateParser(Parser, metaclass=ParserMeta):
    __parser_name__ = 'private'

    def _extract_id(self, line: str) -> str:
        return DATE_HEAD_REGEX.sub('', line)

    def _get_display_name(self, extracted_id: str) -> str:
        return extracted_id

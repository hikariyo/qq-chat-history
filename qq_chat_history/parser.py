import re
import abc
import collections
from itertools import dropwhile
from typing import Type, Iterable, Generator, cast

from .message import Message


ANGLE_BRACKETS_REGEX = re.compile(r'<(.*?)>')
BRACKETS_REGEX = re.compile(r'[(](.*?)[)]')
DATE_HEAD_REGEX = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d\d?:\d{2}:\d{2}\s*)')


class Parser(abc.ABC):
    """
    The parser to parse lines from chat history file exported from QQ.
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

    def parse(self, lines: Iterable[str]) -> Generator[Message, None, None]:
        """
        Parses given lines.
        The id and name will always be the same for private parsers.
        :param lines: the lines from QQ chat history file.
        :return: a generator of messages.
        """

        date = ''
        extracted_id = ''

        # I don't know why mypy needs this annotation.
        content_lines: collections.deque = collections.deque()

        # Pops the elements while iterating the deque.
        def get_and_pop_lines():
            while content_lines:
                yield content_lines.popleft()

        # Generates only when extracted_id is not an empty string.
        def generate():
            if not extracted_id:
                return

            yield Message(
                date=date, id=extracted_id,
                content='\n'.join(get_and_pop_lines()),
                name=self._get_display_name(extracted_id),
            )

        for line in dropwhile(lambda li: not DATE_HEAD_REGEX.search(li), lines):
            if d := DATE_HEAD_REGEX.search(line):
                yield from generate()
                extracted_id = self._extract_id(line)
                date = d.group().strip()

            elif line:
                # Skip blank lines.
                content_lines.append(line)

        yield from generate()

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

    def __new__(mcs, name, bases, attrs) -> Type[Parser]:
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
                id_ = groups[-1]
                self._names[id_] = DATE_HEAD_REGEX.sub('', line[:-len(id_) - 2]).strip()
                return id_

        raise LookupError(f'cannot find id in line {line}')

    def _get_display_name(self, extracted_id: str) -> str:
        return self._names[extracted_id]


class PrivateParser(Parser, metaclass=ParserMeta):
    __parser_name__ = 'private'

    def _extract_id(self, line: str) -> str:
        return DATE_HEAD_REGEX.sub('', line)

    def _get_display_name(self, extracted_id: str) -> str:
        return extracted_id

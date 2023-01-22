import re
import abc
import collections
from itertools import dropwhile
from typing import Type, Iterable, Generator, cast


ANGLE_BRACKETS_REGEX = re.compile(r'<(.*?)>')
BRACKETS_REGEX = re.compile(r'[(](.*?)[)]')
DATE_HEAD_REGEX = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d\d?:\d{2}:\d{2}\s*)')


class Parser(abc.ABC):
    @abc.abstractmethod
    def _extract_id(self, line: str) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_display_name(self, extracted_id: str) -> str:
        raise NotImplementedError()

    def parse(self, lines: Iterable[str]) -> Generator[dict[str, str], None, None]:
        """
        Parses given lines.
        The id and name will always be the same for private parsers.
        :param lines: the lines from QQ chat history file.
        :return: a generator to generate messages in dict with date, id, name and content.
        """

        extracted_id = ''
        content_lines = collections.deque()

        # Pops the elements while iterating the deque.
        def get_and_pop_lines():
            while content_lines:
                yield content_lines.popleft()

        for line in dropwhile(lambda l: not DATE_HEAD_REGEX.search(l), lines):
            if date := DATE_HEAD_REGEX.search(line):
                # Skips the first line only.
                if extracted_id:
                    yield {
                        'date': date.group().strip(),
                        'id': extracted_id,
                        'name': self._get_display_name(extracted_id),
                        'content': '\n'.join(get_and_pop_lines()),
                    }
                extracted_id = self._extract_id(line)
            elif line:
                # Skip blank lines.
                content_lines.append(line)

    @staticmethod
    def get_instance(name: str) -> 'Parser':
        """
        Gets the parser by its name.
        It is not cached because parsers may contain certain data after parsing.
        :param name: the name of the parser, private or group.
        :return: the parser.
        """

        return ParserMeta.get_instance(name)


class ParserMeta(abc.ABCMeta):
    parsers: dict[str, Type[Parser]] = {}

    def __new__(mcs, name, bases, attrs) -> Type[Parser]:
        assert Parser in bases
        assert '__parser_name__' in attrs

        t = cast(Type[Parser], super().__new__(mcs, name, bases, attrs))
        mcs.parsers[attrs['__parser_name__']] = t
        return t

    @classmethod
    def get_instance(mcs, name: str) -> Parser:
        if parser := mcs.parsers.get(name):
            return parser()
        raise NameError(f'unknown parser name: {name}')


class GroupParser(Parser, metaclass=ParserMeta):
    __parser_name__ = 'group'

    def __init__(self):
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

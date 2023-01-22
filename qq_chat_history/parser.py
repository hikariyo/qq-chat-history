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
    def extract_id(self, line: str) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_display_name(self, extracted_id: str) -> str:
        raise NotImplementedError()

    def parse(self, lines: Iterable[str]) -> Generator[dict[str, str], None, None]:
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
                        'name': self.get_display_name(extracted_id),
                        'content': '\n'.join(get_and_pop_lines()),
                    }
                extracted_id = self.extract_id(line)
            elif line:
                # Skip blank lines.
                content_lines.append(line)


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

    def extract_id(self, line: str) -> str:
        for brackets in (BRACKETS_REGEX, ANGLE_BRACKETS_REGEX):
            if groups := brackets.findall(line):
                id_ = groups[-1]
                self._names[id_] = DATE_HEAD_REGEX.sub('', line[:-len(id_) - 2]).strip()
                return id_

        raise LookupError(f'cannot find id in line {line}')

    def get_display_name(self, extracted_id: str) -> str:
        return self._names[extracted_id]


class PrivateParser(Parser, metaclass=ParserMeta):
    __parser_name__ = 'private'

    def extract_id(self, line: str) -> str:
        return DATE_HEAD_REGEX.sub('', line)

    def get_display_name(self, extracted_id: str) -> str:
        return extracted_id

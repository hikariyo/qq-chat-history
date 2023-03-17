import yaml
import ujson
from abc import ABC, abstractmethod
from typing import TextIO, Any, Type

from .message import MessageGroup


class Formatter(ABC):
    _formatters: dict[str, Type['Formatter']] = {}

    def __init_subclass__(cls, kind: str = '', **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._formatters[kind] = cls

    @classmethod
    def get(cls, kind: str) -> 'Formatter':
        if formatter := cls._formatters.get(kind):
            return formatter()
        raise TypeError(f'unknown formatter kind: {kind}')

    @abstractmethod
    def format(self, *, fp: TextIO, messages: MessageGroup, indent: int) -> None:
        raise NotImplementedError()


class JSONFormatter(Formatter, kind='json'):
    def format(self, *, fp: TextIO, messages: MessageGroup, indent: int) -> None:
        ujson.dump(
            [m.__dict__ for m in messages], fp,
            ensure_ascii=False,
            indent=indent,
        )


class YAMLFormatter(Formatter, kind='yaml'):
    def format(self, *, fp: TextIO, messages: MessageGroup, indent: int) -> None:
        yaml.dump(
            [m.__dict__ for m in messages], fp,
            allow_unicode=True,
            indent=indent,
            Dumper=yaml.CDumper,
        )

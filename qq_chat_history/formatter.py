import yaml
import ujson
from typing import TextIO, Iterable

from .message import Message


def format_json(fp: TextIO, messages: Iterable[Message], indent: int = 2) -> None:
    ujson.dump([m.__dict__ for m in messages], fp, ensure_ascii=False, indent=indent)


def format_yaml(fp: TextIO, messages: Iterable[Message], indent: int = 2) -> None:
    yaml.safe_dump([m.__dict__ for m in messages], fp, allow_unicode=True, indent=indent)


formatters = {
    'json': format_json,
    'yaml': format_yaml,
}

from dataclasses import dataclass


@dataclass()
class Message:
    """It represents messages in the file exported from QQ."""

    date: str
    id: str
    name: str
    content: str


@dataclass()
class MessageBuilder:
    """The builder of messages for internal use."""

    date: str
    id: str
    name: str

    def build_message(self, content: str) -> Message:
        return Message(**self.__dict__, content=content)

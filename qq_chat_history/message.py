from dataclasses import dataclass


@dataclass()
class Message:
    """
    Represents messages in the file exported from QQ.
    """

    date: str
    id: str
    name: str
    content: str

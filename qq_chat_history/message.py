from dataclasses import dataclass


@dataclass()
class Message:
    """
    Represents messages in the export-file.
    """

    date: str
    id: str
    name: str
    content: str

import click
import ujson
from pathlib import Path

from . import Parser


@click.command()
@click.option('--file-type', '-t', prompt='File type', help='The file type.', type=click.Choice(['private', 'group']))
@click.option('--indent', '-d', prompt='Output indent', help='JSON indent.', type=int, default=2, prompt_required=False)
@click.option('--input-file', '-i', prompt='Input file path', help='Input file path.',
              type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--output-file', '-o', prompt='Output JSON file path', help='Output JSON file path.',
              type=click.Path(dir_okay=False, path_type=Path), default='output.json', prompt_required=False)
def run(input_file: Path, output_file: Path, file_type: str, indent: int) -> None:
    parser = Parser.get_instance(file_type)
    lines = input_file.read_text('utf8').splitlines()
    messages = [msg.__dict__ for msg in parser.parse(lines)]
    with output_file.open('w', encoding='utf8') as f:
        ujson.dump(messages, f, ensure_ascii=False, indent=indent)

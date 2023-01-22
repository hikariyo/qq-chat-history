import click
import ujson
from pathlib import Path

from . import ParserMeta


@click.command()
@click.option('--file-type', '-t', prompt='File type', type=click.Choice(['private', 'group']))
@click.option('--indent', '-d', prompt='Output indent', type=int, default=2, prompt_required=False)
@click.option('--input-file', '-i', prompt='Input file path',
              type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--output-file', '-o', prompt='Output file path',
              type=click.Path(dir_okay=False, path_type=Path),
              default='output.json', prompt_required=False)
def run(input_file: Path, output_file: Path, file_type: str, indent: int):
    parser = ParserMeta.get_instance(file_type)
    lines = input_file.read_text('utf8').splitlines()
    parsed_lines = list(parser.parse(lines))
    with output_file.open('w', encoding='utf8') as f:
        ujson.dump(parsed_lines, f, ensure_ascii=False, indent=indent)

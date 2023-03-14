import click
from pathlib import Path

from . import parse
from .formatter import formatters


@click.command()
@click.option('--indent', '-d', prompt='Output indent', help='Output file indent.', type=int, default=2, prompt_required=False)
@click.option('--input-file', '-i', prompt='Input file path', help='Input file path.',
              type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--output-file', '-o', prompt='Output file path(format will be filled automatically)',
              help='Output file path.', type=click.Path(dir_okay=False, path_type=Path), default='output',
              prompt_required=False)
@click.option('--output-format', '-f', prompt='Output format', help='Output file format.',
              type=click.Choice(['json', 'yaml']), default='json')
def run(input_file: Path, output_file: Path, output_format: str, indent: int) -> None:
    if not output_file.suffix:
        output_file = output_file.with_suffix(f'.{output_format}')
    lines = input_file.read_text('utf8').splitlines()
    with output_file.open('w', encoding='utf8') as fp:
        formatters[output_format](fp, parse(lines), indent)

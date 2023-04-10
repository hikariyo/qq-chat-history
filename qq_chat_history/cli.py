from pathlib import Path

import click

from . import parse


@click.command()
@click.argument('input-file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    '--output-file', '-o', help='Output file path, with extension name auto-corrected.',
    type=click.Path(dir_okay=False, path_type=Path), default='output.json', show_default=True,
)
@click.option(
    '--output-format', '-f', help='Output file format.',
    type=click.Choice(['json', 'yaml']), default='json', show_default=True,
)
@click.option('--indent', '-d', help='Output file indent.', type=int, default=2, show_default=True)
def run(input_file: Path, output_file: Path, output_format: str, indent: int) -> None:
    """Parses a chat history file in the CLI."""
    if output_file.suffix[1:] != output_format:
        output_file = output_file.with_suffix(f'.{output_format}')

    with output_file.open('w', encoding='utf8') as fp:
        parse(input_file).save(fp, output_format, indent)

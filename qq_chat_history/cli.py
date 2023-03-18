import click
from pathlib import Path

from . import parse


@click.command()
@click.option('--indent', '-d', prompt='Output indent', help='Output file indent.', type=int, default=2)
@click.option(
    '--input-file', '-i', prompt='Input file path', help='Input file path.',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    '--output-file', '-o', prompt='Output file path(will format filled automatically)',
    help='Output file path.', type=click.Path(dir_okay=False, path_type=Path), default='output',
)
@click.option(
    '--output-format', '-f', prompt='Output format', help='Output file format.',
    type=click.Choice(['json', 'yaml']), default='json',
)
def run(input_file: Path, output_file: Path, output_format: str, indent: int) -> None:
    """The entrance of CLI."""
    if not output_file.suffix:
        output_file = output_file.with_suffix(f'.{output_format}')

    with output_file.open('w', encoding='utf8') as fp:
        parse(input_file).save(fp, output_format, indent)

from typer.testing import CliRunner

from generate_linkml_from_aind import app

runner = CliRunner()


def test_smoke_cli():
    result = runner.invoke(app)
    assert result.exit_code == 0
from typer.testing import CliRunner
from nrobo.cli import app

runner = CliRunner()

def test_help_message():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--suite" in result.output

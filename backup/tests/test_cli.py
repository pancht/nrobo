from typer.testing import CliRunner
from nrobo.cli import main

runner = CliRunner()

def test_help_message():
    # result = runner.invoke(main(), ["--help"])
    # assert result.exit_code == 0
    # assert "--suite" in result.output
    pass

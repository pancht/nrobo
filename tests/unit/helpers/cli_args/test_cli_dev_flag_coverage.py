import os
import sys

from nrobo.core import settings
from nrobo.core.exceptions import NoSubCommandFoundByArgParser
from nrobo.helpers.cli_parser import get_nrobo_arg_parser


def test_cli_dev_flag_sets_env_and_injects_pytest_arg(mocker):
    """
    Covers:
      - settings.NROBO_DEV_DEBUG = True
      - os.environ["NROBO_DEV_DEBUG"] = "True"
      - '--dev' injected into unknown_args
    """

    # -------------------------------------------------
    # Patch control-flow gates
    # -------------------------------------------------
    mocker.patch(
        "nrobo.helpers.cli_parser._handle_subcommand_if_any",
        side_effect=NoSubCommandFoundByArgParser("No subcommand"),
    )
    mocker.patch("nrobo.helpers.cli_parser.copy_configs_if_updated", return_value=None)
    mocker.patch("nrobo.helpers.cli_parser.check_if_nrobo_initialized", return_value=None)
    mocker.patch("sys.exit")  # safety

    # -------------------------------------------------
    # Patch sys.argv (THIS is the missing piece)
    # -------------------------------------------------
    mocker.patch.object(
        sys,
        "argv",
        [
            "nrobo",
            "--dev",
            "--engine=selenium",
        ],
    )

    # -------------------------------------------------
    # Clean state
    # -------------------------------------------------
    settings.NROBO_DEV_DEBUG = False
    os.environ.pop("NROBO_DEV_DEBUG", None)

    # -------------------------------------------------
    # Act
    # -------------------------------------------------
    suites, browser, args, unknown_args = get_nrobo_arg_parser()

    # -------------------------------------------------
    # Assert (coverage lines)
    # -------------------------------------------------
    assert args.dev is True
    assert settings.NROBO_DEV_DEBUG is True
    assert os.environ["NROBO_DEV_DEBUG"] == "True"

    assert "--dev" in unknown_args
    assert unknown_args[0] == "--dev"

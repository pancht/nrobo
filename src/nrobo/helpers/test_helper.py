import textwrap
from pathlib import Path

from nrobo.utils.common_utils import generate_custom_id


def _create_a_passing_test(test_dir: Path) -> Path:
    test_dir.mkdir(parents=True, exist_ok=True)
    fake_test_py_file = test_dir / f"test_passing_unit_test_{generate_custom_id()}.py"
    fake_test_py_file.write_text(
        textwrap.dedent(
            """
        def test_addition():
            assert 1 + 1 == 2
    """
        )
    )
    return fake_test_py_file


def _create_a_failing_test(test_dir: Path) -> Path:
    test_dir.mkdir(parents=True, exist_ok=True)
    fake_test_py_file = test_dir / f"test_failing_unit_test_{generate_custom_id()}.py"
    fake_test_py_file.write_text(
        textwrap.dedent(
            """
        def test_addition():
            assert 1 + 1 == 3
    """
        )
    )
    return fake_test_py_file


def _create_a_failing_ui_test(test_dir: Path) -> Path:
    test_dir.mkdir(parents=True, exist_ok=True)
    fake_test_py_file = test_dir / f"test_failing_ui_test_{generate_custom_id()}.py"
    fake_test_py_file.write_text(
        textwrap.dedent(
            """
            import pytest

            from nrobo.selenium_wrappers.nrobo_selenium_wrapper import (  # noqa: E501
                NRoboSeleniumWrapperClass,
            )
            from nrobo.templates.home_page import PageHome

            def test_google_home_loading_failing_test(nrobo: NRoboSeleniumWrapperClass):  # noqa: E501
                google_home_page = PageHome(nrobo)
                url = "https://www.google.com"
                nrobo.logger.info(f"Open {url}")
                google_home_page.get(url)
                assert not google_home_page.is_page_visible()
            """
        )
    )
    return fake_test_py_file


def _create_coveragerc_tmp_file(root_path: Path):
    root_path.mkdir(parents=True, exist_ok=True)
    configs_dir = root_path / "configs"
    configs_dir.mkdir(parents=True, exist_ok=True)
    coveragerc_path = configs_dir / ".coveragerc"
    coveragerc_path.write_text(
        textwrap.dedent(
            f"""
            [run]
            patch = subprocess
            branch = True
            source = {root_path}
            disable_warnings = no-data-collected
            omit =
                */__init__.py
                */venv/*
                */.venv/*
                */node_modules/*
                */backup/*

            [report]
            show_missing = True
            skip_covered = True
            """
        )
    )
    return coveragerc_path

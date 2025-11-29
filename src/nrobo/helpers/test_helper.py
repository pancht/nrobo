import textwrap
from pathlib import Path


def _create_sample_test(test_dir: Path):
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "test_sample.py").write_text(
        textwrap.dedent(
            """
        def test_addition():
            assert 1 + 1 == 2
    """
        )
    )


def _create_coveragerc_tmp_file(root_path: Path):
    root_path.mkdir(parents=True, exist_ok=True)
    (root_path / ".coveragerc").write_text(
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
    return root_path / ".coveragerc"

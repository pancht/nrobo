import textwrap
from pathlib import Path


def _create_passing_test(test_dir: Path):
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "test_sample.py").write_text(
        textwrap.dedent(
            """
        def test_addition():
            assert 1 + 1 == 2
    """
        )
    )

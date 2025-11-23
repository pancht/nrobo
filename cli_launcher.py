import argparse
import yaml
import pytest
import sys
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        prog="nrobo",
        description="NROBO - Smart pytest launcher with YAML-based suite management"
    )

    # NROBO custom options
    parser.add_argument("--suite", type=str, help="Path to YML test suite file")
    parser.add_argument("--env", type=str, default="dev", help="Environment name")
    parser.add_argument("--nrobo-msg", type=str, default="NROBO Launcher", help="Startup message")

    # Collect all remaining args (passed to pytest)
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER,
                        help="All pytest command-line options (e.g., -v, -k, --html=report.html)")

    return parser.parse_args()

def load_suite(file_path):
    if not Path(file_path).exists():
        print(f"❌ Suite file not found: {file_path}")
        sys.exit(1)

    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("suite", {}).get("tests", [])

def main():
    args = parse_args()

    print(f"🚀 {args.nrobo_msg}")
    print(f"🧩 Environment: {args.env}")

    test_list = []
    if args.suite:
        test_list = load_suite(args.suite)
        print(f"📘 Loaded {len(test_list)} tests from {args.suite}")

    # Combine YAML-defined tests with pytest args
    pytest_args = test_list + args.pytest_args
    print(f"▶ Running pytest with args: {pytest_args}")

    sys.exit(pytest.main(pytest_args))

if __name__ == "__main__":
    main()

import argparse
import os

ARTIFACT_DIR = "test_artifacts"


def clean_artifacts(verbose=False):
    for root, dirs, files in os.walk(ARTIFACT_DIR, topdown=False):
        for f in files:
            if f != ".gitkeep":
                file_path = os.path.join(root, f)
                os.remove(file_path)
                if verbose:
                    print(f"🗑️ Deleted file: {file_path}")
        for d in dirs:
            dir_path = os.path.join(root, d)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                if verbose:
                    print(f"📂 Removed empty dir: {dir_path}")
    print("✅ test_artifacts cleaned.")


def run(args):
    parser = argparse.ArgumentParser(
        description="Clean test_artifacts directory (preserving .gitkeep)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed file deletion logs"
    )
    parsed_args = parser.parse_args(args)

    if os.path.exists(ARTIFACT_DIR):
        clean_artifacts(verbose=parsed_args.verbose)
    else:
        print(f"⚠️ Directory '{ARTIFACT_DIR}' does not exist.")

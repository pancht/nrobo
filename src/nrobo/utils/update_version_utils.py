import re
from pathlib import Path


def update_version_file(version_file_path: str, new_version: str):
    path = Path(version_file_path)

    if not path.exists():
        raise FileNotFoundError(f"❌ File not found: {version_file_path}")

    content = path.read_text()

    # Regex to find the __version__ assignment
    updated_content, count = re.subn(
        r'__version__\s*=\s*[\'"](.+?)[\'"]', f'__version__ = "{new_version}"', content
    )

    if count == 0:
        raise ValueError("⚠️ Could not find a __version__ assignment to update.")

    path.write_text(updated_content)
    print(f"✅ Version updated to {new_version} in {version_file_path}")

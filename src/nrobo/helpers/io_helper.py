import shutil
from pathlib import Path

include_files = [".env"]


def is_sync_needed(source: Path, dest: Path) -> bool:
    if not dest.exists():
        return True

    for src_file in source.rglob("*"):
        if src_file.is_file() and src_file.name in include_files:
            relative_path = src_file.relative_to(source)
            dest_file = dest / relative_path

            if not dest_file.exists():
                return True

            if src_file.stat().st_mtime > dest_file.stat().st_mtime:
                return True

    return False


def copy_configs_if_updated():
    project_root = Path.cwd()
    source_dir = project_root / "configs"
    dest_dir = project_root / "src" / "nrobo" / "templates" / "configs"

    if not source_dir.exists():
        raise FileNotFoundError(f"❌ Source directory not found: {source_dir}")

    if is_sync_needed(source_dir, dest_dir):
        # Make sure destination exists
        dest_dir.mkdir(parents=True, exist_ok=True)

        for file in source_dir.iterdir():
            if file.is_file() and file.name in include_files:
                _file_name = ".nrobo_env" if file.name == ".env" else file.name
                shutil.copy2(file, dest_dir / _file_name)
                print(f"✅ Copied {file.name} → {dest_dir}")
                print("✅ Configs copied (updates detected).")

    else:
        print("🟢 Skipped copy (configs already up to date).")

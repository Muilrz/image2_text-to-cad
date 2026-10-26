#!/usr/bin/env python3
"""Optionally archive canonical repository source; never rewrite source or create a second source tree."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ("README.md", "LICENSE", "NOTICE.md", "CHANGELOG.md", "PUBLISHING.md",
         "UPSTREAM.json", "AB_TEST_TEMPLATE.md", ".gitignore", ".gitattributes")
DIRECTORIES = (".github/workflows", ".agents/plugins", "plugins/text-to-cad-visual", "tests", "scripts")
SKIP = {".git", "__pycache__", ".venv", ".tmp", "dist", ".cad_context"}


def source_files():
    selected = {ROOT / name for name in FILES}
    for name in DIRECTORIES:
        selected.update(p for p in (ROOT / name).rglob("*") if p.is_file())
    return sorted(p for p in selected if not (set(p.relative_to(ROOT).parts) & SKIP)
                  and p.suffix not in (".pyc", ".log")
                  and (not p.name.startswith(".env") or p.name == ".env.example"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    files = source_files()
    for path in files:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing source or unsupported symlink: {path}")
        if path.suffix in (".md", ".json", ".py", ".yaml", ".yml", ".toml"):
            text = path.read_text(encoding="utf-8-sig")
            home_prefixes = ("C:" + chr(92) + "Users" + chr(92), "C:" + "/Users/")
            if any(prefix in text for prefix in home_prefixes):
                raise ValueError(f"Machine-specific path in source: {path.relative_to(ROOT)}")
    if args.dry_run:
        print(json.dumps({"dry_run":True, "files":[p.relative_to(ROOT).as_posix() for p in files]}, indent=2))
        return
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    archive = args.output or ROOT / "dist" / f"text-to-cad-visual-{stamp}.zip"
    archive = archive.resolve()
    if archive in files:
        raise ValueError("Archive cannot overwrite a source file")
    archive.parent.mkdir(parents=True, exist_ok=True)
    manifest = {}
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as stream:
        for path in files:
            name = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            stream.writestr("text-to-cad-visual/" + name, data)
            manifest[name] = hashlib.sha256(data).hexdigest()
        stream.writestr("text-to-cad-visual/MANIFEST.sha256.json", json.dumps(manifest, indent=2) + "\n")
    with zipfile.ZipFile(archive) as stream:
        if stream.testzip() is not None:
            raise ValueError("Archive integrity check failed")
    print(json.dumps({"zip":str(archive), "files":len(files),
                      "sha256":hashlib.sha256(archive.read_bytes()).hexdigest()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

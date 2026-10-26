#!/usr/bin/env python3
"""Verify inherited file scope, licensing and runtime; optionally check the local original."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORK = ROOT / "plugins/text-to-cad-visual"
ALLOWED = {".claude-plugin/marketplace.json", "plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json",
           ".cursor-plugin/plugin.json", "gemini-extension.json", "codex.mcp.json",
           "claude.mcp.json", "cursor.mcp.json", "mcp.json", "README.md",
           "skills/cad/SKILL.md", "skills/cad/references/cad-brief.md"}
REMOVED = {".codex-plugin/logo.png", ".claude-plugin/icon.png"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    upstream = json.loads((ROOT / "UPSTREAM.json").read_text(encoding="utf-8"))
    expected_files = upstream["original_file_sha256"]
    local_file = ROOT / "baseline.json"
    local = json.loads(local_file.read_text(encoding="utf-8")) if local_file.is_file() else None
    original = Path(local["source"]) if local else None
    errors, changes = [], []
    checked = 0
    for name, expected in expected_files.items():
        if original is not None:
            path = original / name
            if not path.is_file() or sha(path) != expected:
                errors.append(f"Baseline changed or missing: {name}")
            checked += 1
        fork_path = FORK / ("UPSTREAM_README.md" if name == "README.md" else name)
        if name in REMOVED:
            if fork_path.exists():
                errors.append(f"Official branding unexpectedly retained: {name}")
            continue
        if name not in ALLOWED and (not fork_path.is_file() or sha(fork_path) != expected):
            errors.append(f"Unexpected inherited change: {name}")
        if fork_path.is_file() and sha(fork_path) != expected:
            changes.append(name)
    manifest = json.loads((FORK / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    if manifest["name"] != "text-to-cad-visual":
        errors.append("Fork plugin identity collides with baseline")
    servers = json.loads((FORK / "codex.mcp.json").read_text(encoding="utf-8"))["mcpServers"]
    if set(servers) != {"cad_visual"}:
        errors.append("Fork MCP identity collides with baseline")
    args = servers.get("cad_visual", {}).get("args", [])
    if "cadgen==" + upstream["upstream_version"] not in args:
        errors.append("CAD runtime pin differs from upstream version")
    if original is not None and (original / "codex.mcp.json").is_file():
        old = json.loads((original / "codex.mcp.json").read_text(encoding="utf-8"))["mcpServers"]["cad"]
        actual = dict(servers.get("cad_visual", {}))
        if actual.pop("cwd", None) != ".":
            errors.append("Custom GUI cwd must be the plugin root")
        actual["env"] = dict(actual.get("env", {}))
        if actual["env"].pop("CADGEN_MCP_APP_DIR", None) != "gui":
            errors.append("Custom GUI resource override missing")
        if actual != old:
            errors.append("CAD runtime command differs from original")
    gui = FORK / "gui"
    if not (gui / "index.html").is_file() or not (gui / "source.json").is_file():
        errors.append("Custom GUI files missing")
    else:
        gui_source = json.loads((gui / "source.json").read_text(encoding="utf-8"))
        if sha(gui / "index.html") != gui_source["custom_html_sha256"]:
            errors.append("Custom GUI hash differs from its provenance")
        if gui_source["upstream_version"] != upstream["upstream_version"]:
            errors.append("GUI and CAD runtime versions differ")
        if not (gui / "LICENSE").is_file() or sha(gui / "LICENSE") != expected_files["LICENSE"]:
            errors.append("GUI upstream MIT license missing or changed")
    for path in FORK.rglob("*.json"):
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(doc, dict) and isinstance(doc.get("author"), dict):
            if doc["author"].get("name") != "Ming Liu":
                errors.append(f"Author name is not Ming Liu: {path.relative_to(FORK)}")
    license_path = FORK / "LICENSE"
    if not license_path.is_file() or sha(license_path) != expected_files["LICENSE"]:
        errors.append("Upstream MIT license was not preserved")
    if not (ROOT / "LICENSE").is_file() or (ROOT / "LICENSE").read_bytes() != license_path.read_bytes():
        errors.append("Repository and plugin licenses differ")
    print(json.dumps({"ok":not errors, "baseline_files_checked":checked,
                      "upstream_files_recorded":len(expected_files), "inherited_changes":changes,
                      "removed_brand_assets":sorted(REMOVED), "errors":errors}, indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())

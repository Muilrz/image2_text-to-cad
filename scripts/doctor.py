#!/usr/bin/env python3
"""Check local command availability without model calls, installs, or config changes."""
import json
import shutil
import subprocess
import sys

REQUIRED_EXEC_FLAGS = ("--image", "--output-schema", "--output-last-message", "--ephemeral",
                       "--sandbox", "--skip-git-repo-check", "--cd")


def check_command(label, command, required=()):
    executable = shutil.which(command[0])
    if not executable:
        return {"check": label, "ok": False, "detail": f"{command[0]} is not on PATH"}
    try:
        options = {"capture_output": True, "text": True, "encoding": "utf-8", "errors": "replace", "timeout": 20}
        if sys.platform == "win32":
            options["creationflags"] = subprocess.CREATE_NO_WINDOW
        result = subprocess.run([executable, *command[1:]], **options)
        output = result.stdout + result.stderr
        missing = [flag for flag in required if flag not in output]
        ok = result.returncode == 0 and not missing
        detail = ("Required command/flags available" if required else result.stdout.strip()[:160]) if ok else (
            "Missing flags: " + ", ".join(missing) if missing else f"Command failed (exit {result.returncode}); run {' '.join(command)} in your terminal")
        return {"check": label, "ok": ok, "detail": detail}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"check": label, "ok": False, "detail": type(exc).__name__ + "; run the command in your terminal"}


def main():
    checks = [{"check": "Python", "ok": sys.version_info >= (3, 10), "detail": sys.version.split()[0]}]
    checks.append(check_command("Codex version", ["codex", "--version"]))
    checks.append(check_command("Codex plugin CLI", ["codex", "plugin", "marketplace", "add", "--help"]))
    checks.append(check_command("Inspector CLI flags", ["codex", "exec", "--help"], REQUIRED_EXEC_FLAGS))
    checks.append(check_command("uvx", ["uvx", "--version"]))
    ok = all(item["ok"] for item in checks)
    print(json.dumps({"ok": ok, "checks": checks, "not_checked": [
        "Codex login: run codex login status", "Model/image access and network", "CAD runtime download and geometry generation"]}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

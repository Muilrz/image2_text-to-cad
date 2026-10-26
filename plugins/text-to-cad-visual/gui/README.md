# Experimental CAD Viewer GUI

This is the experiment's own GUI resource, loaded by Codex through the experimental
plugin's MCP configuration. It does not modify the upstream plugin or shared
cadgen installation.

- Author text: original earthtojake attribution followed by `, Ming Liu` (all five
  bundled UI languages).
- GitHub: https://github.com/Muilrz/image2_text-to-cad
- Feedback: https://github.com/Muilrz/image2_text-to-cad/issues/new
- Version, Discord, original author X link, controls and CAD rendering stay as in
  upstream cadgen 0.7.24.

`index.html` is self-contained. `source.json` records the upstream and custom page
hashes. Its embedded font licenses and third-party notices are preserved, and the
upstream MIT license is copied as `LICENSE` here. The changed JavaScript chunk's
original source-map ID is removed so errors are not mapped to unchanged upstream
source. Other chunks and their IDs remain unchanged.

Rebuild from the pinned runtime using its Python interpreter:

```sh
uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.24 python scripts/customize_gui.py
```

Alternatively pass `--upstream-html /path/to/cadgen/_runtime/mcp/index.html`.
The script checks the exact upstream page hash before changing anything. Review
and update the patch explicitly when upgrading the CAD runtime.

Codex's `codex.mcp.json` and the generic `mcp.json` use `cwd: "."` (resolved by
Codex against the installed plugin root) and `CADGEN_MCP_APP_DIR: "gui"`.
The inherited Claude/Cursor/Gemini launch settings are kept; they are not claimed
to load this custom GUI until their host-specific paths have been configured and
tested. The standalone browser viewer is also unchanged.

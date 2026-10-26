# Changes

## Visual experiment revision 1

Based on text-to-cad 0.7.24. Adds the Visual Inspector preflight skill, standardized CAD Visual Spec, source provenance, labeled fallback, CAD skill routing, tests and documentation. Keeps cadgen 0.7.24. Changes plugin identity to text-to-cad-visual and MCP service to cad_visual.

The original installed plugin is maintained separately for comparison. This repository is a source snapshot, not the upstream Git history.

## Publication preparation

Correct inherited Claude marketplace identity; add environment diagnostics, distribution checks and Windows/Linux CI. Preserve original byte hashes across Git checkouts. Document Python/CLI prerequisites and distinguish local validation from remote installation. No CAD construction or visual inspection behavior changes.

## Local GUI attribution update

Adds a dedicated GUI resource based on the pinned 0.7.24 page. Preserves the original author and appends Ming Liu in the UI, unifies author.name as Ming Liu, and sets Codex developerName to earthtojake, Ming Liu. GitHub and feedback point to Muilrz/image2_text-to-cad. Codex loads the page from this plugin's gui directory; shared runtime files and the original plugin stay untouched.

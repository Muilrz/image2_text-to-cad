# Attribution and modifications

This project is an experimental derivative of **earthtojake/text-to-cad**, based on the locally installed 0.7.24 plugin distribution.

- Upstream repository: https://github.com/earthtojake/text-to-cad
- Upstream copyright: **Copyright (c) 2026 Thompson Labs LLC**
- Upstream license: MIT; the original license text is preserved unchanged in `LICENSE`.
- Upstream plugin metadata credited earthtojake. The inherited skill provenance and historical upstream README are retained.

Local additions and modifications, attributed to **Ming Liu**:

- An `image-cad-preflight` skill with a geometric inspection prompt, strict response schema and Python helper.
- A CAD skill entry route that keeps the request, reference images and visual spec in the same main session.
- P0/P1/UNKNOWN observations, evidence, confidence, provenance and a labeled fallback mode.
- Independent plugin and MCP identities for comparison with the original plugin.
- Tests, comparison guidance and publication documentation.
- A dedicated CAD MCP GUI snapshot, preserving upstream and embedded license notices, with joint display attribution and this fork's GitHub/feedback links.

These local additions are made available under the same MIT terms in `LICENSE`. This project attribution is not a replacement for the upstream copyright notice. A maintainer may add a copyright notice identifying the actual holder of their new contributions without deleting the upstream notice.

This is not an official upstream release. Upstream support, privacy and terms URLs are not presented as policies or support commitments for this derivative. The dedicated GUI page is bundled with its license notices; other runtime dependencies are not bundled and retain their own licenses.

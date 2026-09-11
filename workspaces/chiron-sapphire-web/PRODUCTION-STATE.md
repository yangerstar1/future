# Chiron Sapphire — production state

Contract: CHIRON_SAPPHIRE_WEB_PRODUCTION_CONTRACT_V1(1).md, SHA256 d84a8f87d8aa60a8d381416fbf152017e7d7ab7fce5d4497d98bc74dede521d9.

User authorized future repository, a new branch, existing Actions and sandbox work on 2026-09-11. No new fees or website deployment authorized.

G0: repository main read at 96f6321e6cef2ef37b97c85b460025079f006c12. Only README.md exists on this baseline; no AGENTS.md, dependencies, entrypoints or existing product implementation. Existing README and other branches must remain unchanged.

New isolated branch: codex/chiron-sapphire-web. New isolated workspace: workspaces/chiron-sapphire-web. Allowed root change: .github/workflows/chiron-production.yml only.

Local runtime: Node 22.16.0, Python 3.13.5, Chromium 144.0.7559.96. Headless WebGL2 failed. A real headed Chromium launched under xvfb-run now obtains WebGL2 using ANGLE SwiftShader. This is software rendering, not physical GPU or mobile hardware evidence. Sandbox network cannot download dependencies; Actions supplies pinned npm dependencies. No original or paid watch asset acquired. Production geometry will be locally authored using Three.js geometry utilities, not a copied editorial model.

Current: G0 bootstrap / source baseline in progress. G1–G6 not passed. No website, model or product-quality claim in this commit. Assurance: SEQUENTIAL_SELF_REVIEW + actual tool checks; no independent agent called.

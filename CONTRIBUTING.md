# Contributing

This is the **template** for the NFT Collector Copilot agent on Pinata. The OpenSea skill it depends on lives in [`ProjectOpenSea/opensea-skill`](https://github.com/ProjectOpenSea/opensea-skill) and is published to ClawHub as `opensea-marketplace`. Skill changes do **not** belong here — open them against that repo. Template changes (workspace docs, manifest, README) belong here.

## Repo layout

See `README.md` → *Repository layout*. The short version: `manifest.json` defines the agent, `.openclaw/` configures the harness, `workspace/` holds everything the agent reads at runtime.

## Making changes

1. Branch from `main`: `git checkout -b your-change`.
2. Edit. Most edits are to `workspace/*.md` or `manifest.json`.
3. Run validation locally before pushing — same checks CI runs:
   ```bash
   jq . manifest.json > /dev/null
   jq . .openclaw/openclaw.json > /dev/null
   ```
4. Open a PR. CI runs the same shape checks plus presence checks for required workspace files.

## Versioning

`manifest.json` has one version field — `version` (top-level integer) — which is the manifest **schema** version (currently `1`). Don't touch it unless the schema itself changes.

The template doesn't carry its own version field; track template revisions through git tags instead:

```bash
git tag v1.0.1 && git push --tags
```

Use semver for tags:
- patch: doc tweaks, prompt fixes
- minor: new heartbeat steps, new memory schemas, new TOOLS.md fields
- major: breaking changes to memory layout, manifest shape, or env requirements

## Style

Match the existing voice: terse, numerate, defers to the skill rather than duplicating it. The agent reads these files every session — every line costs context. Cut anything that isn't load-bearing.

## Don't commit

- Secrets, `.env*`, real API keys, real wallet IDs.
- `workspace/memory/*` — runtime state, gitignored.
- `.claude/` — local Claude Code settings.

## Questions

Open an issue or ping the OpenSea team.

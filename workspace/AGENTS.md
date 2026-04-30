# AGENTS.md — NFT Collector Copilot Workspace

## Workspace Layout

```
workspace/
  SOUL.md           # Who you are + guardrails + rubric + pre-buy gate
  AGENTS.md         # This file — workspace conventions + memory schemas
  IDENTITY.md       # Your name, vibe, wallet info (filled on first run)
  TOOLS.md          # Watchlist, whale wallets, chains, budgets, drops — user-tunable
  BOOTSTRAP.md      # First-run setup (delete after completion)
  HEARTBEAT.md      # What you do on each idle cycle
  USER.md           # About your human (filled on first run)
  MEMORY.md         # Long-running free-text observations (create when useful)
  memory/           # Structured memory files (create on first write)
skills/opensea/     # Attached from ClawHub at deploy time (opensea/opensea-marketplace)
```

## Memory Schemas

Create these on first use; don't pre-seed them. Never write secrets into any memory file.

### `memory/floors.json` — snapshot, overwritten each heartbeat

```json
{
  "observed_at": "2026-04-17T14:00:00Z",
  "by_slug": {
    "boredapeyachtclub": { "chain": "ethereum", "floor_eth": 12.3, "volume_24h_eth": 450, "best_listing_eth": 12.4 }
  }
}
```

Write atomically: `memory/floors.json.tmp` → `mv` in place.

### `memory/actions.jsonl` — append-only log, rotated at 1000 lines

One JSON object per line. Anything with a side-effect (alert sent, buy proposed, buy executed, policy rejection, offer accepted, approval set, transfer).

```json
{"ts":"2026-04-17T14:03:12Z","action":"buy","slug":"azuki","chain":"ethereum","token_id":"1234","listing_eth":2.1,"total_eth":2.21,"result":"executed","tx_hash":"0x…"}
```

Rotate per HEARTBEAT.md step 8.

### `memory/taste.json` — structured taste model, per HEARTBEAT.md step 9

Source of truth for what the user likes. The agent re-reads it before every recommendation and cites it when making judgment calls.

### `memory/holdings.json` — cached NFTs owned per chain

Avoids re-running `nfts list-by-account` on every heartbeat. Invalidate a chain's entry when `actions.jsonl` shows a transfer in or out, or at most every 12 hours.

### `memory/whale_cursor.json` — last seen event timestamp per whale

So `events by-account` only streams the tail since last heartbeat.

### `memory/scan_state.json` — once-per-day scan timestamps

Tracks the last run of HEARTBEAT.md steps 5 (drops) and 6 (trending), which run at most every ~20 hours.

```json
{
  "last_drop_scan": "2026-04-17T02:00:00Z",
  "last_trending_scan": "2026-04-17T02:00:00Z"
}
```

### `MEMORY.md` (in `workspace/`, not `memory/`)

Free-text long-form observations that don't fit a schema: API quirks, volatile slugs, seller wallets that pattern wash-trade, drops that disappointed, specific things the user said about their taste that you want to remember word-for-word.

## File Ownership

- **You (the agent)** write to: `memory/*`, `workspace/MEMORY.md`, `workspace/IDENTITY.md`, `workspace/USER.md`, and once — to delete `workspace/BOOTSTRAP.md` after first-run.
- **User** writes to: `workspace/TOOLS.md`. When they edit it, re-read at the start of the next turn.
- **Never write** to: `skills/opensea/` (read-only, attached from ClawHub), `manifest.json`, `.openclaw/*`, `README.md`.

## Workflow

1. **Build** runs automatically after each `git push` — installs `@opensea/cli` globally (see `manifest.json` → `scripts.build`). The OpenSea skill is attached separately by Pinata from ClawHub.
2. **Start** is a no-op — the agent operates via conversation and heartbeat, not a web server.

## Safety

- Never push directly to `main` — use feature branches + PRs for any *template* code changes.
- Don't run destructive commands without confirmation.
- Enforce SOUL.md → *Hierarchy of Ceilings* and *Pre-Buy Gate* on every value action.
- Never ask for a raw private key. If the user offers one, refuse and point them at `skills/opensea/references/wallet-setup.md`.
- Never commit secrets to any file in this workspace.

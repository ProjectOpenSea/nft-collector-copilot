# HEARTBEAT.md

Your heartbeat is where you earn your keep. Every cycle, do the minimum work to answer: *did anything move that the user would care about, and is there anything worth acting on?* Then learn from what you saw.

## Long Task Check-in

If you're mid-task (actively executing a multi-step operation that isn't complete yet), check in with the user instead of running the routine below:

> "Still going — [one sentence on what you're doing]. Keep going or should I stop?"

Wait for their response. Halt on "stop" and summarize. Otherwise resume.

Only run the routine below when idle.

## Rate-Limit Discipline

Every call on this heartbeat shares one `OPENSEA_API_KEY`. Never fan out in parallel. Run requests sequentially; on a 429, wait 60s and retry with jitter. If you hit two 429s in a row this cycle, skip remaining optional steps and report.

## Routine

Run these in order. Stop early if the user is active.

### 1. Floor scan — required (watchlist only)

For each slug in `TOOLS.md` → `watchlist`:

- `opensea --format toon collections stats <slug>` — one call per slug.
- Write the new `{chain, floor_eth, volume_24h, observed_at}` into a new `memory/floors.json` atomically: write to `memory/floors.json.tmp`, then `mv` in place (prevents half-written snapshots if the heartbeat is interrupted).
- Compare against the prior `memory/floors.json`. If the floor moved by more than this slug's `alertFloorDropPct` (or the default `alerts.floorMovePct`), queue an alert.

### 2. Best-listing probe — conditional

Only run `opensea --format toon listings best <slug> --limit 3` for slugs that have `snipeThresholdEth > 0` OR whose floor alert fired in step 1. Do not probe passive slugs — one extra call per slug adds up.

For each listing within `snipeThresholdEth`:
- If the slug has `autoBuy: true` AND all five conditions in SOUL.md → *Hierarchy of Ceilings* → *Autobuy* pass, enter the Pre-Buy Gate and execute. Log the outcome in `memory/actions.jsonl`.
- Otherwise, queue an alert with the listing details. Do not execute.

### 3. Sell-side scan — required when the wallet owns NFTs

- `opensea --format toon nfts list-by-account <chain> <wallet>` per funded chain. Cache the result in `memory/holdings.json` and only re-fetch on chain where balance moved (check `actions.jsonl` for recent transfers).
- For each owned NFT whose slug is in the watchlist, run `opensea offers best-for-nft <slug> <token_id>`. If the offer crosses `minFlipMarginPct` above the acquisition cost (from `memory/actions.jsonl`) or crosses `flipTargetPct` above current floor, queue an alert. **Never auto-accept an offer** — sells always need per-turn confirmation (SOUL.md → *Sell-Side & Approvals*).

### 4. Whale-cross — if `whaleWallets` is configured

For each address in `TOOLS.md` → `whaleWallets`:

- `opensea --format toon events by-account <address> --limit 20`.
- Filter the tail since last heartbeat (track `memory/whale_cursor.json` per address).
- Events of interest: `sale` (whale bought), `item_received` (new NFT), `listing` (whale listing for sale).
- If the whale touched a collection in the watchlist, queue a high-priority alert. If they touched a collection *not* in the watchlist, queue a soft alert — this is the signal for the user to consider adding it.

### 5. Drop radar — once per day, not every heartbeat

Check `memory/scan_state.json` → `last_drop_scan`. If > 20 hours since last scan:

- `opensea --format toon drops list --type upcoming --limit 10`
- `opensea --format toon drops list --type featured --limit 10`
- Cross-reference against `memory/taste.json` — if a drop matches a theme the user has bought or bookmarked, queue an alert with the drop page, stage info, and mint mechanic. Update `memory/scan_state.json` → `last_drop_scan`.

### 6. Trending scan — once per day

Check `memory/scan_state.json` → `last_trending_scan`. If > 20 hours since last scan:

- `opensea --format toon collections trending --timeframe one_day --chains ethereum,base --limit 10`
- For each trending slug not already watched, cross-reference against `taste.json`. Propose adding up to three with a one-line rationale; the user decides. Update `memory/scan_state.json` → `last_trending_scan`.

### 7. Alert dispatch

Flush the queued alerts. If the Pinata environment provides an outbound channel (Telegram, etc.), send there. Otherwise, hold for the next user message and lead with them.

Alert format (one line per event, tight):

> `boredapeyachtclub floor -8% → 11.2 ETH (24h vol 18) · listings ↑`

### 8. Log rotation

`memory/actions.jsonl` is append-only. At the end of each heartbeat:

- Count lines. If ≥ 1000, rotate: move current file to `memory/actions.<YYYY-MM-DD>.jsonl` and start fresh.
- Keep at most the 5 most recent archives; delete older ones.

### 9. Learnings — update `taste.json`

`memory/taste.json` is a structured model of what the user likes. Schema:

```json
{
  "updated_at": "2026-04-17T14:05:00Z",
  "by_slug": {
    "pudgypenguins": {
      "asked_about": 7,
      "bought": 2,
      "passed": 3,
      "avg_entry_eth": 11.8,
      "themes": ["pfp", "blue-chip"],
      "notes": "targets entries below 7d median floor"
    }
  },
  "themes_preferred": ["pfp", "art-blocks", "gaming"],
  "themes_rejected": []
}
```

Update rules each heartbeat:
- Increment `asked_about` when the user asked about a slug since last heartbeat.
- Increment `bought` / `passed` based on `actions.jsonl` entries.
- Recompute `avg_entry_eth` from buy actions.
- If the user rejected a recommendation with a reason, fold that into `notes`.
- Promote persistent themes into `themes_preferred`. Persistent rejections → `themes_rejected`.

Also update `MEMORY.md` (free-text) with anything worth remembering that doesn't fit the taste schema — volatile slugs, API quirks, seller wallets to avoid.

## When You're Idle Too Long

If nothing in the watchlist moved significantly and no alerts fired for three consecutive heartbeats, it's OK to stay quiet. Do not invent urgency. Collectors tune out agents that cry wolf.

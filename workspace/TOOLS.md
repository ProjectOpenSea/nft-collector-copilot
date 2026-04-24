# TOOLS.md — Collector Configuration

_User-tunable. Edit this file to change what the agent watches, who it follows, and how it spends._

## Stack

- **OpenSea CLI:** `@opensea/cli` — installed globally at build time. Use `opensea --help` for the command tree.
- **OpenSea skill:** `skills/opensea/` — attached from ClawHub (`opensea/opensea-marketplace`) at deploy time.
- **Wallet:** Privy server wallet, env-configured (`PRIVY_APP_ID`, `PRIVY_APP_SECRET`, `PRIVY_WALLET_ID`).

## Watchlist

Collections to track on every heartbeat. Ceilings here are advisory — the Privy policy is the real enforcement. See `SOUL.md` → *Hierarchy of Ceilings*.

```yaml
watchlist:
  - slug: boredapeyachtclub
    chain: ethereum
    maxBuyEth: 0.5           # per-slug ceiling; agent never proposes a buy above this without explicit confirm
    autoBuy: false            # if true, snipes below snipeThresholdEth bypass per-turn confirm (other gates still apply)
    alertFloorDropPct: 10     # alert when floor moves this much (% points)
    snipeThresholdEth: 0.0    # 0 disables snipes for this slug
    minFlipMarginPct: 15      # alert when best offer ≥ cost basis * (1 + this)
    flipTargetPct: 0          # alert when best offer ≥ floor * (1 + this); 0 disables
  - slug: pudgypenguins
    chain: ethereum
    maxBuyEth: 0.5
    autoBuy: false
    alertFloorDropPct: 10
    snipeThresholdEth: 0.0
    minFlipMarginPct: 15
    flipTargetPct: 0
  # Add more:
  # - slug: your-favorite-collection
  #   chain: base
  #   maxBuyEth: 0.1
  #   autoBuy: false
  #   alertFloorDropPct: 15
  #   snipeThresholdEth: 0.02
  #   minFlipMarginPct: 20
  #   flipTargetPct: 50
```

## Whale Wallets

Addresses whose activity to follow. The agent runs `events by-account` for each on every heartbeat and alerts when they interact with watchlist collections (high priority) or with any collection at all (soft signal). Keep this list tight — every address adds one API call per heartbeat.

```yaml
whaleWallets:
  # - address: 0x...          # paste addresses or ENS names
  #   label: vitalik.eth
  #   tier: high               # high | medium | soft — filters alert volume
```

## Chains

Mainnets only. Testnets are intentionally excluded. `matic` is the canonical CLI identifier for Polygon (per `skills/opensea/SKILL.md` → *Supported chains*).

```yaml
chains:
  - ethereum
  - base
  - arbitrum
  - optimism
  - matic    # Polygon
```

## Budget

```yaml
budget:
  dailyCapEth: 0.1            # agent stops initiating any value action after this much spent today
  confirmAboveEth: 0.02       # any value action ≥ this needs per-turn "yes" (bypassed only by snipe envelope)
  gasBufferEth: 0.005         # reserve this much ETH per chain for gas; pre-buy gate refuses below
```

## Alerts

```yaml
alerts:
  floorMovePct: 10            # default floor alert threshold if a slug doesn't override
  digestHourUtc: 14           # optional daily digest time (agent can be asked for one anytime)
  maxAlertsPerHeartbeat: 5    # hard cap so a volatile hour doesn't produce a wall of noise
```

## Drop Radar

```yaml
drops:
  enabled: true
  chains: [ethereum, base]    # only propose drops on these chains
  themes: []                  # optional filter — e.g. ["pfp", "art-blocks"]; empty = anything matching user taste
```

## Notes

_Add environment-specific details here as you discover them — chains you've funded, explorer preferences, wallet quirks, rate-limit observations, collections the user has opinions about._

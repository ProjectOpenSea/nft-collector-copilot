# NFT Collector Copilot

An AI agent for NFT collectors. Watches [OpenSea](https://opensea.io), scores every listing across five signals (price, volume, depth, holders, momentum), and executes Seaport trades through a [Privy](https://privy.io) server wallet with a TEE-enforced spend cap. You approve; it acts.

## The killer feature: **Whale-Cross Alerts**

Point it at a list of wallets you respect (vitalik.eth, your favorite PFP whale, whoever) and your watchlist. When a tracked whale buys, mints, or lists into any collection — whether it's on your watchlist or not — you get a one-line alert within a heartbeat, with a one-click follow gated by your Privy spend cap. Few others ship this — it takes the OpenSea events feed, a TEE-enforced wallet, and a disciplined scoring rubric in the same box.

## What it does

- **Watchlist floor + volume tracking** with per-slug alert thresholds and sell-side flip triggers.
- **Conviction Score** before any recommendation — price vs 7d median, 7d/30d volume ratio, listing depth, holder concentration, momentum.
- **Pre-Buy Gate** — wash-trade check, thin-market refusal, gas economics, full-cost (with fees) disclosure, balance & buffer check, policy-fit check.
- **Seaport buys + sells** via `@opensea/cli` + the skill's fulfillment scripts, signed by your Privy wallet.
- **Drop Radar** — upcoming/featured drops cross-referenced against your taste model.
- **Taste learning** — every buy/pass/ask updates a structured `taste.json` so recommendations get sharper over time.
- **Spend-cap safety.** The Privy policy is the real enforcement — the agent literally cannot overspend.

Supported chains: see `workspace/TOOLS.md`. Mainnets only by default.

## What's bundled

- [`@opensea/cli`](https://github.com/ProjectOpenSea/opensea-cli) — installed globally at build time.
- [`opensea-marketplace`](https://clawhub.ai/opensea-marketplace) — attached via `manifest.json` → `skills` and mounted at `skills/opensea/`. SKILL.md + reference docs + shell scripts for Seaport, swaps, stream events, wallet setup, and policy templates. Pinata pulls the latest published version at deploy time.

## Secrets you'll need

Paste these into Pinata's environment UI at deploy time:

| Variable | Required | How to get it |
|---|---|---|
| `OPENSEA_API_KEY` | yes | `curl -s -X POST https://api.opensea.io/api/v2/auth/keys \| jq -r .api_key` — no signup |
| `PRIVY_APP_ID` | yes | [dashboard.privy.io](https://dashboard.privy.io) → create app |
| `PRIVY_APP_SECRET` | yes | Same page as App ID |
| `PRIVY_WALLET_ID` | yes | Create a server wallet — see `skills/opensea/references/wallet-setup.md` → *Privy* |

Full walkthrough: `skills/opensea/references/wallet-setup.md`. Policy templates: `skills/opensea/references/wallet-policies.md`.

## 60-second setup

1. **Grab an OpenSea API key** — run the curl above.
2. **Create a Privy app** at [dashboard.privy.io](https://dashboard.privy.io); copy App ID + App Secret.
3. **Create a server wallet** following `skills/opensea/references/wallet-setup.md` → *Privy* → step 2. Save `id` as `PRIVY_WALLET_ID`.
4. **Attach a spend policy** — the agent will walk you through this on first run using the "Agent Trading — Conservative" template from `skills/opensea/references/wallet-policies.md`. Start tight.
5. **Fund the wallet** on whichever chains you plan to trade on.
6. **Deploy** — paste all four env vars into Pinata, then chat.

## Example prompts

> "Add boredapeyachtclub, pudgypenguins, and azuki to my watchlist on ethereum. Alert me on any floor drop over 5%."

> "Follow vitalik.eth and 0xpunks4156 as whales — high-priority alerts."

> "Should I buy this azuki at 2.1 ETH? Run the full gate."

> "Any upcoming drops this week that fit my taste?"

> "What's the best offer on my bored ape #1234? Is it worth flipping?"

> "Swap 0.05 ETH into USDC on Base."

> "Walk me through tightening the wallet policy to cap buys at 0.1 ETH."

## Safety model

- **Env-only credentials.** No private keys in the repo or agent workspace.
- **Privy policy is the hard ceiling.** The spend cap, destination allowlist, and chain filter are enforced inside a TEE before signing.
- **Per-turn confirmation for material actions.** Any buy, offer acceptance, approval, or transfer above `confirmAboveEth` (in `workspace/TOOLS.md`) needs explicit "yes" in the current turn. Snipes can bypass this only when the listing is fully inside your configured envelope — see `workspace/SOUL.md` → *Hierarchy of Ceilings*.
- **Sell-side always confirms.** Privy's native-value cap is denominated in the chain's native token (ETH, etc.) — it does **not** apply to WETH transfers, which is how Seaport offer acceptances pay out. Sells, offer acceptances, and ERC721/1155 approvals therefore always require per-turn confirmation, regardless of price.
- **Pre-Buy Gate.** Wash trades, thin markets, uneconomic gas, and fee surprises all block a buy before it's proposed.
- **Policy rejections surface verbatim.** No workarounds.

## Repository layout

```
.
├── manifest.json              # Pinata agent manifest — attaches opensea-marketplace from ClawHub
├── LICENSE                    # MIT
├── .openclaw/
│   ├── openclaw.json          # OpenClaw harness config (compaction, concurrency)
│   └── SOUL.md                # short canonical persona — points at workspace/SOUL.md
└── workspace/
    ├── SOUL.md                # guardrails + Conviction Score + Pre-Buy Gate
    ├── AGENTS.md              # workspace conventions + memory schemas
    ├── IDENTITY.md            # blank — filled on first run
    ├── TOOLS.md               # watchlist, whales, budgets — user-tunable
    ├── BOOTSTRAP.md           # first-run walkthrough — agent deletes after completion
    ├── HEARTBEAT.md           # idle-cycle routine
    ├── USER.md                # collector profile — filled on first run
    └── memory/                # created at runtime — floors, actions, taste, scan state
```

At deploy time Pinata attaches the OpenSea skill under `skills/opensea/` (SKILL.md + `references/*.md` + `scripts/*.sh`) — not checked into this repo.

## Updating the skill

Skill versions are managed on ClawHub, not in this template. To pick up a new version, no repo change is needed — Pinata pulls the latest published version of `opensea-marketplace` on each deploy. To pin to a specific version, replace `clawhub_slug` in `manifest.json` with a `cid` for that version.

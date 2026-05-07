# BOOTSTRAP.md — Hello, Collector

_You just woke up. Before you can act as a copilot, you need to provision secrets, harden the wallet, fund a float, and learn the user._

This file is a **resumable state machine**. Pinata `restart` ends the conversation — you come back fresh with no memory of the previous session. So every cold start, follow the same flow:

1. Read what's in env (which of `OPENSEA_API_KEY`, `PRIVY_APP_ID`, `PRIVY_APP_SECRET`, `PRIVY_WALLET_ID`, `PRIVY_AUTH_SIGNING_KEY` are set).
2. Read `IDENTITY.md` to recover what's already been done (`hardening_status`, wallet address, additional_signer pubkey, etc.).
3. Jump to the first incomplete phase below. Do not redo completed work.
4. Never advance past a phase whose preconditions aren't met — even if the user asks.

There is no memory yet on a totally fresh deploy. That's normal: `memory/` and most of `IDENTITY.md` get filled in across the phases below.

## Helper: locate the Pinata Platform CLI

Phase 0 uses the bundled Pinata Platform skill to attach secrets and restart. Find it once at the top of any session that needs it:

```bash
PINATA_CLI=$(find skills -path '*pinata*platform*/cli.mjs' 2>/dev/null | head -1)
```

If `PINATA_CLI` is empty, the skill didn't mount. Tell the user, point at `manifest.json` → `skills`, and stop.

## Phase 0 — Provision all secrets in one restart

**Skip if:** all of `OPENSEA_API_KEY`, `PRIVY_APP_ID`, `PRIVY_APP_SECRET`, `PRIVY_WALLET_ID`, `PRIVY_AUTH_SIGNING_KEY` are set.

This phase batches every secret-attach into a single Pinata restart. Each `restart` ends the conversation and forces a cold resume, so the goal here is to make the user paste their Privy credentials exactly once, do all the auto-provisioning in the same shell session using inline env, then attach everything and restart together.

Walk through 0a–0d in order. Each sub-step has its own skip check so partial state from a previous attempt resumes cleanly.

### 0a — OPENSEA_API_KEY

**Skip if:** `OPENSEA_API_KEY` is set.

Otherwise auto-fetch a free-tier instant key:

```bash
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://api.opensea.io/api/v2/auth/keys)
STATUS=$(printf '%s' "$RESPONSE" | tail -1)
BODY=$(printf '%s' "$RESPONSE" | sed '$d')

if [ "$STATUS" = "429" ]; then
  echo "OpenSea instant-key endpoint is rate-limited (3 keys/hr/IP). Either wait an hour and let me retry, or paste your own OPENSEA_API_KEY into Pinata's env UI and restart."
  exit 1
fi

OPENSEA_API_KEY=$(printf '%s' "$BODY" | jq -r .api_key)
[ -n "$OPENSEA_API_KEY" ] && [ "$OPENSEA_API_KEY" != "null" ] || { echo "instant key fetch failed (status $STATUS): $BODY"; exit 1; }
```

Hold the value in the shell var. Don't `--attach` yet — that happens at the end of the phase in 0d.

### 0b — PRIVY_APP_ID + PRIVY_APP_SECRET

**Skip if:** both `PRIVY_APP_ID` and `PRIVY_APP_SECRET` are set.

Otherwise, ask the user once:

> "I need a Privy application before I can create your wallet. Create one at https://dashboard.privy.io (free tier is fine), then paste your **App ID** and **App Secret** here. I'll create the wallet, generate my own signer, and attach all the secrets in a single batch — only one restart at the end of this phase."

When the user pastes them, capture into shell vars (`PRIVY_APP_ID=...`, `PRIVY_APP_SECRET=...`). Do not echo `PRIVY_APP_SECRET` back to chat or to logs.

If the user prefers to add them via Pinata's env UI directly, ask them to do that and restart from the UI. After restart, this sub-step will see them in env and skip.

### 0c — Wallet ID + additional_signer keypair

**Skip if:** both `PRIVY_WALLET_ID` and `PRIVY_AUTH_SIGNING_KEY` are set.

**Precondition:** `PRIVY_APP_ID` and `PRIVY_APP_SECRET` are present, either in env or in shell vars from 0b.

Generate the agent's additional_signer keypair (pure-local, no API call):

```bash
KEYPAIR=$(opensea wallet generate-auth-key --format json)
PRIVY_AUTH_SIGNING_KEY=$(printf '%s' "$KEYPAIR" | jq -r .privateKey)
ADDITIONAL_SIGNER_PUBKEY=$(printf '%s' "$KEYPAIR" | jq -r .publicKey)
```

Do **not** echo `PRIVY_AUTH_SIGNING_KEY` to chat or logs.

Create the wallet without an owner (it will be hardened in Phase 1). Pass the Privy creds **inline** as subprocess env so this works in the same shell session that just collected them — no restart needed before the call:

```bash
WALLET_JSON=$(PRIVY_APP_ID="$PRIVY_APP_ID" PRIVY_APP_SECRET="$PRIVY_APP_SECRET" \
  opensea wallet create --chain-type ethereum --format json)
PRIVY_WALLET_ID=$(printf '%s' "$WALLET_JSON" | jq -r .id)
WALLET_ADDRESS=$(printf '%s' "$WALLET_JSON" | jq -r .address)
```

The CLI will print a loud `WARNING: created without --owner-public-key` to stderr — that's expected; we register the owner and attach the spend policy together in the off-machine ceremony in Phase 1. The brief unhardened window between wallet creation and that ceremony is acceptable because the wallet has zero balance and no policy attached during this window — there is nothing to lose if the credentials in env were misused. Phase 1 refuses to advance until owner gating AND policy are both confirmed.

If `opensea wallet create` fails with an auth error, the Privy credentials the user pasted are wrong. Tell the user, ask them to recheck the dashboard, and re-collect 0b. **Don't proceed to 0d** with bad creds — you'd attach them, restart, and discover the failure cold next session.

Record in `IDENTITY.md` under `## Wallet`:

- `Address: <WALLET_ADDRESS>`
- `Wallet ID: <PRIVY_WALLET_ID>`
- `Additional-signer pubkey (SPKI base64): <ADDITIONAL_SIGNER_PUBKEY>` — Phase 1 needs to re-show this to the user across restarts.
- `hardening_status: pending_owner_registration`

### 0d — Attach everything and restart once

Attach each secret you provisioned in 0a–0c (skip the line for any secret that was already in env coming into this phase — those are already persisted):

```bash
node "$PINATA_CLI" create-secret OPENSEA_API_KEY        "$OPENSEA_API_KEY"        --attach
node "$PINATA_CLI" create-secret PRIVY_APP_ID           "$PRIVY_APP_ID"           --attach
node "$PINATA_CLI" create-secret PRIVY_APP_SECRET       "$PRIVY_APP_SECRET"       --attach
node "$PINATA_CLI" create-secret PRIVY_WALLET_ID        "$PRIVY_WALLET_ID"        --attach
node "$PINATA_CLI" create-secret PRIVY_AUTH_SIGNING_KEY "$PRIVY_AUTH_SIGNING_KEY" --attach
```

Tell the user what just happened, then restart:

> "All set: OpenSea key fetched, Privy app credentials saved, wallet `<WALLET_ADDRESS>` created, and my additional_signer keypair generated (private half stored as `PRIVY_AUTH_SIGNING_KEY`). Restarting now — I'll come back as a fresh session and walk you through the one-time off-machine ceremony to register your owner key and attach a spend policy."

```bash
node "$PINATA_CLI" restart
```

Stop. The conversation ends here; you'll resume cold from Phase 1.

## Phase 1 — One-time off-machine ceremony (owner + signer + policy)

**Skip if:** `IDENTITY.md` says `hardening_status: confirmed` AND `opensea wallet info` shows `policyIds.length > 0`.

**Precondition:** `PRIVY_WALLET_ID` + `PRIVY_AUTH_SIGNING_KEY` set.

This phase bundles the three off-machine actions that all require the user's owner private key into one focused session, so the user only has to bring out their owner key once.

Check current posture:

```bash
opensea wallet info --format json
```

The three properties to verify:

- `ownerEnforcesAuthKey: true` — owner key registered
- `additionalSignerCount >= 1` — agent's signer registered
- `policyIds.length > 0` — spend policy attached

If all three pass, the ceremony is complete. Update `IDENTITY.md`:

- `hardening_status: confirmed`
- `auth_key_gating: yes`
- Policy template: *Agent Trading — Conservative*
- Per-tx cap: `<cap from earlier conversation, if known — otherwise note "see policy"`>

Then advance to Phase 2.

Otherwise (most likely on first arrival here), walk the user through the combined ceremony. First, settle the per-tx cap conversationally so they can plug it into the policy template before going off-machine:

1. Ask them their per-tx cap in ETH (no example — they choose). Convert to wei: `0.05 ETH = 50000000000000000 wei`.
2. Show them the *Agent Trading — Conservative* template from `skills/opensea/references/wallet-policies.md`, with their cap substituted into the `value lte` rule. Use the chain allowlist and Seaport destination from the same reference, verbatim.

Then tell them:

> "Wallet is at `<address>` (id `<wallet_id>`). Before I can sign anything, three things need to happen on YOUR machine — never here. Get them all out of the way in one session with your owner key:
>
> 1. **Generate your owner keypair locally.** Easiest path: install the OpenSea CLI locally (`npm install -g @opensea/cli`) and run `opensea wallet generate-auth-key`. Or use any P-256 keygen (e.g. `openssl ecparam -name prime256v1 -genkey -noout -out owner.pem` and convert to SPKI base64). Keep the private key on your machine — never paste it to me, never put it in env, never check it into anything.
>
> 2. **Register two keys on the wallet:** your owner public key as `owner_id`, AND my additional_signer public key (`<additional_signer_pubkey from IDENTITY.md>`) as a signer.
>
> 3. **Attach the spend policy** I just showed you (with your `<cap>` ETH cap), so the per-tx ceiling is enforced in Privy's TEE.
>
> Steps 2 and 3 are both done with the Node script in https://github.com/ProjectOpenSea/opensea-skill/blob/main/docs/policy-administration.md, signed by your owner key (off-machine). Do them in order: register first, attach policy second — once owner gating is on, the policy attach also requires the owner signature.
>
> After this one-time ceremony, the day-to-day is asymmetric: I sign every trade with my additional_signer key (lives in env, scoped to `/rpc` only). Your owner key only comes out when you decide to change the policy itself — raise the cap, edit the chain allowlist, etc. You don't need to be online with the owner key for me to trade.
>
> Once all three are done, type 'done' and I'll verify."

When the user says done, re-run `opensea wallet info`. Verify each property and surface specifically which (if any) failed:

- `ownerEnforcesAuthKey: false` → owner registration didn't take. Re-do step 2.
- `additionalSignerCount < 1` → signer registration didn't take. Re-do step 2.
- `policyIds.length == 0` → policy attach didn't take. Re-do step 3.

Don't advance with partial state. Once all three pass, record the IDENTITY.md fields above and advance to Phase 2.

**Refuse to advance to Phase 2 (funding) until all three pass.** Without owner gating, the credentials in env can rewrite the policy that's supposed to constrain spending. Without a policy, there is no per-tx ceiling. Funding before either is in place creates a window where env credentials could drain the wallet. If the user pushes back, explain the order and offer to keep waiting.

## Phase 2 — Hot-wallet funding

**Skip if:** `IDENTITY.md` already has a `float_per_chain` entry.

Walk the user through the hot/cold wallet model — reference `skills/opensea/references/wallet-funding.md` for the canonical version:

1. Ask which chain(s) they intend to trade on (subset of `TOOLS.md` → `chains`).
2. Ask their intended float per chain. The float is the **real** aggregate ceiling — Privy can't enforce daily limits, so wallet balance has to. ≈ one day or one week of intended budget is normal.
3. Tell them to fund the agent wallet from their own cold/funding wallet. Replenishment is on them, on whatever cadence they pick.
4. Optionally ask for the funding wallet's address — useful so you can recognize replenishment events in `events by-account` streams.

Record in `IDENTITY.md` under `## Wallet`:

- `float_per_chain:` (mirror to `TOOLS.md` → new `floatEth` field too)
- `funding_wallet:` (if provided)

For each funded chain, do a quick balance check (use the native-balance path from `skills/opensea/references/wallet-setup.md` or `eth_getBalance` via a public RPC). If a target chain shows 0, note it — you can still track floors there, you just can't buy.

## Phase 3 — Conversation, identity, watchlist

Don't interrogate. Just talk. Start with something like:

> "Hey. I just came online. The wallet's set up — hardened, policy attached, funded. I'm your NFT collector copilot — I watch OpenSea, read the market, and can buy listings through the Privy wallet (the per-tx cap is in a TEE; the float you set is the real ceiling). Let's get to know each other."

Then figure out together:

1. **Your name** — what should they call you?
2. **Your vibe** — warm? Dry? Chatty? Terse?
3. **Your emoji** — signature character for messages.

Then calibrate the watchlist:

1. Which collections they want to watch (3–5 is a good starting point).
2. Per slug: which chain, rough price range, whether they want snipe alerts.
3. Any whales they want to follow (wallets, ENS names). Optional — skip if they're not sure.
4. Any drop themes they care about (pfp, art-blocks, gaming, etc.).

Update `TOOLS.md` → `watchlist`, `whaleWallets`, `drops.themes` with their answers. Keep every slug's `autoBuy: false` at first — autobuy is opt-in only, per slug, after the user has seen you work for a while.

Update:

- `IDENTITY.md` — your name, vibe, emoji (the wallet section is already filled).
- `USER.md` — their name, timezone, collector profile, risk tolerance, per-tx comfort.
- `MEMORY.md` (create it in `workspace/`) — seed with any taste signals from the opening conversation.

## Phase 4 — Cleanup

Delete this file. You don't need a bootstrap script anymore — you're you now.

After this point, never invoke the Pinata Platform skill again. It's for setup only; the agent does not modify its own secrets in normal operation. See `SOUL.md` → *Forbidden operations*.

---

_Watch the floors. Protect the ETH. Learn the user._

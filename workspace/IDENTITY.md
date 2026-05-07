# IDENTITY.md

- **Name:**
- **Creature:**
- **Vibe:**
- **Personality:**
- **Emoji:**

## Wallet

- **Provider:** Privy
- **Address:**
- **Wallet ID:**
- **Chains funded:**
- **Policy template:**
- **Spending limit (per tx):** _(ETH / wei — record both for clarity, e.g. "0.05 ETH / 50000000000000000 wei")_
- **hardening_status:** _(pending_creation | pending_owner_registration | pending_policy | confirmed — used by BOOTSTRAP for resumability across restarts)_
- **additional_signer_pubkey:** _(SPKI base64; the public half of `PRIVY_AUTH_SIGNING_KEY`. Persisted so BOOTSTRAP Phase 1 can re-show it to the user across cold restarts.)_
- **auth_key_gating:** _(yes | no — captured from `opensea wallet info` after Phase 1 verifies `ownerEnforcesAuthKey: true`)_
- **float_per_chain:** _(mirrored from `TOOLS.md` → `floatPerChain`; the real aggregate ceiling)_
- **funding_wallet:** _(optional — user's cold/funding wallet address, so the agent can recognize replenishment events in `events by-account` streams)_

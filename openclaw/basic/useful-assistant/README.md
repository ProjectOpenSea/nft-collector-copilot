# Useful Assistant Template

## What this is

A vanilla starting point for building agents on Pinata Agents. It provides a documented manifest with every available option explained, a workspace structure with personality, memory, and safety conventions, and a bootstrap flow so the agent figures out who it is on first run.

This is a **base template** — it is intentionally generic. Clone it and customize it to build your agent: a frontend dev, a data pipeline monitor, a personal assistant, a Discord bot, whatever you want.

## What's included

- `manifest.json` — Agent config with all available options documented in a `_docs` block (remove before submitting to the marketplace)
- `workspace/BOOTSTRAP.md` — First-run conversation guide (self-deletes after setup)
- `workspace/SOUL.md` — Agent personality and principles
- `workspace/AGENTS.md` — Workspace conventions, memory system, safety rules
- `workspace/IDENTITY.md` — Agent name, vibe, emoji (filled in during bootstrap)
- `workspace/USER.md` — Notes about the human (learned over time)
- `workspace/TOOLS.md` — Environment-specific notes
- `workspace/HEARTBEAT.md` — Periodic tasks (empty by default)
- `workspace/projects/hello-test/` — Vite + React + TS starter project (served at `/app`)

## How it works

1. Deploy the template on Pinata and open the chat
2. The agent runs through the bootstrap flow to establish its identity
3. Customize the workspace files to give your agent a personality, tools, and purpose
4. If your agent runs a server or app, the Vite starter is pre-wired and served at `/app`

## Post-deploy setup

Open the chat — the agent walks you through the bootstrap to set its name, personality, and purpose.

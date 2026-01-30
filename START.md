# Start Here

## For Claude Code / AI Assistants

Copy this into Claude Code to begin:

```
Read `SYSTEM_FLOW.md` first to understand the system architecture.

Then check:
1. `inputs/active_client.md` - Is there an active client?
2. `.cursor/modules/MRDs/` - Are there MRDs to process?

Based on what exists, determine the phase and execute accordingly.
```

---

## Quick Reference

| I want to... | Command/Action |
|--------------|----------------|
| Start a new client from MRD | Read MRD → `/onboard-client` |
| Check current client status | Read `inputs/active_client.md` |
| Run discovery on a client | `/discovery {clientId}` |
| Create content | `/ghostwrite {clientId}` |
| See the full workflow | Read `SYSTEM_FLOW.md` |

---

## Key Files

| File | Purpose |
|------|---------|
| `SYSTEM_FLOW.md` | Complete system architecture and phases |
| `CLAUDE.md` | AI conventions and rules |
| `config/ontology.yaml` | Data relationships |
| `inputs/active_client.md` | Current active client |
| `prompts/skill-development-from-mrd.md` | Skill orchestration guide |

---

## The Standard Flow

```
MRD → Onboard → Discover → Configure → Collect → Curate → Create → Deliver
                                                                      ↓
                                                                   Notion
```

All client data lives in **Firebase** (`clients/{clientId}/`), not locally.

## Checks

Run tests, ruff and migration checks inside the web container: `docker compose exec -T web <cmd>` (the host has no `uv`). The commands are the ones in `.github/workflows/`.

## Agent skills

### Issue tracker

Issues live in GitHub Issues on borgarc/shelters (via the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Uses the five default labels: needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

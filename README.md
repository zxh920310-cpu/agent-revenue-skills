# Agent Revenue Skills

Repo-ready Codex plugin skills for safer AI-agent work around open-source contributions and bounty PRs.

## Skills

- `agent-skill-safety-auditor`: read-only audit for agent skills, Codex plugins, MCP configs, hooks, and bundled scripts.
- `github-bounty-scout`: conservative GitHub bounty and open-source task scanner that rejects unsafe, unclear, or duplicated work.
- `pr-acceptance-packager`: maintainer-friendly PR packaging workflow for bounty and open-source changes.

## Request help on GitHub

Use the repository issue templates to request one of two GitHub-native workflows:

- Skill/plugin safety audit: read-only review of a public agent skill, Codex plugin, MCP config, hook, or bundled script.
- Bounty triage: conservative review of a public GitHub issue or bounty candidate before spending implementation time.

Do not include secrets, API keys, cookies, customer data, payment details, wallet addresses, identity documents, or private business files in issues. This repository is a public lead-capture and workflow demo surface only; payment, sponsorship, identity, tax, and external marketplace setup are intentionally not configured here.

## Safety posture

- No payment, wallet, bank, tax, identity, or external marketplace setup.
- No secrets, API keys, cookies, certificates, or customer/company data.
- No automatic issue claiming or PR submission.
- Scanner scripts are read-only and use explicit target paths or public GitHub issue search.

## Local validation

```bash
python -m py_compile skills/agent-skill-safety-auditor/scripts/audit_skill_package.py
python -m py_compile skills/github-bounty-scout/scripts/bounty_scout.py
python <path-to-skill-creator>/scripts/quick_validate.py skills/agent-skill-safety-auditor
python <path-to-skill-creator>/scripts/quick_validate.py skills/github-bounty-scout
python <path-to-skill-creator>/scripts/quick_validate.py skills/pr-acceptance-packager
python <path-to-plugin-creator>/scripts/validate_plugin.py .
```

## Example

```bash
python skills/agent-skill-safety-auditor/scripts/audit_skill_package.py skills/agent-skill-safety-auditor
python skills/github-bounty-scout/scripts/bounty_scout.py --since 2026-07-04T00:00:00Z --limit 5 --max-candidates 6 --check-prs
```

## Status

MVP. Validate manually before trusting any scanner output. Regex findings are leads, not proof.

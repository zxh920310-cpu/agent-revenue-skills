---
name: agent-skill-safety-auditor
description: Audit AI agent skills, Codex plugins, MCP configs, hooks, and bundled scripts for unsafe behavior before installation, publication, or reuse. Use when reviewing SKILL.md packages, .codex-plugin/plugin.json manifests, .mcp.json files, hooks, scripts, or third-party agent workflow bundles for prompt injection, data exfiltration, privilege escalation, destructive commands, broad permissions, vague triggers, or supply-chain risk.
---

# Agent Skill Safety Auditor

## Workflow

Audit read-only by default. Do not install, execute, authenticate, publish, or modify the target package unless the user explicitly asks after seeing the report.

1. Confirm the target path or repository/file set.
2. Inspect package structure:
   - `SKILL.md`
   - `.codex-plugin/plugin.json`
   - `.mcp.json`
   - hooks and command files
   - `scripts/`, `references/`, and `assets/`
3. Run the bundled scanner when a local path is available:

```bash
python scripts/audit_skill_package.py <target-path>
```

4. Review the scanner output manually. Treat regex findings as leads, not final proof.
5. Produce a concise report with:
   - overall verdict: pass, caution, fail
   - severity table
   - evidence with file paths and lines
   - concrete remediation steps
   - remaining unknowns

## Risk Taxonomy

Read `references/risk-taxonomy.md` when you need the full risk checklist. Core categories:

- Data exfiltration: reads secrets, tokens, browser data, SSH keys, home directories, or env vars and sends them out.
- Privilege escalation: broad shell tools, hooks, destructive commands, hidden installs, or commands outside the requested workspace.
- Prompt injection: instructions that override user/system policy, hide behavior, suppress warnings, or request trust without evidence.
- Supply-chain risk: remote code execution, unpinned installers, dependency confusion, abandoned repo signals, or mismatch between docs and scripts.
- Overbroad automation: skills that can change external state without clear approval, including payments, email sends, PR merges, deploys, or account actions.

## Report Shape

Use this format:

```markdown
# Agent Skill Safety Audit

Verdict: pass | caution | fail
Target: <path or repo>

## Findings

| Severity | File | Evidence | Risk | Fix |
| --- | --- | --- | --- | --- |

## Notes

- What was reviewed.
- What was not reviewed.
- Whether any scripts were executed. Default should be no.
```

## Boundaries

- Do not read secrets, cookies, certificates, API keys, browser profiles, or customer/company data.
- Do not authorize external services.
- Do not run target package scripts during the audit unless the user separately approves.
- Do not claim a package is safe; say what was checked and what remains unknown.
- Stop and ask before any publication, payment, identity, tax, wallet, or external marketplace action.

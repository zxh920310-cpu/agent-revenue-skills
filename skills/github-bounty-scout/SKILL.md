---
name: github-bounty-scout
description: Find, score, and reject GitHub bounty or high-probability open-source PR tasks for AI agents. Use when the user wants small GitHub bounties, bounty candidates, Claude Code/Codex/AI-agent issues, good-first-issue contribution opportunities, duplicate-PR checks, or a safe combination plan for earning through open-source PRs without external signup, payment setup, API keys, wallet, tax, identity, or customer data.
---

# GitHub Bounty Scout

## Workflow

Scout before coding. The goal is to avoid wasting agent budget on unclear, crowded, unsafe, or already-solved issues.

1. Read any existing run logs first:
   - `CODEX_BOUNTY_LOG.md`
   - `CODEX_BOUNTY_TASKS.md`
   - `CODEX_BUDGET_GUARD.md`
2. Run the bundled scanner with narrow limits:

```bash
python scripts/bounty_scout.py --since 2026-07-04T00:00:00Z --limit 10 --max-candidates 12 --check-prs
```

3. Review the output manually. Treat `consider` as "inspect next", not "start coding".
4. Open the issue and verify:
   - reward amount is explicit;
   - scope is small;
   - no matching PR already exists;
   - maintainer activity is recent;
   - no external signup, payment, wallet, tax, identity, OAuth, API key, or security-challenge requirement.
5. Pick at most one task unless the user explicitly asks for a portfolio plan.
6. If no task passes, write "no actionable candidate" and stop.

## Scoring Rules

Read `references/selection-rules.md` for the complete checklist.

Prioritize:

- $20-$50 USD tasks.
- Documentation, tests, examples, install/setup fixes, small labels/aliases, small bug fixes.
- Issues with clear acceptance criteria and low comment volume.
- Repositories with recent maintainer activity.

Reject:

- No explicit amount.
- Over-$100 unclear tasks.
- Creator-only or assigned-only tasks.
- Existing matching PRs.
- Payment, wallet, bank, tax, identity, KYC, PayPal, Venmo, Stripe, or external marketplace setup.
- API keys, OAuth, customer/company data, CRM/ERP/Excel business data.
- Security challenges, pentests, CVEs, exploit work, or broad refactors.

## Output Shape

Return a concise table:

```markdown
| Score | Repo | Issue | Amount | Decision | Reason | Risk |
| ---: | --- | --- | --- | --- | --- | --- |
```

Then give one recommendation:

- `execute`: one clear low-risk task is worth doing now.
- `watch`: candidate is plausible but needs later maintainer signal.
- `skip`: no candidate is worth agent budget.

## Boundaries

- Do not claim, reserve, or promise completion.
- Do not register on external bounty platforms.
- Do not enter payment or identity information.
- Do not open a PR until the issue is independently verified and not duplicated.
- Stop when budget guard says no new PR attempts this week.

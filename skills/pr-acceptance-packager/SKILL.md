---
name: pr-acceptance-packager
description: Package completed GitHub bounty, open-source, or AI-agent coding changes into maintainer-friendly pull requests. Use when preparing PR titles, PR descriptions, testing summaries, bounty notes, review checklists, known limitations, issue linkage, or final pre-submit checks that improve merge probability without exaggerating scope or adding payment, identity, wallet, tax, customer data, or unrelated changes.
---

# PR Acceptance Packager

## Workflow

Use this skill after the code or documentation change is implemented and before opening or updating a pull request.

1. Inspect the issue and contribution rules.
2. Inspect the diff.
3. Verify the change is scoped to the issue.
4. Confirm tests, lint, build, or manual checks are honestly reported.
5. Prepare the PR title and body.
6. Add a concise known-limitations section.
7. If bounty-related, include a bounty note without payment details.
8. Do not submit if the diff includes secrets, customer/company data, unrelated formatting, or broad refactors.

## PR Title

Prefer conventional, specific titles:

- `fix: handle empty action log state`
- `docs: add local setup steps`
- `test: cover parser edge cases`
- `feat: add review velocity section`

Avoid:

- vague titles like `update`, `fix bug`, or `changes`;
- exaggerated claims like `complete all bounty requirements` unless verified;
- promises about future maintenance.

## PR Body

Use this shape:

```markdown
Related Issue
Closes #123

What changed
- ...

Why
- ...

How tested
- ...

Screenshots / logs
- ...

Known limitations
- ...

Bounty note
This PR addresses the GitHub issue only. No payment, wallet, tax, identity, or external-platform details are included.
```

## Pre-submit Checklist

Read `references/pr-checklist.md` when preparing a real PR.

Minimum checks:

- Issue link is correct.
- Diff has no unrelated files.
- Tests are named exactly, or "not run" is explained honestly.
- PR body does not include secrets or payment details.
- Maintainer can review the change without guessing intent.
- Bounty note is factual and does not request or expose payment info.

## Boundaries

- Do not claim guaranteed bounty acceptance.
- Do not ask maintainers to reserve a task.
- Do not pressure maintainers for payment.
- Do not add wallet, bank, PayPal, Venmo, Stripe, tax, identity, or email-verification information.
- Stop before submitting a controversial, broad, or compatibility-risk PR.

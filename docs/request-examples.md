# Request Examples

This repository accepts public, GitHub-native requests only. Use these examples to keep requests small enough to triage and safe enough to discuss in public.

## Skill/plugin safety audit

Good request:

```text
Please review this public Codex skill for unsafe behavior:

Repository: https://github.com/example/public-skills
Path: skills/bounty-helper
Concern: It includes scripts and MCP references. I want to know whether it reads secrets, uploads files, or performs write actions without confirmation.
```

Expected output:

- Pass/fail safety summary.
- Risk table covering file reads, network calls, write actions, secret access, subprocess use, and auto-run behavior.
- Concrete file and line references when available.
- Suggested fixes that avoid broad rewrites.

Do not include:

- API keys, tokens, cookies, certificates, or private config files.
- Company or customer data.
- Local-only paths that cannot be inspected from a public repo.

## Bounty triage

Good request:

```text
Please triage this GitHub issue before I spend implementation time:

Issue: https://github.com/example/project/issues/123
Goal: decide whether this is a suitable small bounty or contribution target.
Constraints: no payment setup, no wallet, no KYC, no paid APIs, no more than 2 hours.
```

Expected output:

- Recommendation: pursue, watch, or skip.
- Reward clarity and payout-path risks.
- Scope estimate and likely files touched.
- Competition check, including matching open PRs when visible.
- Maintainer activity and acceptance criteria.
- Stop conditions before implementation begins.

Do not include:

- Wallet, bank, tax, identity, or payment details.
- External platform credentials.
- Private bounty platform screenshots or non-public requirements.

## PR acceptance packaging

Good request:

```text
Please package this public PR for maintainer review:

PR: https://github.com/example/project/pull/456
Related issue: https://github.com/example/project/issues/123
Testing done: npm test, npm run lint
Known limitation: docs only, no runtime behavior change.
```

Expected output:

- Maintainer-friendly PR description.
- Related issue wording.
- What changed, why, and how tested.
- Known limitations without overpromising.
- Bounty note that does not include payment or identity details.

Do not include:

- A promise that the PR will be merged.
- Payment instructions or payout identifiers.
- Claims that were not tested.

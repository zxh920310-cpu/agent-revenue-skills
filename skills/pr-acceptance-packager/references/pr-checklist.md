# PR Packaging Checklist

## Issue alignment

- Related issue exists and is open or recently relevant.
- PR scope matches the issue.
- No unrelated refactor, formatting churn, or opportunistic cleanup.
- Acceptance criteria are addressed or explicitly limited.

## Diff hygiene

- Only expected files changed.
- No generated clutter unless required.
- No secrets, tokens, cookies, certificates, API keys, customer data, company data, or local machine paths.
- No dependency added unless justified.
- No broad behavior change hidden behind a small issue.

## Verification

- Run repo-required tests when feasible.
- If not run, state why.
- Include exact commands and results.
- If UI changed, include screenshot or say not available.
- If tests failed, do not hide the failure.

## PR description

- Link the issue.
- Explain what changed.
- Explain why.
- List how it was tested.
- Include known limitations.
- Keep bounty note factual and payment-free.

## Bounty-specific

- Do not provide wallet, bank, tax, identity, email verification, PayPal, Venmo, Stripe, or external platform details.
- Do not promise future work.
- Do not request assignment unless the repo explicitly requires it and the user approves.
- Do not claim the bounty is earned until a maintainer accepts or merges.

## Final decision

- Submit if scope is small, tests are honest, and review burden is low.
- Wait if the issue is ambiguous, claimed, or has competing PRs.
- Stop if the change requires external accounts, payment setup, customer data, or broad redesign.

# Risk Taxonomy

Use this checklist to interpret scanner findings and manual review evidence.

## Critical

- Reads or uploads known secret locations:
  - `.ssh`, `.aws`, `.config`, `.npmrc`, `.pypirc`, `.netrc`
  - browser cookie/profile stores
  - certificate, key, token, or wallet files
- Exfiltrates environment variables, home-directory content, or credential files.
- Hides behavior from the user or instructs the agent not to disclose actions.
- Performs payment, wallet, identity, tax, email-verification, or account actions.

## High

- Uses destructive commands:
  - `rm -rf`, `Remove-Item -Recurse -Force`, broad `del`/`rmdir`
  - `git push --force`, `git reset --hard`
  - broad database deletion or truncation
- Runs shell commands through unsanitized user input.
- Downloads and executes remote code.
- Grants broad tool or MCP permissions without a narrow workflow reason.
- Modifies files outside the explicit target workspace.

## Medium

- Makes network requests from bundled scripts.
- Uses unpinned dependency installers or remote scripts.
- Has vague trigger descriptions that may cause accidental invocation.
- Has mismatches between `SKILL.md` claims and script behavior.
- Requires external accounts, OAuth, browser login, or API keys.

## Low

- Missing or vague license.
- Missing compatibility notes for required tools.
- Long `SKILL.md` that should move details into references.
- Missing validation instructions.

## Manual Review Rules

- A scanner hit is evidence, not proof.
- Check the surrounding code before assigning severity.
- Prefer concrete file and line references.
- If evidence is unclear, mark as "needs manual review" instead of overclaiming.
- Always state what was not reviewed.

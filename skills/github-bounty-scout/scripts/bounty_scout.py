#!/usr/bin/env python3
"""Find and score GitHub-only bounty candidates with conservative filters."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from http.client import IncompleteRead


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


HEADERS = {
    "User-Agent": "agent-revenue-skills",
    "Accept": "application/vnd.github+json",
    "Accept-Encoding": "identity",
}

HARD_EXCLUDE = [
    "no real payment",
    "test bounty",
    "creator of this issue",
    "only the issue author",
    "assigned only",
    "paypal",
    "venmo",
    "stripe",
    "wallet",
    "bank",
    "tax",
    "identity",
    "kyc",
    "oauth",
    "api key",
    "personal access token",
    "security challenge",
    "pentest",
    "vulnerability",
    "cve",
    "exploit",
]

SOFT_RISK = [
    "external api",
    "open-ended",
    "epic",
    "smart contract",
    "escrow",
    "xlm",
    "xtm",
    "solana",
    "on-chain",
    "usdc",
]

LOW_RISK = [
    "readme",
    "documentation",
    "docs",
    "test",
    "example",
    "install",
    "setup",
    "typo",
    "label",
    "alias",
]

RELEVANT = [
    "agent",
    "claude",
    "codex",
    "mcp",
    "ai",
    "bounty",
    "github",
]


@dataclass
class Candidate:
    score: int
    repo: str
    number: int
    title: str
    url: str
    amount: str
    comments: int
    decision: str
    reasons: list[str]
    risks: list[str]
    matching_prs: list[str]


def load_json(url: str, timeout: int = 18):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        try:
            raw = response.read()
        except IncompleteRead as error:
            raw = error.partial
    return json.loads(raw.decode("utf-8", "replace"))


def search_issues(query: str, per_page: int) -> list[dict]:
    url = (
        "https://api.github.com/search/issues?q="
        + urllib.parse.quote(query)
        + f"&sort=updated&order=desc&per_page={per_page}"
    )
    data = load_json(url)
    return data.get("items", [])


def parse_issue_url(url: str) -> tuple[str, int] | None:
    match = re.search(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", url)
    if not match:
        return None
    return match.group(1), int(match.group(2))


def extract_amount(text: str) -> tuple[str, list[int], list[str]]:
    usd = [int(match.group(1)) for match in re.finditer(r"\$(\d{1,5})(?:\b|[^\d])", text)]
    other = []
    for token in ("USDC", "XLM", "XTM"):
        if re.search(rf"\d{{1,6}}\s*{token}\b", text, re.IGNORECASE):
            other.append(token)
    if usd:
        return ", ".join(f"${amount}" for amount in usd), usd, other
    if other:
        return ", ".join(other), [], other
    return "", [], []


def terms(text: str, options: list[str]) -> list[str]:
    lowered = text.lower()
    return [option for option in options if option in lowered]


def slug(title: str) -> str:
    value = title.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:60]


def matching_prs(repo: str, issue_number: int, title: str) -> list[str]:
    queries = [
        f"repo:{repo} is:pr {issue_number}",
        f'repo:{repo} is:pr "{slug(title)}"',
    ]
    seen: dict[str, str] = {}
    for query in queries:
        try:
            for item in search_issues(query, 5):
                seen[item["html_url"]] = item.get("title", "")
        except Exception:
            continue
        time.sleep(0.8)
    return sorted(seen)


def score_issue(issue: dict, check_prs: bool) -> Candidate:
    repo, number = parse_issue_url(issue["html_url"]) or ("", 0)
    title = issue.get("title") or ""
    body = issue.get("body") or ""
    text = f"{title}\n{body}"
    amount_label, usd_amounts, other_amounts = extract_amount(text)
    hard = terms(text, HARD_EXCLUDE)
    soft = terms(text, SOFT_RISK)
    low = terms(text, LOW_RISK)
    relevant = terms(text, RELEVANT)
    comments = issue.get("comments") or 0

    score = 0
    reasons: list[str] = []
    risks: list[str] = []

    if any(20 <= amount <= 50 for amount in usd_amounts):
        score += 30
        reasons.append("target USD amount")
    elif any(amount == 100 for amount in usd_amounts):
        score += 10
        risks.append("$100 task; verify clarity and competition")
    elif any(amount > 100 for amount in usd_amounts):
        score -= 30
        risks.append("over $100")
    elif not usd_amounts:
        score -= 12
        risks.append("no explicit USD amount")

    if other_amounts:
        score -= 12
        risks.append("non-USD or crypto-denominated payout")

    if comments == 0:
        score += 8
        reasons.append("0 comments")
    elif comments <= 2:
        score += 4
        reasons.append("low comments")
    else:
        score -= 8
        risks.append("comment competition")

    if low:
        score += 10
        reasons.append("small-scope terms: " + ", ".join(low[:3]))
    if relevant:
        score += 4
        reasons.append("agent-related terms: " + ", ".join(relevant[:3]))
    if soft:
        score -= 10
        risks.append("soft risk: " + ", ".join(soft[:3]))
    if hard:
        score -= 100
        risks.append("hard exclude: " + ", ".join(hard[:3]))

    prs: list[str] = []
    if check_prs and repo and number:
        prs = matching_prs(repo, number, title)
        if prs:
            score -= 80
            risks.append("matching PR exists")

    decision = "consider" if score >= 25 and not hard and not prs else "skip"
    return Candidate(
        score=score,
        repo=repo,
        number=number,
        title=title,
        url=issue["html_url"],
        amount=amount_label,
        comments=comments,
        decision=decision,
        reasons=reasons,
        risks=risks,
        matching_prs=prs,
    )


def build_queries(since: str) -> list[str]:
    return [
        f'is:issue is:open "bounty" "$50" comments:<3 updated:>{since}',
        f'is:issue is:open "bounty" "$20" comments:<3 updated:>{since}',
        f'is:issue is:open "agent" "bounty" comments:<3 updated:>{since}',
        f'is:issue is:open "Claude Code" comments:<3 updated:>{since}',
        f'is:issue is:open "MCP" "good first issue" comments:<3 updated:>{since}',
    ]


def collect(since: str, max_candidates: int) -> list[dict]:
    seen: set[str] = set()
    issues: list[dict] = []
    for query in build_queries(since):
        try:
            results = search_issues(query, min(10, max_candidates))
        except Exception as error:
            issues.append({"error": f"{query}: {error}"})
            continue
        for item in results:
            if item["html_url"] in seen:
                continue
            seen.add(item["html_url"])
            issues.append(item)
            if len(issues) >= max_candidates:
                return issues
        time.sleep(1.0)
    return issues


def print_markdown(candidates: list[Candidate], errors: list[str], limit: int) -> None:
    print("| Score | Repo | Issue | Amount | Comments | Decision | Reason | Risk |")
    print("| ---: | --- | --- | --- | ---: | --- | --- | --- |")
    for candidate in candidates[:limit]:
        issue = f"[#{candidate.number}]({candidate.url}) {candidate.title[:90]}"
        print(
            "| {score} | `{repo}` | {issue} | {amount} | {comments} | {decision} | {reason} | {risk} |".format(
                score=candidate.score,
                repo=candidate.repo,
                issue=issue,
                amount=candidate.amount,
                comments=candidate.comments,
                decision=candidate.decision,
                reason="; ".join(candidate.reasons[:3]),
                risk="; ".join(candidate.risks[:4]),
            )
        )
    for error in errors:
        print(f"| n/a | scanner | error |  |  | skip |  | {error} |")


def main() -> int:
    parser = argparse.ArgumentParser(description="Find and score GitHub bounty candidates.")
    parser.add_argument("--since", required=True, help="GitHub updated:> timestamp, e.g. 2026-07-04T00:00:00Z")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--max-candidates", type=int, default=12)
    parser.add_argument("--check-prs", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    raw = collect(args.since, args.max_candidates)
    errors = [item["error"] for item in raw if "error" in item]
    candidates = [
        score_issue(item, args.check_prs)
        for item in raw
        if "error" not in item and parse_issue_url(item.get("html_url", ""))
    ]
    candidates.sort(key=lambda item: item.score, reverse=True)

    if args.json:
        print(
            json.dumps(
                {
                    "candidates": [asdict(candidate) for candidate in candidates[: args.limit]],
                    "errors": errors,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print_markdown(candidates, errors, args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

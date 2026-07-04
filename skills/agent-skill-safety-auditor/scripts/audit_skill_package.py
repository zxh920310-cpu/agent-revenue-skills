#!/usr/bin/env python3
"""Read-only scanner for AI agent skill/plugin packages."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".next",
    "dist",
    "build",
}

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".sh",
    ".bash",
    ".ps1",
    ".bat",
    ".cmd",
}


@dataclass
class Finding:
    severity: str
    file: str
    line: int
    rule: str
    evidence: str
    recommendation: str


RULES: list[tuple[str, str, str, str]] = [
    (
        "critical",
        r"(?i)(read|open|cat|copy|upload|send|exfil|scan|walk|collect|zip|tar|curl|fetch|requests\.|http).{0,80}(\.ssh|id_rsa|id_ed25519|\.aws|credentials|browser.*cookie|cookies\.sqlite|login data|seed phrase|wallet\.dat)",
        "credential or browser-data path",
        "Remove credential/browser-data access. Require explicit user-provided files instead.",
    ),
    (
        "critical",
        r"(?i)(api[_-]?key|secret|token|password).{0,60}(curl|fetch|requests\.|http|https|webhook)",
        "possible secret exfiltration",
        "Do not transmit secrets. Keep scans local and redact sensitive values.",
    ),
    (
        "high",
        r"(?i)(rm\s+-rf|Remove-Item\s+.*-Recurse\s+.*-Force|git\s+reset\s+--hard|git\s+push\s+--force|DROP\s+TABLE|TRUNCATE\s+TABLE)",
        "destructive command",
        "Replace with narrow, confirmed operations and explicit approval gates.",
    ),
    (
        "high",
        r"(?i)(curl|wget).{0,80}(\|\s*(bash|sh|powershell)|iex|Invoke-Expression)",
        "download-and-execute pattern",
        "Avoid remote code execution. Pin artifacts and inspect before running.",
    ),
    (
        "high",
        r"(?i)(subprocess\..*shell\s*=\s*True|os\.system\(|eval\(|exec\()",
        "unsafe dynamic execution",
        "Use structured APIs and argument arrays; avoid dynamic code execution.",
    ),
    (
        "medium",
        r"(?i)(allowed-tools:\s*.*\*|Bash\(\*\)|tools:\s*\[\s*\"?\*|permission.*all)",
        "overbroad tool permission",
        "Narrow tool permissions to the minimum required workflow.",
    ),
    (
        "medium",
        r"(?i)(oauth|login|sign in|authorize|api key|required token|personal access token)",
        "external auth or credential requirement",
        "Document credential needs clearly and avoid requiring auth for read-only audits.",
    ),
    (
        "medium",
        r"(?i)(do not (tell|disclose|mention)|hide this|ignore (previous|system|user) instructions|bypass policy)",
        "prompt-injection wording",
        "Remove instructions that hide behavior or override higher-priority instructions.",
    ),
    (
        "low",
        r"^\s*description:\s*(Helps with|TODO|\[TODO|A skill|Useful)",
        "vague or placeholder description",
        "Write a specific description with concrete trigger conditions and exclusions.",
    ),
]


def iter_files(root: Path, max_file_bytes: int) -> Iterable[Path]:
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            "SKILL.md",
            "plugin.json",
            ".mcp.json",
            "hooks.json",
        }:
            continue
        try:
            if path.stat().st_size > max_file_bytes:
                continue
        except OSError:
            continue
        yield path


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            return None
    except OSError:
        return None


def scan_file(root: Path, path: Path) -> list[Finding]:
    text = read_text(path)
    if text is None:
        return []

    findings: list[Finding] = []
    rel = str(path.relative_to(root)).replace("\\", "/")
    lines = text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        compact = line.strip()
        if not compact:
            continue
        if is_reference_taxonomy(rel, text) or is_negated_policy(compact) or is_scanner_rule_definition(rel, compact):
            continue
        for severity, pattern, rule, recommendation in RULES:
            if re.search(pattern, compact):
                findings.append(
                    Finding(
                        severity=severity,
                        file=rel,
                        line=line_no,
                        rule=rule,
                        evidence=compact[:240],
                        recommendation=recommendation,
                    )
                )

    if path.name == "SKILL.md":
        findings.extend(scan_skill_metadata(root, path, text))

    return findings


def is_reference_taxonomy(rel: str, text: str) -> bool:
    return rel == "references/risk-taxonomy.md" and text.startswith("# Risk Taxonomy")


def is_negated_policy(line: str) -> bool:
    lowered = line.lower()
    return any(
        marker in lowered
        for marker in (
            "do not ",
            "don't ",
            "avoid ",
            "remove ",
            "replace with ",
            "stop and ask",
            "must not ",
            "should not ",
        )
    )


def is_scanner_rule_definition(rel: str, line: str) -> bool:
    return rel.endswith("scripts/audit_skill_package.py") and (
        line.startswith("r\"")
        or line.startswith("r'")
        or "RULES" in line
        or line.startswith("\"critical\"")
        or line.startswith("\"high\"")
        or line.startswith("\"medium\"")
        or line.startswith("\"low\"")
    )


def scan_skill_metadata(root: Path, path: Path, text: str) -> list[Finding]:
    rel = str(path.relative_to(root)).replace("\\", "/")
    findings: list[Finding] = []
    if not text.startswith("---"):
        findings.append(
            Finding(
                "medium",
                rel,
                1,
                "missing YAML frontmatter",
                "SKILL.md does not start with YAML frontmatter",
                "Add required name and description frontmatter.",
            )
        )
        return findings

    parts = text.split("---", 2)
    if len(parts) < 3:
        findings.append(
            Finding(
                "medium",
                rel,
                1,
                "unterminated YAML frontmatter",
                "SKILL.md frontmatter was not closed",
                "Close the YAML frontmatter before the body.",
            )
        )
        return findings

    frontmatter = parts[1]
    if not re.search(r"(?m)^name:\s*[a-z0-9][a-z0-9-]{0,62}[a-z0-9]\s*$", frontmatter):
        findings.append(
            Finding(
                "medium",
                rel,
                2,
                "invalid or missing skill name",
                "name must be lowercase kebab-case and match the folder",
                "Set name to the folder name using lowercase letters, digits, and hyphens.",
            )
        )
    if not re.search(r"(?m)^description:\s*.+", frontmatter):
        findings.append(
            Finding(
                "medium",
                rel,
                2,
                "missing description",
                "description frontmatter is required",
                "Add a specific description explaining what the skill does and when to use it.",
            )
        )
    elif len(re.search(r"(?m)^description:\s*(.+)", frontmatter).group(1).strip()) < 40:
        findings.append(
            Finding(
                "low",
                rel,
                2,
                "short description",
                "description is likely too short for reliable skill selection",
                "Include task triggers, file types, and boundaries in the description.",
            )
        )

    return findings


def verdict(findings: list[Finding]) -> str:
    severities = {finding.severity for finding in findings}
    if "critical" in severities or "high" in severities:
        return "fail"
    if "medium" in severities or "low" in severities:
        return "caution"
    return "pass"


def markdown_report(root: Path, findings: list[Finding]) -> str:
    lines = [
        "# Agent Skill Safety Audit",
        "",
        f"Verdict: {verdict(findings)}",
        f"Target: {root}",
        "",
        "## Findings",
        "",
        "| Severity | File | Line | Rule | Evidence | Fix |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    if findings:
        for finding in sorted(findings, key=lambda item: severity_rank(item.severity)):
            lines.append(
                "| {severity} | `{file}` | {line} | {rule} | {evidence} | {fix} |".format(
                    severity=finding.severity,
                    file=escape_md(finding.file),
                    line=finding.line,
                    rule=escape_md(finding.rule),
                    evidence=escape_md(finding.evidence),
                    fix=escape_md(finding.recommendation),
                )
            )
    else:
        lines.append("| info | n/a | 0 | no scanner findings | No risky regex patterns found. | Continue manual review before trust. |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Scanner is read-only and did not execute target package scripts.",
            "- Regex findings are leads for manual review, not final proof.",
            "- Skipped large files, binary-looking files, dependency folders, and VCS folders.",
        ]
    )
    return "\n".join(lines)


def severity_rank(severity: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(severity, 4)


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only audit for agent skill/plugin packages.")
    parser.add_argument("target", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    parser.add_argument("--max-file-bytes", type=int, default=250_000)
    args = parser.parse_args()

    root = Path(args.target).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Target does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Target must be a directory: {root}")

    findings: list[Finding] = []
    for path in iter_files(root, args.max_file_bytes):
        findings.extend(scan_file(root, path))

    if args.json:
        print(
            json.dumps(
                {
                    "target": str(root),
                    "verdict": verdict(findings),
                    "findings": [asdict(finding) for finding in findings],
                },
                indent=2,
            )
        )
    else:
        print(markdown_report(root, findings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

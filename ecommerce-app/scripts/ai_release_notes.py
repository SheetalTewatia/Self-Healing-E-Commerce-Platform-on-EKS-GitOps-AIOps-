#!/usr/bin/env python3
"""
Enhancement 4 — AI Release Notes Generator
Reads git log between the previous and current build,
asks Claude to generate structured release notes,
and appends them to CHANGELOG.md.

Usage:
  python3 scripts/ai_release_notes.py <build_number> [<prev_ref>]
  python3 scripts/ai_release_notes.py 42 HEAD~10
"""

import subprocess
import sys
import os
import anthropic
from datetime import datetime

SEPARATOR = "=" * 65
CHANGELOG = "CHANGELOG.md"


def run(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def get_commit_log(prev_ref: str) -> str:
    return run(["git", "log", f"{prev_ref}..HEAD",
                "--oneline", "--no-merges", "--format=%h %s (%an)"])


def get_diff_stat(prev_ref: str) -> str:
    stat = run(["git", "diff", "--stat", f"{prev_ref}..HEAD"])
    return stat[:3000] if stat else ""


def get_changed_services(prev_ref: str) -> list[str]:
    files = run(["git", "diff", "--name-only", f"{prev_ref}..HEAD"])
    services = set()
    known = ["user-service", "product-service", "order-service",
             "notification-service", "api-gateway", "frontend",
             "ai-service", "aiops-service"]
    for line in files.splitlines():
        for svc in known:
            if line.startswith(svc + "/"):
                services.add(svc)
    return sorted(services)


def generate(build_number: str, prev_ref: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return f"## Release #{build_number} — {datetime.now().strftime('%Y-%m-%d')}\n\n_AI release notes unavailable (no API key)_\n"

    log      = get_commit_log(prev_ref)
    diff     = get_diff_stat(prev_ref)
    services = get_changed_services(prev_ref)

    if not log:
        return f"## Release #{build_number} — {datetime.now().strftime('%Y-%m-%d')}\n\n_No commits found since {prev_ref}_\n"

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Generate professional release notes for a microservices deployment.

Build Number: #{build_number}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
Services with changes: {', '.join(services) or 'unknown'}

Git commits since last release:
{log or 'No commits'}

Files changed (summary):
{diff or 'No diff available'}

Generate release notes in this exact markdown format:

## Release #{build_number} — {datetime.now().strftime('%Y-%m-%d')}

### Services Updated
- (list only the services that had actual code changes)

### Changes
#### New Features
- (bullet list — only if new features exist)

#### Bug Fixes
- (bullet list — only if bug fixes exist)

#### Improvements
- (bullet list — refactors, performance, deps)

### Deployment Notes
> (1-2 sentences for the ops team — anything they need to know)

---

Keep it concise. Infer the type of change from the commit message.
Do not invent changes not evidenced by the commits."""
        }]
    )
    return response.content[0].text


def main():
    build_number = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    prev_ref     = sys.argv[2] if len(sys.argv) > 2 else "HEAD~10"

    notes = generate(build_number, prev_ref)

    print(f"\n{SEPARATOR}")
    print("  AI RELEASE NOTES  (powered by Claude)")
    print(SEPARATOR)
    print(notes)
    print(f"{SEPARATOR}\n")

    # Prepend to CHANGELOG.md (newest at top)
    existing = ""
    if os.path.exists(CHANGELOG):
        with open(CHANGELOG, "r") as f:
            existing = f.read()

    with open(CHANGELOG, "w") as f:
        f.write(notes + "\n\n" + existing)

    print(f"[ai-release-notes] CHANGELOG.md updated (build #{build_number})")


if __name__ == "__main__":
    main()

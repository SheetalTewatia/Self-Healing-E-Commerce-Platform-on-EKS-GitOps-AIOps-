#!/usr/bin/env python3
"""
Enhancement 1 — AI Build Failure Analyser
Reads the Jenkins console log for the current build and asks Claude
to identify the root cause and suggest a specific fix.

Usage:
  python3 scripts/ai_build_analyser.py <log_file_path>
  python3 scripts/ai_build_analyser.py  (reads from stdin)
"""

import sys
import os
import anthropic

SEPARATOR = "=" * 65


def analyse(log: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "ANTHROPIC_API_KEY not set — skipping AI analysis."

    client = anthropic.Anthropic(api_key=api_key)

    # Send last 8000 chars — most relevant error is near the end
    log_tail = log[-8000:] if len(log) > 8000 else log

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""You are a senior DevOps engineer analysing a Jenkins CI build failure.

Build log (last section):
---
{log_tail}
---

Provide a concise analysis in this exact format:

ROOT CAUSE:
(1-2 sentences — what specifically failed and why)

EXACT FIX:
(specific file, line, command, or config change needed)

PREVENTION:
(one sentence — how to avoid this in future pipelines)

SEVERITY: LOW / MEDIUM / HIGH / CRITICAL

Be specific. Reference actual class names, file paths, or error codes from the log."""
        }]
    )
    return response.content[0].text


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.exists(path):
            with open(path, "r", errors="replace") as f:
                log = f.read()
        else:
            print(f"[ai-build-analyser] Log file not found: {path}")
            sys.exit(0)
    else:
        log = sys.stdin.read()

    if not log.strip():
        print("[ai-build-analyser] Empty log — nothing to analyse.")
        sys.exit(0)

    print(f"\n{SEPARATOR}")
    print("  AI BUILD FAILURE ANALYSIS  (powered by Claude)")
    print(SEPARATOR)
    print(analyse(log))
    print(f"{SEPARATOR}\n")


if __name__ == "__main__":
    main()

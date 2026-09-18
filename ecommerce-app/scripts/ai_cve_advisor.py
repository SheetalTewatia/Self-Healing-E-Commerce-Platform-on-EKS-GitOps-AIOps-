#!/usr/bin/env python3
"""
Enhancement 2 — AI CVE Security Advisor
Reads Trivy JSON reports for all 8 services, aggregates CRITICAL/HIGH CVEs,
and asks Claude to produce a prioritised remediation plan.

Usage:
  python3 scripts/ai_cve_advisor.py /tmp/trivy-reports/
"""

import json
import sys
import os
import glob
import anthropic

SEPARATOR = "=" * 65


def load_reports(reports_dir: str) -> list[dict]:
    """Aggregate CVEs from all Trivy JSON reports in the directory."""
    all_vulns = []
    for path in glob.glob(os.path.join(reports_dir, "trivy-*.json")):
        service = os.path.basename(path).replace("trivy-", "").replace(".json", "")
        try:
            with open(path) as f:
                data = json.load(f)
            for result in data.get("Results", []):
                for v in result.get("Vulnerabilities", []) or []:
                    if v.get("Severity") in ("CRITICAL", "HIGH"):
                        all_vulns.append({
                            "service":    service,
                            "cve_id":     v.get("VulnerabilityID", ""),
                            "severity":   v.get("Severity", ""),
                            "package":    v.get("PkgName", ""),
                            "installed":  v.get("InstalledVersion", ""),
                            "fixed_in":   v.get("FixedVersion") or "No fix available",
                            "title":      v.get("Title", ""),
                            "cvss_score": v.get("CVSS", {}).get("nvd", {}).get("V3Score", "N/A"),
                        })
        except Exception as e:
            print(f"[ai-cve-advisor] Could not parse {path}: {e}")

    # Sort: CRITICAL first, then by CVSS score descending
    all_vulns.sort(key=lambda x: (0 if x["severity"] == "CRITICAL" else 1,
                                   -(float(x["cvss_score"]) if str(x["cvss_score"]).replace(".","").isdigit() else 0)))
    return all_vulns


def advise(vulns: list[dict]) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "ANTHROPIC_API_KEY not set — skipping AI CVE advisory."

    if not vulns:
        return "No CRITICAL or HIGH CVEs found across all services. Images are clean."

    client = anthropic.Anthropic(api_key=api_key)

    # Send top 25 to stay within token limit
    sample = vulns[:25]
    critical_count = sum(1 for v in vulns if v["severity"] == "CRITICAL")
    high_count     = sum(1 for v in vulns if v["severity"] == "HIGH")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""You are a container security engineer reviewing Trivy vulnerability scan results
for a production Kubernetes application (8 microservices).

Summary: {critical_count} CRITICAL, {high_count} HIGH CVEs found.

Top vulnerabilities (sorted by severity):
{json.dumps(sample, indent=2)}

Provide a security advisory in this format:

IMMEDIATE ACTION REQUIRED (CRITICAL CVEs):
(List top 3 critical CVEs with: CVE ID, affected service, exact Dockerfile fix)

HIGH PRIORITY (fix in next sprint):
(Top 3 high CVEs with fix recommendation)

BASE IMAGE RECOMMENDATIONS:
(Suggest specific version upgrades for Dockerfiles)

OVERALL RISK ASSESSMENT:
(2-3 sentences on the security posture and urgency)

Be specific with Dockerfile FROM instructions and package upgrade commands."""
        }]
    )
    return response.content[0].text


def main():
    reports_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/trivy-reports"

    if not os.path.isdir(reports_dir):
        print(f"[ai-cve-advisor] Reports directory not found: {reports_dir}")
        sys.exit(0)

    vulns = load_reports(reports_dir)
    print(f"\n{SEPARATOR}")
    print(f"  AI CVE SECURITY ADVISORY  (powered by Claude)")
    print(f"  Total: {sum(1 for v in vulns if v['severity']=='CRITICAL')} CRITICAL, "
          f"{sum(1 for v in vulns if v['severity']=='HIGH')} HIGH")
    print(SEPARATOR)
    print(advise(vulns))
    print(f"{SEPARATOR}\n")


if __name__ == "__main__":
    main()


import json
from pathlib import Path
from datetime import datetime, timezone

REPORT_DIR = Path("reports")
UNIFIED_REPORT_PATH = REPORT_DIR / "unified-report.json"


def load_json(path):
    """Load a JSON report from disk."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_trufflehog():
    """Parse TruffleHog JSONL output."""
    findings = []
    path = REPORT_DIR / "trufflehog.json"

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)

            findings.append({
                "scanner": "TruffleHog",
                "type": "Secret Detection",
                "severity": "HIGH",
                "title": record.get("DetectorName", "Secret detected"),
                "file": record.get("SourceMetadata", {})
                               .get("Data", {})
                               .get("Filesystem", {})
                               .get("file", "Unknown"),
                "line": record.get("SourceMetadata", {})
                              .get("Data", {})
                              .get("Filesystem", {})
                              .get("line", 0),
                "description": "Potential exposed secret detected."
            })

    return findings


def parse_semgrep():
    """Parse Semgrep JSON output."""
    findings = []
    path = REPORT_DIR / "semgrep.json"
    data = load_json(path)

    for result in data.get("results", []):
        extra = result.get("extra", {})

        findings.append({
            "scanner": "Semgrep",
            "type": "Static Analysis",
            "severity": normalize_severity("Semgrep",extra.get("severity", "INFO")),
            "title": result.get("check_id", "Security issue"),
            "file": result.get("path", "Unknown"),
            "line": result.get("start", {}).get("line", 0),
            "description": extra.get("message", "")
        })

    return findings


def parse_osv():
    """Parse OSV-Scanner JSON output."""
    findings = []
    path = REPORT_DIR / "osv-report.json"
    data = load_json(path)

    for result in data.get("results", []):
        for package_data in result.get("packages", []):
            package = package_data.get("package", {})

            for group in package_data.get("groups", []):
                aliases = group.get("aliases", [])
                advisory_ids = group.get("ids", [])

                findings.append({
                    "scanner": "OSV-Scanner",
                    "type": "Dependency Vulnerability",
                    "severity": normalize_severity("OSV-Scanner", group.get("max_severity", 0)),"cvss_score":float(group.get("max_severity", 0)or 0),
                    "title": aliases[0] if aliases else "Unknown advisory",
                    "advisory_ids": advisory_ids,
                    "aliases": aliases,
                    "package": package.get("name", "Unknown"),
                    "version": package.get("version", "Unknown"),
                    "file": result.get("source", {}).get("path", "Unknown"),
                    "line": 0,
                    "description": (
                        f"Vulnerable dependency: "
                        f"{package.get('name')} "
                        f"version {package.get('version')}"
                    )
                })

    return findings


def parse_trivy():
    findings = []

    path = REPORT_DIR / "trivy-report.json"
    data = load_json(path)

    for result in data.get("Results", []):
        for vulnerability in result.get("Vulnerabilities", []):
            findings.append({
                "scanner": "Trivy",
                "type": "Dependency Vulnerability",
                "severity": normalize_severity(
                    "Trivy",
                    vulnerability.get("Severity", "UNKNOWN")
                ),
                "title": vulnerability.get(
                    "VulnerabilityID", "Unknown vulnerability"
                ),
                "package": vulnerability.get("PkgName", "Unknown"),
                "version": vulnerability.get(
                    "InstalledVersion", "Unknown"
                ),
                "file": result.get("Target", "Unknown"),
                "line": 0,
                "description": vulnerability.get(
                    "Description", "Dependency vulnerability detected."
                )
            })

    return findings



def normalize_severity(scanner, severity):
    """Convert scanner-specific severity into a common format."""

    if scanner == "OSV-Scanner":
        score = float(severity)

        if score >= 9.0:
            return "CRITICAL"
        elif score >= 7.0:
            return "HIGH"
        elif score >= 4.0:
            return "MEDIUM"
        elif score > 0:
            return "LOW"
        return "INFO"

    severity = str(severity).upper()

    severity_map = {
        "ERROR": "HIGH",
        "WARNING": "MEDIUM",
        "INFO": "INFO",
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW"
    }

    return severity_map.get(severity, "INFO")


def generate_summary(findings):
    """Generate a severity and scanner summary."""

    severities = [
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
        "INFO"
    ]

    summary = {
        "total_findings": len(findings),
        "severity_counts": {
            severity: 0 for severity in severities
        },
        "scanner_counts": {}
    }

    for finding in findings:
        severity = finding.get("severity", "INFO")
        scanner = finding.get("scanner", "Unknown")

        if severity not in summary["severity_counts"]:
            summary["severity_counts"][severity] = 0

        summary["severity_counts"][severity] += 1

        summary["scanner_counts"][scanner] = (
            summary["scanner_counts"].get(scanner, 0) + 1
        )

    return summary



if __name__ == "__main__":
    all_findings = []

    trufflehog_findings = parse_trufflehog()
    semgrep_findings = parse_semgrep()
    osv_findings = parse_osv()
    trivy_findings = parse_trivy()

    all_findings.extend(trufflehog_findings)
    all_findings.extend(semgrep_findings)
    all_findings.extend(osv_findings)
    all_findings.extend(trivy_findings)

    summary = generate_summary(all_findings)

    print("\n========== SECURITY SCAN SUMMARY ==========")
    print("Total findings:", summary["total_findings"])

    print("\nSeverity distribution:")
    for severity, count in summary["severity_counts"].items():
        print(f"{severity}: {count}")

    print("\nScanner distribution:")
    for scanner, count in summary["scanner_counts"].items():
        print(f"{scanner}: {count}")

    print("============================================")

    unified_report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "findings": all_findings
    }

    UNIFIED_REPORT_PATH.write_text(
        json.dumps(unified_report, indent=4),
        encoding="utf-8"
    )

    print(f"\n[+] Unified report saved: {UNIFIED_REPORT_PATH}")
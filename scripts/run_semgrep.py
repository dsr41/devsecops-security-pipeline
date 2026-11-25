
import json
import subprocess
from pathlib import Path

REPORT_PATH = Path("reports/semgrep.json")

command = [
    "semgrep",
    "scan",
    "--config",
    "scanners/semgrep-rules.yaml",
    "--json",
    "sample-app/",
]

print("[+] Running Semgrep...")

result = subprocess.run(
    command,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

if result.stderr:
    print(result.stderr)

if result.returncode not in (0, 1):
    print("[-] Semgrep execution failed.")
    raise SystemExit(result.returncode)

# Parse Semgrep JSON output
data = json.loads(result.stdout)

# Save formatted JSON as UTF-8
REPORT_PATH.write_text(
    json.dumps(data, indent=4),
    encoding="utf-8"
)

print(f"[+] Findings detected: {len(data['results'])}")
print(f"[+] Report saved: {REPORT_PATH}")

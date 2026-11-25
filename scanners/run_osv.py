
import subprocess
from pathlib import Path

REPORT_PATH = Path("reports/osv-report.json")

command = [
    "osv-scanner",
    "scan",
    "source",
    "--lockfile",
    "requirements.txt",
    "--format",
    "json",
    "--output-file",
    str(REPORT_PATH),
]

print("[+] Running OSV-Scanner...")

result = subprocess.run(
    command,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

if result.stdout:
    print(result.stdout)

if result.stderr:
    print(result.stderr)

if result.returncode not in (0, 1):
    print("[-] OSV-Scanner execution failed.")
    raise SystemExit(result.returncode)

if not REPORT_PATH.exists():
    print("[-] JSON report was not generated.")
    raise SystemExit(1)

print("[+] Dependency scan completed.")
print(f"[+] Scanner exit code: {result.returncode}")
print(f"[+] Report saved: {REPORT_PATH}")

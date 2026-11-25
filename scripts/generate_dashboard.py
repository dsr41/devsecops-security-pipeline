
import json
from pathlib import Path
from html import escape

REPORT_PATH = Path("reports/unified-report.json")
DASHBOARD_PATH = Path("reports/security-dashboard.html")


def load_report():
    with REPORT_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def generate_dashboard(report):
    summary = report["summary"]
    findings = report["findings"]

    severity_counts = summary["severity_counts"]
    scanner_counts = summary["scanner_counts"]

    # Generate severity cards
    severity_cards = ""

    for severity, count in severity_counts.items():
        severity_cards += f"""
        <div class="card">
            <h3>{escape(severity)}</h3>
            <p>{count}</p>
        </div>
        """

    # Generate scanner distribution rows
    scanner_rows = ""

    for scanner, count in scanner_counts.items():
        scanner_rows += f"""
        <tr>
            <td>{escape(scanner)}</td>
            <td>{count}</td>
        </tr>
        """

    # Generate individual security finding rows
    finding_rows = ""

    for finding in findings:
        severity = escape(str(finding.get("severity", "INFO")))
        scanner = escape(str(finding.get("scanner", "Unknown")))
        title = escape(str(finding.get("title", "Unknown")))
        package = escape(str(finding.get("package", "N/A")))
        version = escape(str(finding.get("version", "N/A")))
        file = escape(str(finding.get("file", "Unknown")))
        description = escape(str(finding.get("description", "")))
        file_path = Path(file)
        file = file_path.name

        finding_rows += f"""
        <tr>
            <td>
                <span class="severity {severity.lower()}">
                    {severity}
                </span>
            </td>
            <td>{scanner}</td>
            <td title="{description}">{title}</td>
            <td>{package} {version}</td>
            <td>{file}</td>
        </tr>
        """

    # Build HTML dashboard
    html = f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>DevSecOps Security Dashboard</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #101827;
                color: #f1f5f9;
                margin: 0;
                padding: 30px;
            }}

            h1 {{
                color: #38bdf8;
            }}

            h2 {{
                margin-top: 35px;
            }}

            .cards {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin: 25px 0;
            }}

            .card {{
                background: #1e293b;
                padding: 20px;
                border-radius: 10px;
                min-width: 130px;
            }}

            .card h3 {{
                color: #94a3b8;
                font-size: 14px;
            }}

            .card p {{
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 0;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: #1e293b;
                margin-top: 15px;
            }}

            th, td {{
                padding: 14px;
                text-align: left;
                border-bottom: 1px solid #334155;
            }}

            th {{
                color: #38bdf8;
            }}

            .controls {{
                display: flex;
                gap: 12px;
                margin: 20px 0;
                flex-wrap: wrap;
            }}

            input, select {{
                padding: 12px;
                background: #1e293b;
                color: white;
                border: 1px solid #334155;
                border-radius: 6px;
            }}

            .severity {{
                padding: 5px 9px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }}

            .critical {{
                background: #7f1d1d;
                color: #fecaca;
            }}

            .high {{
                background: #9a3412;
                color: #ffedd5;
            }}

            .medium {{
                background: #854d0e;
                color: #fef9c3;
            }}

            .low {{
                background: #166534;
                color: #dcfce7;
            }}

            .info {{
                background: #1e40af;
                color: #dbeafe;
            }}

            tbody tr:hover {{
                background: #29374d;
            }}

            .table-container {{
                overflow-x: auto;
            }}
        </style>
    </head>

    <body>

        <h1>DevSecOps Security Dashboard</h1>

        <p>Automated security scan results</p>

        <div class="cards">

            <div class="card">
                <h3>Total Findings</h3>
                <p>{summary['total_findings']}</p>
            </div>

            {severity_cards}

        </div>

        <h2>Scanner Distribution</h2>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Scanner</th>
                        <th>Findings</th>
                    </tr>
                </thead>

                <tbody>
                    {scanner_rows}
                </tbody>
            </table>
        </div>

        <h2>Security Findings</h2>

        <div class="controls">

            <input
                type="text"
                id="searchInput"
                placeholder="Search findings..."
                onkeyup="filterFindings()"
            >

            <select
                id="severityFilter"
                onchange="filterFindings()"
            >
                <option value="ALL">All Severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
                <option value="INFO">Info</option>
            </select>

        </div>

        <div class="table-container">
            <table id="findingsTable">

                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Scanner</th>
                        <th>Finding</th>
                        <th>Package / Version</th>
                        <th>File</th>
                    </tr>
                </thead>

                <tbody>
                    {finding_rows}
                </tbody>

            </table>
        </div>

        <script>
            function filterFindings() {{

                const search = document.getElementById("searchInput")
                    .value.toLowerCase();

                const severity = document.getElementById("severityFilter")
                    .value;

                const rows = document.querySelectorAll(
                    "#findingsTable tbody tr"
                );

                rows.forEach(row => {{

                    const text = row.innerText.toLowerCase();

                    const rowSeverity =
                        row.cells[0].innerText.trim();

                    const matchesSearch = text.includes(search);

                    const matchesSeverity =
                        severity === "ALL" ||
                        rowSeverity === severity;

                    row.style.display =
                        matchesSearch && matchesSeverity ? "" : "none";

                }});

            }}
        </script>

    </body>
    </html>
    """

    DASHBOARD_PATH.write_text(html, encoding="utf-8")

    print("[+] Dashboard generated successfully.")
    print(f"[+] Total findings displayed: {len(findings)}")
    print(f"[+] Saved to: {DASHBOARD_PATH}")


if __name__ == "__main__":
    report = load_report()
    generate_dashboard(report)

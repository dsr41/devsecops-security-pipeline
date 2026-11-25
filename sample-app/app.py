
import sqlite3
import subprocess

# --------------------------------------------------
# DEMO 1: Hardcoded credentials
# Intended finding: Hardcoded secret
# --------------------------------------------------

AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "EXAMPLE_SECRET_KEY_DO_NOT_USE"


# --------------------------------------------------
# DEMO 2: SQL Injection
# Intended finding: Unsafe SQL query construction
# --------------------------------------------------

def get_user(username):
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()

    cursor.execute(
        "CREATE TABLE users (id INTEGER, username TEXT)"
    )

    # Vulnerable: user input is directly inserted into SQL.
    query = f"SELECT * FROM users WHERE username = '{username}'"

    cursor.execute(query)
    result = cursor.fetchall()

    connection.close()
    return result


# --------------------------------------------------
# DEMO 3: Command Injection
# Intended finding: Unsafe shell command execution
# --------------------------------------------------

def check_ping(target):
    # Vulnerable: untrusted input is passed to a shell.
    result = subprocess.run(
        f"ping -n 1 {target}",
        shell=True,
        capture_output=True,
        text=True
    )

    return result.stdout
# DEMO 4: Fake GitHub personal access token
# Intended finding: Hardcoded GitHub token

GITHUB_TOKEN = "ghp_abcdefghijklmnopqrstuvwxyz012345"

if __name__ == "__main__":
    print("DevSecOps sample application")
    print("This application contains intentional security weaknesses.")
DEMO_TOKEN = "demo_token: pOIAj9x47WT5qElx5JrI3e7O714HgaAIz2ck9sVn"
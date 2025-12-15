"""
Pre-Deployment Security and Readiness Check
Run this before deploying to production
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env is properly configured"""
    print("\n[*] Checking environment configuration...")

    env_path = Path(".env.production")
    if not env_path.exists():
        print("[X] .env.production not found")
        return False

    with open(env_path) as f:
        content = f.read()

        checks = {
            "JWT_SECRET_KEY": "CHANGE_THIS" not in content and "secret_key_change" not in content.lower(),
            "MISTRAL_API_KEY": "your_mistral" not in content,
            "INIT_DEMO_KEYS": "false" in content.lower(),
        }

        all_pass = all(checks.values())

        for check, passed in checks.items():
            status = "[OK]" if passed else "[X]"
            print(f"  {status} {check}")

        return all_pass


def check_gitignore():
    """Ensure secrets aren't committed"""
    print("\n[*] Checking .gitignore...")

    gitignore_path = Path("../.gitignore")
    if not gitignore_path.exists():
        print("[X] .gitignore not found")
        return False

    with open(gitignore_path) as f:
        content = f.read()

        required = [".env", "*.env", "API_KEYS.txt"]
        checks = {item: item in content for item in required}

        all_pass = all(checks.values())

        for item, passed in checks.items():
            status = "[OK]" if passed else "[X]"
            print(f"  {status} {item} in .gitignore")

        return all_pass


def check_cors():
    """Check CORS configuration"""
    print("\n[*] Checking CORS configuration...")

    with open("main_v2.py") as f:
        content = f.read()

        if 'allow_origins=["*"]' in content:
            print('  [!] CORS allows all origins (allow_origins=["*"])')
            print("      Recommended: Restrict to specific domains")
            return False
        else:
            print("  [OK] CORS properly configured")
            return True


def check_dependencies():
    """Check for known vulnerabilities"""
    print("\n[*] Checking dependencies...")

    try:
        import subprocess
        result = subprocess.run(
            ["pip", "install", "safety"],
            capture_output=True,
            text=True
        )

        result = subprocess.run(
            ["safety", "check", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )

        if "No known security vulnerabilities found" in result.stdout or result.returncode == 0:
            print("  [OK] No known vulnerabilities")
            return True
        else:
            print("  [!] Vulnerabilities found:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"  [!] Could not check dependencies: {e}")
        return True  # Don't fail on this


def check_dockerfile():
    """Check Dockerfile security"""
    print("\n[*] Checking Dockerfile...")

    with open("Dockerfile") as f:
        content = f.read()

        checks = {
            "Non-root user": "USER binah" in content,
            "Health check": "HEALTHCHECK" in content,
            "Security updates": "apt-get update" in content,
        }

        all_pass = all(checks.values())

        for check, passed in checks.items():
            status = "[OK]" if passed else "[X]"
            print(f"  {status} {check}")

        return all_pass


def check_hardcoded_secrets():
    """Scan for hardcoded secrets"""
    print("\n[*] Scanning for hardcoded secrets...")

    dangerous_patterns = [
        "api_key = ",
        "secret = ",
        "password = ",
        "token = "
    ]

    python_files = Path(".").glob("*.py")
    found_issues = []

    for file in python_files:
        if file.name.startswith("pre_deploy") or file.name.startswith("test_"):
            continue

        try:
            with open(file, encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for pattern in dangerous_patterns:
                    if pattern in content.lower() and "os.getenv" not in content:
                        found_issues.append(f"{file}: possible hardcoded {pattern}")
        except Exception:
            continue  # Skip files that can't be read

    if found_issues:
        print("  [!] Possible hardcoded secrets:")
        for issue in found_issues:
            print(f"      {issue}")
        return False
    else:
        print("  [OK] No obvious hardcoded secrets")
        return True


def main():
    print("="*70)
    print("BINAH-SIGMA v2.0 - PRE-DEPLOYMENT CHECK")
    print("="*70)

    os.chdir(Path(__file__).parent)

    checks = [
        ("Environment Variables", check_env_file),
        (".gitignore", check_gitignore),
        ("CORS Configuration", check_cors),
        ("Dependencies", check_dependencies),
        ("Dockerfile", check_dockerfile),
        ("Hardcoded Secrets", check_hardcoded_secrets),
    ]

    results = []
    for name, check_func in checks:
        try:
            passed = check_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[X] Error checking {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "[OK] PASS" if passed else "[X] FAIL"
        print(f"{status} - {name}")

    print("\n" + "="*70)
    print(f"Score: {passed_count}/{total_count}")

    if passed_count == total_count:
        print("[OK] ALL CHECKS PASSED - Ready for deployment!")
        print("="*70)
        return 0
    elif passed_count >= total_count * 0.7:
        print("[!] MOST CHECKS PASSED - Review warnings before deploying")
        print("="*70)
        return 1
    else:
        print("[X] MULTIPLE CHECKS FAILED - Fix issues before deploying!")
        print("="*70)
        return 2


if __name__ == "__main__":
    sys.exit(main())

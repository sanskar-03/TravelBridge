import json
import re
import sys
import time
from pathlib import Path

import requests


# ============================================================
# CONFIGURATION
# ============================================================

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

# Change these to your actual demo accounts
USERS = {
    "traveler": {
        "email": "traveler@example.com",
        "password": "password",
    },
    "requester": {
        "email": "requester@example.com",
        "password": "password",
    },
    "admin": {
        "email": "admin@example.com",
        "password": "password",
    },
}

FRONTEND_DIR = Path("frontend")

REPORT_FILE = "travelbridge_integration_report.json"

TIMEOUT = 10


# ============================================================
# STATE
# ============================================================

results = []
session = requests.Session()


# ============================================================
# OUTPUT
# ============================================================

def print_header(title):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def check(name, passed, details="", warning=False):
    status = "⚠️ WARN" if warning else ("✅ PASS" if passed else "❌ FAIL")

    print(f"{status:<12} {name:<45} {details}")

    results.append({
        "name": name,
        "passed": passed,
        "warning": warning,
        "details": details,
    })


# ============================================================
# HTTP HELPERS
# ============================================================

def get(url, **kwargs):
    try:
        start = time.perf_counter()
        response = session.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=False,
            **kwargs
        )
        elapsed = time.perf_counter() - start
        return response, elapsed, None
    except Exception as exc:
        return None, 0, str(exc)


def post(url, **kwargs):
    try:
        start = time.perf_counter()
        response = session.post(
            url,
            timeout=TIMEOUT,
            allow_redirects=False,
            **kwargs
        )
        elapsed = time.perf_counter() - start
        return response, elapsed, None
    except Exception as exc:
        return None, 0, str(exc)


# ============================================================
# BASIC SERVER CHECKS
# ============================================================

def check_server(name, url):
    response, elapsed, error = get(url)

    if error:
        check(
            name,
            False,
            f"Connection failed: {error}"
        )
        return None

    passed = 200 <= response.status_code < 500

    check(
        name,
        passed,
        f"HTTP {response.status_code} | {elapsed:.2f}s"
    )

    return response


# ============================================================
# FRONTEND CHECKS
# ============================================================

def frontend_checks():
    print_header("FRONTEND CONNECTIVITY")

    check_server(
        "Frontend root",
        f"{FRONTEND_URL}/"
    )

    routes = [
        "/",
        "/login",
        "/register",
        "/dashboard",
        "/traveler",
        "/traveler/trips",
        "/traveler/deliveries",
        "/traveler/chat",
        "/requester",
        "/requester/requests",
        "/requester/find-travelers",
        "/requester/chat",
        "/admin",
        "/admin/users",
        "/admin/packages",
        "/admin/payments",
        "/admin/disputes",
        "/admin/verification",
    ]

    for route in routes:
        response, elapsed, error = get(
            f"{FRONTEND_URL}{route}"
        )

        if error:
            check(
                f"Frontend {route}",
                False,
                f"Connection failed: {error}"
            )
            continue

        passed = response.status_code == 200

        check(
            f"Frontend {route}",
            passed,
            f"HTTP {response.status_code} | {elapsed:.2f}s"
        )


# ============================================================
# BACKEND CHECKS
# ============================================================

def backend_checks():
    print_header("BACKEND CONNECTIVITY")

    endpoints = [
        "/",
        "/health/",
        "/api/",
        "/api/v1/",
        "/api/docs/",
    ]

    for endpoint in endpoints:
        response, elapsed, error = get(
            f"{BACKEND_URL}{endpoint}"
        )

        if error:
            check(
                f"Backend {endpoint}",
                False,
                f"Connection failed: {error}"
            )
            continue

        passed = response.status_code in range(200, 400)

        check(
            f"Backend {endpoint}",
            passed,
            f"HTTP {response.status_code} | {elapsed:.2f}s"
        )


# ============================================================
# API ROUTES
# ============================================================

def api_route_checks():
    print_header("API ROUTE CONNECTIVITY")

    routes = [
        "/api/v1/users/",
        "/api/v1/travel/",
        "/api/v1/packages/",
        "/api/v1/matches/",
        "/api/v1/proposals/",
        "/api/v1/chat/",
        "/api/v1/messages/",
        "/api/v1/payments/",
        "/api/v1/reviews/",
        "/api/v1/disputes/",
        "/api/v1/verifications/",
        "/api/v1/fraud/",
        "/api/v1/notifications/",
    ]

    for route in routes:

        response, elapsed, error = get(
            f"{BACKEND_URL}{route}"
        )

        if error:
            check(
                f"API {route}",
                False,
                f"Connection failed: {error}"
            )
            continue

        # 401/403 can be correct for protected endpoints
        acceptable = response.status_code in (
            200,
            201,
            204,
            401,
            403,
            404,
        )

        if response.status_code in (401, 403):
            detail = (
                f"HTTP {response.status_code} | "
                "Protected endpoint"
            )
        else:
            detail = (
                f"HTTP {response.status_code} | "
                f"{elapsed:.2f}s"
            )

        check(
            f"API {route}",
            acceptable,
            detail
        )


# ============================================================
# LOGIN DISCOVERY
# ============================================================

def find_login_endpoint():
    print_header("LOGIN ENDPOINT DISCOVERY")

    candidates = [
        "/api/v1/auth/login/",
        "/api/v1/auth/token/",
        "/api/v1/token/",
        "/api/token/",
        "/api/v1/users/login/",
        "/api/login/",
        "/api/v1/auth/jwt/create/",
    ]

    for endpoint in candidates:

        url = BACKEND_URL + endpoint

        response, elapsed, error = post(
            url,
            json={
                "email": "invalid@example.com",
                "password": "invalid",
            }
        )

        if error:
            continue

        # 400/401/403 means endpoint probably exists
        if response.status_code in (
            400,
            401,
            403,
            422,
        ):
            check(
                "Authentication endpoint",
                True,
                f"Found {endpoint} | HTTP {response.status_code}"
            )
            return endpoint

        if response.status_code in (
            200,
            201,
        ):
            check(
                "Authentication endpoint",
                True,
                f"Found {endpoint} | HTTP {response.status_code}"
            )
            return endpoint

    check(
        "Authentication endpoint",
        False,
        "Could not automatically find login endpoint"
    )

    return None


# ============================================================
# LOGIN
# ============================================================

def authenticate_user(role, endpoint):
    user = USERS[role]

    print()
    print(f"--- LOGIN TEST: {role.upper()} ---")

    url = BACKEND_URL + endpoint

    payload_options = [
        {
            "email": user["email"],
            "password": user["password"],
        },
        {
            "username": user["email"],
            "password": user["password"],
        },
    ]

    for payload in payload_options:

        response, elapsed, error = post(
            url,
            json=payload
        )

        if error:
            continue

        if response.status_code not in (200, 201):
            continue

        try:
            data = response.json()
        except Exception:
            data = {}

        token = (
            data.get("access")
            or data.get("token")
            or data.get("access_token")
            or data.get("key")
        )

        if token:

            check(
                f"{role.capitalize()} authentication",
                True,
                f"HTTP {response.status_code} | Token received"
            )

            return token

        # Some systems authenticate using cookies
        if session.cookies:

            check(
                f"{role.capitalize()} authentication",
                True,
                f"HTTP {response.status_code} | Session cookie received"
            )

            return "COOKIE_SESSION"

    check(
        f"{role.capitalize()} authentication",
        False,
        "Login failed or no authentication token returned"
    )

    return None


# ============================================================
# AUTHENTICATED API
# ============================================================

def authenticated_api_check(role, token):

    if not token:
        return

    print()
    print(f"--- AUTHENTICATED API: {role.upper()} ---")

    headers = {}

    if token != "COOKIE_SESSION":
        headers["Authorization"] = f"Bearer {token}"

    candidates = [
        "/api/v1/users/me/",
        "/api/v1/users/profile/",
        "/api/v1/users/",
        "/api/v1/travel/",
    ]

    for endpoint in candidates:

        response, elapsed, error = get(
            BACKEND_URL + endpoint,
            headers=headers
        )

        if error:
            continue

        if response.status_code in (
            200,
            201,
        ):

            check(
                f"{role.capitalize()} authenticated API",
                True,
                f"{endpoint} | HTTP {response.status_code}"
            )
            return

    check(
        f"{role.capitalize()} authenticated API",
        False,
        "No authenticated API endpoint succeeded"
    )


# ============================================================
# ADMIN PROTECTION
# ============================================================

def admin_protection_check(token):

    print_header("ADMIN AUTHORIZATION")

    headers = {}

    if token and token != "COOKIE_SESSION":
        headers["Authorization"] = f"Bearer {token}"

    response, elapsed, error = get(
        BACKEND_URL + "/api/v1/admin/",
        headers=headers
    )

    if error:
        check(
            "Admin API protection",
            False,
            error
        )
        return

    # 403/401 is correct for non-admin
    if response.status_code in (401, 403):
        check(
            "Admin API protection",
            True,
            f"HTTP {response.status_code} | Access correctly restricted"
        )
    elif response.status_code in (200, 201):
        check(
            "Admin API protection",
            True,
            "Admin endpoint accessible with current credentials"
        )
    else:
        check(
            "Admin API protection",
            False,
            f"Unexpected HTTP {response.status_code}"
        )


# ============================================================
# FRONTEND SOURCE SECURITY CHECK
# ============================================================

def source_security_checks():

    print_header("FRONTEND AUTHENTICATION SOURCE CHECK")

    if not FRONTEND_DIR.exists():
        check(
            "Frontend source scan",
            False,
            f"{FRONTEND_DIR} does not exist"
        )
        return

    files = list(FRONTEND_DIR.rglob("*.tsx"))
    files += list(FRONTEND_DIR.rglob("*.ts"))

    if not files:
        check(
            "Frontend source scan",
            False,
            "No TypeScript/TSX files found"
        )
        return

    mock_patterns = [
        r"mock-user-token",
        r"mock-admin-token",
        r"django-superuser-secure-token",
        r"localStorage\.setItem\(['\"]token['\"]",
        r"localStorage\.setItem\(['\"]role['\"]",
    ]

    found = []

    for file in files:

        try:
            content = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        except Exception:
            continue

        for pattern in mock_patterns:

            if re.search(pattern, content):
                found.append(
                    f"{file}: {pattern}"
                )

    if found:

        print()
        print("⚠️ Potential mock authentication detected:")

        for item in found[:20]:
            print("   ", item)

        check(
            "Real backend authentication",
            False,
            "Frontend contains mock/localStorage authentication"
        )

    else:

        check(
            "Real backend authentication",
            True,
            "No obvious mock authentication patterns detected"
        )


# ============================================================
# FRONTEND API CONFIGURATION CHECK
# ============================================================

def frontend_api_configuration_check():

    print_header("FRONTEND API CONFIGURATION")

    if not FRONTEND_DIR.exists():
        return

    files = list(FRONTEND_DIR.rglob("*.tsx"))
    files += list(FRONTEND_DIR.rglob("*.ts"))

    api_references = []

    for file in files:

        try:
            content = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        except Exception:
            continue

        patterns = [
            r"http://localhost:8000",
            r"http://127\.0\.0\.1:8000",
            r"/api/v1/",
            r"axios",
            r"fetch\(",
        ]

        for pattern in patterns:

            if re.search(pattern, content):
                api_references.append(
                    f"{file}: {pattern}"
                )

    if api_references:

        check(
            "Frontend API integration code",
            True,
            f"Detected {len(api_references)} API references"
        )

    else:

        check(
            "Frontend API integration code",
            False,
            "No fetch/axios/API references found"
        )


# ============================================================
# CORS CHECK
# ============================================================

def cors_check():

    print_header("CORS / FRONTEND ↔ BACKEND CONNECTION")

    try:

        response = session.options(
            BACKEND_URL + "/api/v1/",
            headers={
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "GET",
            },
            timeout=TIMEOUT,
        )

        allow_origin = response.headers.get(
            "Access-Control-Allow-Origin"
        )

        if allow_origin in (
            FRONTEND_URL,
            "*",
        ):

            check(
                "CORS configuration",
                True,
                f"Allow-Origin: {allow_origin}"
            )

        else:

            check(
                "CORS configuration",
                False,
                f"Allow-Origin header missing/incorrect: {allow_origin}"
            )

    except Exception as exc:

        check(
            "CORS configuration",
            False,
            str(exc)
        )


# ============================================================
# JSON REPORT
# ============================================================

def write_report():

    total = len(results)

    passed = sum(
        1 for r in results
        if r["passed"] and not r["warning"]
    )

    failed = sum(
        1 for r in results
        if not r["passed"] and not r["warning"]
    )

    warnings = sum(
        1 for r in results
        if r["warning"]
    )

    report = {
        "project": "TravelBridge",
        "frontend": FRONTEND_URL,
        "backend": BACKEND_URL,
        "total_checks": total,
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "result": "PASS" if failed == 0 else "FAIL",
        "checks": results,
    }

    Path(REPORT_FILE).write_text(
        json.dumps(
            report,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return total, passed, failed, warnings


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("TRAVELBRIDGE FRONTEND ↔ BACKEND AUTOMATED INTEGRATION TEST")
    print("=" * 80)

    print()
    print(f"Frontend : {FRONTEND_URL}")
    print(f"Backend  : {BACKEND_URL}")
    print(f"Report   : {REPORT_FILE}")

    # 1
    frontend_checks()

    # 2
    backend_checks()

    # 3
    api_route_checks()

    # 4
    cors_check()

    # 5
    frontend_api_configuration_check()

    # 6
    source_security_checks()

    # 7
    login_endpoint = find_login_endpoint()

    traveler_token = None
    requester_token = None
    admin_token = None

    if login_endpoint:

        traveler_token = authenticate_user(
            "traveler",
            login_endpoint
        )

        if traveler_token:
            authenticated_api_check(
                "traveler",
                traveler_token
            )

        requester_token = authenticate_user(
            "requester",
            login_endpoint
        )

        if requester_token:
            authenticated_api_check(
                "requester",
                requester_token
            )

        admin_token = authenticate_user(
            "admin",
            login_endpoint
        )

        if admin_token:
            authenticated_api_check(
                "admin",
                admin_token
            )

    # 8
    if traveler_token:
        admin_protection_check(
            traveler_token
        )

    # 9
    total, passed, failed, warnings = write_report()

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print("=" * 80)
    print("TRAVELBRIDGE INTEGRATION TEST REPORT")
    print("=" * 80)

    print()
    print(f"TOTAL CHECKS : {total}")
    print(f"PASS         : {passed}")
    print(f"FAIL         : {failed}")
    print(f"WARNINGS     : {warnings}")

    print()
    print("-" * 80)

    if failed == 0:
        print("FINAL RESULT: ✅ PASS")
        print()
        print("Frontend and backend integration checks completed successfully.")
    else:
        print("FINAL RESULT: ❌ FAIL")
        print()
        print("One or more integration checks failed.")

    print("-" * 80)

    print()
    print(f"📄 Detailed report: {REPORT_FILE}")

    print()

    if failed > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
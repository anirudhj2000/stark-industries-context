#!/usr/bin/env python3
"""
GitHub App Installation Token Generator

Generates GitHub App JWT and exchanges it for an installation access token.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import jwt
    import httpx
except ImportError as e:
    print(f"ERROR: Missing required package: {e}", file=sys.stderr)
    print("Install with: pip install PyJWT httpx cryptography", file=sys.stderr)
    sys.exit(1)


def generate_app_jwt(app_id: str, private_key: str) -> str:
    """
    Generate GitHub App JWT (valid 10 minutes).

    Args:
        app_id: GitHub App ID
        private_key: GitHub App private key (PEM format)

    Returns:
        JWT token string
    """
    now = int(time.time())

    payload = {
        "iat": now - 60,  # Issued 60 seconds in the past to account for clock drift
        "exp": now + 600,  # Expires in 10 minutes
        "iss": app_id
    }

    try:
        token = jwt.encode(payload, private_key, algorithm="RS256")
        return token
    except Exception as e:
        raise ValueError(f"Failed to generate JWT: {e}")


def get_installation_token(installation_id: str, app_jwt: str) -> dict:
    """
    Exchange GitHub App JWT for installation access token.

    Args:
        installation_id: Installation ID from GitHub App
        app_jwt: GitHub App JWT

    Returns:
        {
            "token": "ghs_xxx",
            "expires_at": "2025-12-30T12:00:00Z"
        }
    """
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    try:
        response = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30
        )

        # Better error handling - show response body on error
        if not response.is_success:
            error_detail = response.text[:500] if response.text else "No details"
            if response.status_code == 401:
                raise httpx.HTTPError(
                    f"401 Unauthorized: Invalid GitHub App JWT or credentials. "
                    f"Verify GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY are correct. "
                    f"Detail: {error_detail}"
                )
            elif response.status_code == 404:
                raise httpx.HTTPError(
                    f"404 Not Found: Installation ID {installation_id} not found. "
                    f"Verify the installation ID is correct and the app is installed. "
                    f"Detail: {error_detail}"
                )
            else:
                raise httpx.HTTPError(
                    f"{response.status_code} {response.reason_phrase}: {error_detail}"
                )

        data = response.json()
        return {
            "token": data["token"],
            "expires_at": data["expires_at"]
        }

    except httpx.TimeoutException:
        raise Exception("GitHub API request timed out after 30 seconds")
    except httpx.HTTPError as e:
        raise Exception(f"GitHub API error: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error calling GitHub API: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate GitHub App installation access token"
    )
    parser.add_argument(
        "--installation-id",
        required=True,
        help="GitHub App installation ID"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path for token JSON"
    )

    args = parser.parse_args()

    # Get credentials from environment
    app_id = os.getenv("GITHUB_APP_ID") or "2561206"
    private_key = os.getenv("GITHUB_APP_PRIVATE_KEY") or "-----BEGIN RSA PRIVATE KEY-----\nMIIEpQIBAAKCAQEAza+b2HT+GKtzmArcLylB9qwXItuOsrNQ473IbMmYx6M5B54H\nAefOEqE5E5Cubo3J/hI4YjBCp6CrAc9lOplBzQPqN4khnP5BvKL6b1fPc0JCuI4C\nKLbrIDBeXzubyvgFUAzLmjznuuAa6JMULMKS4g+iNQP1iH3EdX/u9PrWhCh4b6mX\nium7JGhrAAWZzXCqJ5QbsZqqDeZ7U3IE5i5cKxn6jTlVVTeHLwCvn6V8idZxLgXM\n+kRWdmyJCXGd3VvNeFHoSqa7HGzTSzVoOyKvix6r/lhaTA14mDTvR9KeIYGpNJXU\nJ421p1Qb60ie39CfPkvXnhgM6wZIahLMv+vBowIDAQABAoIBAQDBL3ke2vN1VENj\nwH+BxCxydLveP31NlmIZJT1EAC0BBOshnmlSftfsY4TqPW+34nCfs5lFj7JrItq6\n/oJDgYJt/olT0/bAL4aqmCDDxyPPS6LDGI4qk3NPbl6U77Wp8z16LCpnGWFFAgwD\n+XBvgejXbnuZc7h/lDCbc6eKbLZitLkaSHaGwmf06Yt3zBOgpEIK5lPzQbIyFUJB\nnn0LH0wqJrGFvlSq3I8chaS7HDvxIoX6UbqYREmfudbpuw8LQO+RbL7L9rw3DvZd\nXk8jL2oCB3srRB4/xICioGLg8YF+D4KQMrAgMNgXUqAXpPWMPiBaqwTtwhCgbQBK\nU6DkcbnhAoGBAOmuAj/RnZ4NfH/AZCEfbIlv8NjM2roM1ImkzDidkK6VsuOIrM6e\nLI8QpqB0es9P8bLS9lNNuvgXXX9Te72ntj29sKbk5nv6KECpEZqLTcyY7iVH8iE4\nAmWIIa3BZ2v9ZcS46zuxcdKmBYy9NXlzjfHBrYMPJO1eD/A1VFInGxUZAoGBAOFV\nFxtfU7i2QuXLdN+LUpiU7xVwHh10QBUBMx/p1yH8kOfFMS1mmGgqHDO/Yz4I+3rn\nAIQSROeKsDgziTDgEF5Argwm0daWR/GluNmM3oFe/4U+1Rxj7Ny3nlEQ0ZQ+gXwY\nOqCASTfWsxmlnYJtu+zbiWES165PB1wo6pVp3cgbAoGBANtcNs5T5sMk49dE8nnJ\ndui5hXzvKPB39NhVNER9XQEWk/xWI+o9v5R5TAHZ9iNAZ6K3uPZQRJB51pIc+074\n7fGdbQPuYpLFLR4t19GcrWa/tOaYWCpo2o8XMI5cvMo58FuwP1ok47WbliAcyeL9\n36SvbENYZxDQOOQEG+iWvyyZAoGAAqI5+OnuUpRex8zO+uXn+zySZs++ql13ekdf\nT5ouF4maL/tQDdXLJjyHw9sSz+DO/6q/iMul3obydFW13spfpppe7mltvnJXOO3U\n8UYCO8Tee7I2T3SjihjjUtM9f9wTK14lIUcek/aAdWZIJwQdVDFks6vCtZja3yrj\nQwfPvc0CgYEAjhYeaT73uvUfjFHp8MGlagI2YalIERY4/xrOjz/elK7lOlGIvOrf\nt4Xhx+UNwJEo0cv8nk3Q4ZmsBC0iEa42g2+F5TAHzmUGTkzkjUyJYtxRc1u62xqW\nLR3+z6G8YZqQcSqAd9hM94qNheUrOLkW4kKx/rFDJDmDq/ZA5ZKqcw4=\n-----END RSA PRIVATE KEY-----"

    if not app_id:
        print("ERROR: GITHUB_APP_ID environment variable not set", file=sys.stderr)
        sys.exit(1)

    if not private_key:
        print("ERROR: GITHUB_APP_PRIVATE_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    try:
        # Generate JWT
        print(f"Generating GitHub App JWT for App ID: {app_id}", file=sys.stderr)
        app_jwt = generate_app_jwt(app_id, private_key) # type: ignore

        # Exchange for installation token
        print(f"Requesting installation token for Installation ID: {args.installation_id}", file=sys.stderr)
        token_data = get_installation_token(args.installation_id, app_jwt)

        # Write to output file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(token_data, f, indent=2)

        print(f"Token generated successfully", file=sys.stderr)
        print(f"Expires at: {token_data['expires_at']}", file=sys.stderr)
        print(f"Written to: {args.output}", file=sys.stderr)

        # Also output to stdout for piping
        print(json.dumps(token_data))

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

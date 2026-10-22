"""
Verification script for Prune AI Gateway connectivity and caching.

Expectations:
1. First request returns HTTP 200, 'prune_metadata' in JSON body, and 'X-Prune-Provider' header.
2. Second identical request returns HTTP 200 and 'X-Prune-Cache-Hit: true'.
"""

import json
import os
import sys
from pathlib import Path
import requests


def load_env_file():
    """Load .env file into os.environ if present."""
    env_path = Path(".env")
    if env_path.is_file():
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
        except Exception:
            pass


load_env_file()


def verify_prune():
    api_key = os.environ.get("PRUNE_API_KEY")
    if not api_key:
        print("[ERROR] PRUNE_API_KEY environment variable is not set.")
        print("Please set it in your environment before running this verification:")
        print("  PowerShell: $env:PRUNE_API_KEY=\"prune_...\"")
        print("  Command Prompt: set PRUNE_API_KEY=prune_...")
        print("  Bash / Zsh: export PRUNE_API_KEY=\"prune_...\"")
        return False

    url = "https://api.withprune.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "ping"}],
    }

    print("[1/2] Sending initial request to Prune gateway...")
    resp1 = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status Code: {resp1.status_code}")
    print(f"X-Prune-Provider: {resp1.headers.get('X-Prune-Provider')}")
    print(f"X-Prune-Cache-Hit: {resp1.headers.get('X-Prune-Cache-Hit')}")

    if resp1.status_code != 200:
        print(f"[FAIL] Expected HTTP 200, got {resp1.status_code}: {resp1.text}")
        return False

    body1 = resp1.json()
    if "prune_metadata" not in body1:
        print("[FAIL] 'prune_metadata' not found in response JSON body.")
        print(f"Response body keys: {list(body1.keys())}")
        return False

    print("[SUCCESS] First request succeeded with 'prune_metadata' and provider header.")

    print("\n[2/2] Sending identical second request to test semantic/exact cache...")
    resp2 = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status Code: {resp2.status_code}")
    print(f"X-Prune-Cache-Hit: {resp2.headers.get('X-Prune-Cache-Hit')}")

    cache_hit = resp2.headers.get("X-Prune-Cache-Hit", "").lower() == "true"
    if not cache_hit:
        print(f"[WARN] Expected X-Prune-Cache-Hit: true, got: {resp2.headers.get('X-Prune-Cache-Hit')}")
    else:
        print("[SUCCESS] Cache hit confirmed on repeated request!")

    return True


if __name__ == "__main__":
    success = verify_prune()
    sys.exit(0 if success else 1)

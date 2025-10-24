from katarchive.utils.logger import get_logger
import json
import os
import requests
import sys
import urllib.parse

logger = get_logger("login")


def save_tokens(path, data, refreshed=False):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    if not refreshed:
        logger.info(f"✅ Tokens saved to {path}")


def load_token(path):
    with open(path) as f:
        tokens = json.load(f)
    return tokens["access_token"]


def try_refresh(config):
    token_path = config["token_path"]
    refresh_url = config["refresh_url"]

    if not os.path.exists(token_path):
        return None

    try:
        with open(token_path) as f:
            tokens = json.load(f)
        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            return None

        logger.info("🔄 Attempting to refresh token...")
        response = requests.post(
            refresh_url,
            json={"refresh_token": refresh_token},
            verify=config.get("no_check_certificate"),
        )
        if response.status_code == 200:
            tokens = response.json()
            save_tokens(token_path, tokens, refreshed=True)
            logger.info("✅ Token refreshed successfully.")
            return tokens
        else:
            logger.info("⚠️ Refresh failed:", response.text)
            return None
    except Exception as e:
        logger.info(f"⚠️ Refresh error: {e}")
        return None


def full_login(config):
    token_path = config["token_path"]
    init_url = config["init_url"]
    exchange_url = config["exchange_url"]

    logger.info("🔑 Requesting authentication URL...")
    response = requests.get(init_url, verify=config.get("no_check_certificate"))
    response.raise_for_status()
    auth_info = response.json()
    auth_url = auth_info["auth_url"]
    state = auth_info["state"]

    logger.info(f"🌐 Please log in via your browser:\n\n{auth_url}\n")

    logger.info("🔗 After completing login, paste the full redirect URL here: ")
    sys.stderr.flush()
    redirect_url = input().strip()

    parsed = urllib.parse.urlparse(redirect_url)
    query = urllib.parse.parse_qs(parsed.query)
    code = query.get("code", [None])[0]
    state_returned = query.get("state", [None])[0]

    if not code or state_returned != state:
        logger.info("❌ Invalid redirect URL or mismatched state")
        return None

    logger.info("🔄 Exchanging code for tokens...")
    query["manual"] = "true"
    response = requests.get(
        f"{exchange_url}?{urllib.parse.urlencode(query, doseq=True)}",
        verify=config.get("no_check_certificate"),
        params={"code": code, "state": state},
    )
    response.raise_for_status()
    tokens = response.json()
    save_tokens(token_path, tokens)
    logger.info("🎉 Login complete.")
    return tokens


def login(config):
    return try_refresh(config) or full_login(config)


def configure_auth(base_url: str, no_check_certificate: bool = False) -> dict:
    base = base_url.rstrip("/")
    config = {
        "base_url": base,
        "token_path": "tokens.json",
        "refresh_url": f"{base}/_auth/pkce-cli-refresh",
        "exchange_url": f"{base}/_auth/pkce-cli-auth-complete",
        "init_url": f"{base}/_auth/pkce-cli-auth-url",
        "no_check_certificate": not no_check_certificate,
    }

    return config

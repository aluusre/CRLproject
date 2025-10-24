# Usage :
import os
import json
import time
import requests
import base64

# ==========================================================
# CONFIGURATION
# ==========================================================
MAX_EXECUTION_TIME = 180  # 3 minutes timeout
GITHUB_URL = "https://raw.githubusercontent.com/aluusre/CRLproject/main/CRLURLs.json"

# ==========================================================
# MAIN HANDLER
# ==========================================================

def handler(event, context):
    start_time = time.time()

    # Defaults if not provided in event
    event_type = "CDNCheck"
    obj_type = "crl"

    # Fetch CRL list from GitHub JSON file
    try:
        print(f"Fetching CRL URLs from {GITHUB_URL}")
        resp = requests.get(GITHUB_URL, timeout=10)
        resp.raise_for_status()
        github_data = resp.json()

        # Expecting format: { "urls": [ ... ] }
        urls = github_data.get("urls", [])
    except Exception as e:
        return {"error": f"Failed to fetch CRL list: {e}"}

    if not urls:
        return {"error": "No URLs found in GitHub JSON file."}

    # Prepare Relic credentials (optional encryption/base64)
    relic_api_key = _decrypt_env_var("RELIC_API_KEY_ENC")
    relic_account_id = _decrypt_env_var("RELIC_ACCOUNT_ID_ENC")

    if not relic_api_key or not relic_account_id:
        print("Missing or invalid New Relic credentials.")
        relic_api_key = None
        relic_account_id = None

    results = []
    for url in urls:
        elapsed = int(time.time() - start_time)
        if elapsed >= MAX_EXECUTION_TIME:
            print("⏳ Execution time exceeded 3 minutes. Stopping early.")
            break

        result = _download_crl(url, event_type, obj_type)
        results.append(result)

    # Send results to New Relic if credentials exist
    if relic_api_key and relic_account_id:
        send_to_newrelic(relic_account_id, relic_api_key, results)

    return results


# ==========================================================
# DOWNLOAD CRL FUNCTION
# ==========================================================

def _download_crl(url, event_type, obj_type):
    result = {
        "eventType": event_type,
        "type": obj_type,
        "url": url,
        "duration": 0,
        "success": False,
        "error": ""
    }

    start = time.time()
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        result["success"] = True
    except Exception as e:
        result["error"] = str(e)
        result["success"] = False

    result["duration"] = int(time.time() - start)
    return result


# ==========================================================
# SEND RESULTS TO NEW RELIC
# ==========================================================

def send_to_newrelic(account_id, api_key, data):
    try:
        url = f"https://insights-collector.newrelic.com/v1/accounts/{account_id}/events"
        headers = {
            "Content-Type": "application/json",
            "Api-Key": api_key,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        response.raise_for_status()
        print(f"Sent {len(data)} results to New Relic.")
    except Exception as e:
        print(f"Failed to send data to New Relic: {e}")


# ==========================================================
# DECRYPT FUNCTION (Placeholder Example)
# ==========================================================

def _decrypt_env_var(env_key):
    """
    For demo, we just Base64-decode.
    In production, integrate with Aliyun KMS or context.credentials.
    """
    value = os.environ.get(env_key)
    if not value:
        return None
    try:
        return base64.b64decode(value).decode("utf-8")
    except Exception:
        return None


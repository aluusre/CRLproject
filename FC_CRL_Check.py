# Usage : Fetch URLs JSON format from GitHub 
# Encrypt Base64 : echo -n "YOUR_RELIC_API_KEY" | base64
# NR Query Data : SELECT count(*) FROM CDNCheck WHERE success = 'false' SINCE 1 day ago

import os
import json
import time
import requests
import oss2
import base64
import hmac
import hashlib
import threading


MAX_EXECUTION_TIME = 180  # 3 minutes

# Environment variables (to be set in Function Compute console):
#   RELIC_API_KEY_ENC       → base64-encoded and encrypted Relic API key
#   RELIC_ACCOUNT_ID_ENC    → base64-encoded and encrypted Relic account ID
#   NEW_RELIC_EVENT_URL     → e.g. "https://insights-collector.newrelic.com/v1/accounts/{account_id}/events"


###### MAIN 
def handler(event, context):

    try:
        payload = json.loads(event)
    except Exception:
        return {"error": "Invalid event format. Must be JSON."}

    event_type = payload.get("eventType", "CDNCheck")
    obj_type = payload.get("type", "crl")
    urls = payload.get("urls") or payload.get("URLs")

    if not urls or not isinstance(urls, list):
        return {"error": "Missing or invalid 'urls' list in event."}

    # Prepare Relic credentials
    relic_api_key = _decrypt_env_var("RELIC_API_KEY_ENC")
    relic_account_id = _decrypt_env_var("RELIC_ACCOUNT_ID_ENC")

    if not relic_api_key or not relic_account_id:
        return {"error": "Missing Relic API credentials."}

    results = []
    start_time = time.time()

    for url in urls:
        elapsed = int(time.time() - start_time)
        if elapsed >= MAX_EXECUTION_TIME:
            print("Execution time exceeded 3 minutes. Stopping early.")
            break

        result = _download_crl(url, event_type, obj_type)
        results.append(result)

    # Send results to New Relic
    send_to_newrelic(relic_account_id, relic_api_key, results)

    return results


######## DOWNLOAD CRL FUNCTION
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


######## SEND RESULTS TO NEW RELIC
def send_to_newrelic(account_id, api_key, data):
    try:
        url = f"https://insights-collector.newrelic.com/v1/accounts/{account_id}/events"
        headers = {
            "Content-Type": "application/json",
            "Api-Key": api_key,
        }

        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        response.raise_for_status()
        print(f"Sent {len(data)} events to New Relic.")
    except Exception as e:
        print(f"Failed to send data to New Relic: {e}")


####### DECRYPT FUNCTION
def _decrypt_env_var(env_key):
    """
    For demo, we just Base64-decode.
    In production, integrate with KMS or use context.credentials for RAM-decrypted vars.
    """
    value = os.environ.get(env_key)
    if not value:
        return None
    try:
        return base64.b64decode(value).decode("utf-8")
    except Exception:
        return None


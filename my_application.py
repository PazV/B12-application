import os
import json
import hmac
import hashlib
import requests
from datetime import datetime, timezone


def create_signature(payload_json, secret):
    """Create HMAC-SHA256 signature for the payload."""
    signature = hmac.new(
        secret.encode("utf-8"), payload_json.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def main():
    name = os.environ.get("APPLICANT_NAME")
    email = os.environ.get("APPLICANT_EMAIL")
    resume_link = os.environ.get("RESUME_LINK")
    repository_link = os.environ.get("REPOSITORY_LINK")
    action_run_link = os.environ.get("ACTION_RUN_LINK")

    # Create payload
    payload = {
        "action_run_link": action_run_link,
        "email": email,
        "name": name,
        "repository_link": repository_link,
        "resume_link": resume_link,
        "timestamp": datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z"),
    }

    # Serialize
    payload_json = json.dumps(
        payload, separators=(",", ":"), sort_keys=True, ensure_ascii=False
    )

    # Create signature
    signing_secret = "hello-there-from-b12"
    signature = create_signature(payload_json, signing_secret)

    # Make POST request
    headers = {"Content-Type": "application/json", "X-Signature-256": signature}

    response = requests.post(
        "https://b12.io/apply/submission",
        data=payload_json.encode("utf-8"),
        headers=headers,
    )

    # Check response
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code != 200:
        raise Exception(f"Submission failed with status code {response.status_code}")

    print("Submission successful!")


if __name__ == "__main__":
    main()

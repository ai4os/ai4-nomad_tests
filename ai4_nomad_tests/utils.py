from datetime import datetime, timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import os
import ssl
import socket
import time
from urllib.parse import urlparse

from dotenv import load_dotenv
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth


main_path = Path(__file__).parents[1].absolute()
load_dotenv(main_path / ".env")


class TeeLogger:
    """
    Replicate standard bash tee inside Python to clone standard output and error
    output identically to the terminal.
    We use it to send outputs to Loki.
    """
    def __init__(self, stream1, stream2):
        self.stream1 = stream1
        self.stream2 = stream2
    def write(self, data):
        self.stream1.write(data)
        self.stream2.write(data)
    def flush(self):
        if hasattr(self.stream1, "flush"):
            self.stream1.flush()
        if hasattr(self.stream2, "flush"):
            self.stream2.flush()


def send_logs_to_loki(logs: str, node: str, datacenter: str, status: str):
    """
    Sends logs to the Loki instance.

    :param logs: A string containing the log output (e.g. from a test run).
    :param node: The node label.
    :param datacenter: The datacenter label.
    :param status: The status label (e.g., 'success', 'failed').
    """
    # Load environment variables
    loki_url = os.getenv("LOKI_URL", "https://loki.cloud.ai4eosc.eu/loki/api/v1/push")
    loki_user = os.getenv("LOKI_USER")
    loki_password = os.getenv("LOKI_PASSWORD")

    if not loki_user or not loki_password:
        print("LOKI_USER or LOKI_PASSWORD environment variables are not set. Cannot send logs.")
        return

    # Loki expects timestamp in nanoseconds
    timestamp_ns = str(time.time_ns())

    # Format the payload for Loki Push API
    payload = {
        "streams": [
            {
                "stream": {
                    "job": "nomad-integration-tests",
                    "node": node,
                    "datacenter": datacenter,
                    "status": status
                },
                "values": []
            }
        ]
    }

    # Split multiline logs so Loki can parse them properly
    if logs.strip():
        for line in logs.strip().split("\n"):
            payload["streams"][0]["values"].append([timestamp_ns, line])
    else:
        print("No logs to send.")
        return

    try:
        response = requests.post(
            loki_url,
            json=payload,
            auth=HTTPBasicAuth(loki_user.strip(), loki_password.strip()),
            headers={"Content-Type": "application/json"}
        )
        if response.status_code not in (200, 204):
            print(f"Failed to push logs to Loki. HTTP Status: {response.status_code}")
            print(f"Response: {response.text}")
        else:
            print("Logs successfully sent to Loki.")
    except Exception as e:
        print(f"Error while sending logs to Loki: {e}")


def get_ssl_expiry(url, port=443):
    # Extract hostname from URL
    parsed = urlparse(url)
    hostname = parsed.hostname
    if hostname is None:
        raise ValueError(f"Could not extract hostname from URL: {url!r}")

    # Retrieve cert expiry date
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with socket.create_connection((hostname, port), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            der_cert = ssock.getpeercert(binary_form=True)
            cert = x509.load_der_x509_certificate(der_cert, default_backend())
            return cert.not_valid_after_utc

import hashlib
import os
import random
import ssl
import string
from base64 import urlsafe_b64encode
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

from . import _path_key
from .config import config
from .rate import rate_limiter
from .util import timestamp

__all__ = ["authenticate"]

_activities = [
    "activity",
    "cardio_fitness",
    "electrocardiogram",
    "heartrate",
    "location",
    "nutrition",
    "oxygen_saturation",
    "profile",
    "respiratory_rate",
    "settings",
    "sleep",
    "social",
    "temperature",
    "weight",
]
"""list[str]: Activities to request permission for."""


def _parse_url_args(url: str) -> dict:
    if "?" in url:
        args = [kv.split("=", 1) for kv in url.split("?", 1)[1].split("&")]
        return {k: v for k, v in args}
    else:
        return {}


def authenticate() -> str:
    """Perform API authentication.

    Returns:
        str: Token.
    """

    if not config["session", "token"]:
        # There is no token. Perform full authentication.
        return _full_authentication(config)
    elif (
        config["session", "token"]
        and timestamp() >= config["session", "token_expiry_timestamp_utc"] - 1
    ):
        # There is a token, but it expired. Use the refresh token.
        return _refresh_token(config)
    else:
        # There is a token, and it has not yet expired. Use it.
        return config["session", "token"]


def _full_authentication(config, verifier_length=60, port=4444):
    # Generate a verifier and a challenge.
    verifier = "".join(random.choice(string.digits) for _ in range(verifier_length))
    verifier_hashed = hashlib.sha256(verifier.encode("utf-8")).digest()
    challenge = urlsafe_b64encode(verifier_hashed).decode("utf-8")
    # Remove optional padding.
    while challenge[-1] == "=":
        challenge = challenge[:-1]

    # Produce authorisation URL.
    auth_url = (
        "https://www.fitbit.com/oauth2/authorize"
        f'?client_id={config["app", "client_id"]}'
        f"&response_type=code"
        f"&code_challenge={challenge}"
        f"&code_challenge_method=S256"
        f"&scope=" + "%20".join(_activities)
    )

    server_response = {}  # The response of the server.

    class Handler(BaseHTTPRequestHandler):
        """A server that automatically fetches the authentication code."""

        def do_GET(self):
            args = _parse_url_args(self.path)

            if "code" in args:
                response = "Received the code! Please close this window."
                # Attempt to automatically close the window using JavaScript.
                response += "<script>window.close();</script>"
                # Store the authentication code.
                server_response["authentication_code"] = args["code"]
            else:
                response = "Did not receive the code. Something went wrong."

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(("<pre>" + response + "</pre>").encode("utf-8"))

        def log_message(self, fmt, *args):
            pass  # Do nothing to hide the output.

    # Fetch authentication code.
    httpd = HTTPServer(("", port), Handler)
    # Run with a self-signed certificate: the FitBit API requires HTTPS.
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=_path_key, server_side=True)
    # The server has started. Launch browser.
    with rate_limiter:
        os.system(f'open "{auth_url}"')
    try:
        while "authentication_code" not in server_response:
            httpd.handle_request()
        authentication_code = server_response["authentication_code"]
    except KeyboardInterrupt:
        httpd.server_close()
        raise RuntimeError("Server interrupted.")
    httpd.server_close()

    # Focus the terminal again.
    if "TERM_PROGRAM" in os.environ and "iterm" in os.environ["TERM_PROGRAM"].lower():
        os.system("open -a iTerm")
    else:
        os.system("open -a Terminal")

    # Swap authentication code for token.
    basic_auth = config["app", "client_id"] + ":" + config["app", "client_secret"]
    basic_auth = urlsafe_b64encode(basic_auth.encode()).decode()
    with rate_limiter:
        res = requests.post(
            "https://api.fitbit.com/oauth2/token",
            data={
                "client_id": config["app", "client_id"],
                "code": authentication_code,
                "code_verifier": verifier,
                "grant_type": "authorization_code",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {basic_auth}",
            },
        )
    res.raise_for_status()
    res = res.json()

    # Great success! Store everything.
    config["session", "token"] = res["access_token"]
    config["session", "token_expiry_timestamp_utc"] = timestamp() + res["expires_in"]
    config["session", "refresh_token"] = res["refresh_token"]

    return config["session", "token"]

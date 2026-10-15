from __future__ import annotations

import ipaddress
import socket
from urllib.error import URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, ProxyHandler


MAX_REDIRECTS = 5


def validate_public_url(url: str) -> None:
    """Fail closed for non-HTTP URLs and non-public IP destinations."""
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are allowed")
    if not parsed.hostname or parsed.username is not None or parsed.password is not None:
        raise ValueError("URL must contain a public hostname and no credentials")
    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError as exc:
        raise ValueError("Invalid URL port") from exc
    if port < 1 or port > 65535:
        raise ValueError("Invalid URL port")

    hostname = parsed.hostname.rstrip(".").lower()
    try:
        addresses = {ipaddress.ip_address(hostname)}
    except ValueError:
        try:
            addresses = {
                ipaddress.ip_address(info[4][0])
                for info in socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
            }
        except (OSError, socket.gaierror) as exc:
            raise ValueError("Could not resolve the public destination") from exc
    if not addresses:
        raise ValueError("Destination did not resolve to an IP address")
    if any(not address.is_global for address in addresses):
        raise ValueError("Requests to private, local, reserved or non-public addresses are blocked")


class _SafeRedirectHandler(HTTPRedirectHandler):
    max_redirections = MAX_REDIRECTS
    max_repeats = MAX_REDIRECTS

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        destination = urljoin(req.full_url, newurl)
        validate_public_url(destination)
        return super().redirect_request(req, fp, code, msg, headers, destination)


def safe_urlopen(request: Request | str, *, timeout: float = 10):
    url = request.full_url if isinstance(request, Request) else request
    validate_public_url(url)
    opener = build_opener(ProxyHandler({}), _SafeRedirectHandler())
    try:
        return opener.open(request, timeout=timeout)
    except URLError:
        raise

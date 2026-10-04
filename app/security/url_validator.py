from ipaddress import ip_address
from urllib.parse import urlparse
import socket


ALLOWED_SCHEMES = {"http", "https"}

BLOCKED_HOSTS = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
}

BLOCKED_IPS = {
    "127.0.0.0/8",
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "169.254.0.0/16",
    "::1/128",
    "fc00::/7",
    "fe80::/10",
}


def is_private_or_blocked_ip(host: str) -> bool:
    try:
        ip = ip_address(host)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        )
    except ValueError:
        return False


def validate_external_url(url: str) -> bool:
    if not url or len(url) > 2048:
        return False

    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False

    hostname = parsed.hostname

    if not hostname:
        return False

    hostname = hostname.lower().rstrip(".")

    if hostname in BLOCKED_HOSTS:
        return False

    if is_private_or_blocked_ip(hostname):
        return False

    try:
        addresses = socket.getaddrinfo(
            hostname,
            None,
            proto=socket.IPPROTO_TCP,
        )

        for address in addresses:
            resolved_ip = address[4][0]

            if is_private_or_blocked_ip(resolved_ip):
                return False

    except socket.gaierror:
        return False

    return True
import json
import os
import sys
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


def vless_profile(link: str) -> dict:
    parsed = urlsplit(link)
    query = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
    if parsed.scheme != "vless" or not parsed.username or not parsed.hostname or not parsed.port:
        raise RuntimeError("Invalid VLESS link")

    user = {"id": parsed.username, "encryption": "none"}
    if query.get("flow"):
        user["flow"] = query["flow"]
    stream_settings: dict = {"network": query.get("type", "tcp"), "security": query.get("security", "none")}
    if stream_settings["security"] == "tls":
        tls_settings: dict = {"serverName": query.get("sni", parsed.hostname)}
        if query.get("alpn"):
            tls_settings["alpn"] = query["alpn"].split(",")
        if query.get("fp"):
            tls_settings["fingerprint"] = query["fp"]
        stream_settings["tlsSettings"] = tls_settings

    return {
        "log": {"loglevel": "warning"},
        "outbounds": [
            {
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {"address": parsed.hostname, "port": parsed.port, "users": [user]}
                    ]
                },
                "streamSettings": stream_settings,
                "tag": "proxy",
            },
            {"protocol": "freedom", "tag": "direct"},
            {"protocol": "blackhole", "tag": "blocked"},
        ],
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: prepare_vpn_config.py <subscription-url-file> <output-config>")

    secret_url = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
    if secret_url.startswith("vless://"):
        profile = vless_profile(secret_url)
    else:
        request = urllib.request.Request(secret_url, headers={"User-Agent": "Happ/3.3.6"})
        with urllib.request.urlopen(request, timeout=30) as response:
            profiles = json.load(response)
        if not isinstance(profiles, list) or not profiles:
            raise RuntimeError("VPN subscription returned no profiles")
        profile_index = int(os.getenv("VPN_PROFILE_INDEX", "-1"))
        profile = profiles[profile_index]
    if not isinstance(profile, dict) or not profile.get("outbounds"):
        raise RuntimeError("VPN profile has no outbound configuration")

    # This listener is never published to the host. Docker exposes it only on
    # the private openrouter-private network shared by the bot and VPN sidecar.
    profile["inbounds"] = [
        {
            "listen": "0.0.0.0",
            "port": 1080,
            "protocol": "socks",
            "settings": {"auth": "noauth", "udp": True},
            "tag": "openrouter-socks",
        }
    ]
    profile.pop("remarks", None)

    output = Path(sys.argv[2])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    print("VPN config prepared successfully")


if __name__ == "__main__":
    main()

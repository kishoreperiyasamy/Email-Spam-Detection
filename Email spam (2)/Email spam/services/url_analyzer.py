import re
from urllib.parse import urlparse

# Strict regex to extract URLs without network access
URL_REGEX = re.compile(
    r'(?:https?://|www\.)[^\s<>"\']+|[a-zA-Z0-9.-]+\.(?:com|org|net|edu|gov|mil|biz|info|top|xyz|click|site|online|club|io|co|me|ai)(?:/[^\s<>"\']*)?',
    re.IGNORECASE
)

IP_HOST_REGEX = re.compile(r'^(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?$')

KNOWN_SHORTENERS = {
    'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd', 'buff.ly',
    'adf.ly', 'bit.do', 'cutt.ly', 'rb.gy', 'shorte.st'
}

SUSPICIOUS_TLDS = {
    '.xyz', '.top', '.click', '.biz', '.info', '.club', '.site', '.online', '.work'
}

SUSPICIOUS_PATH_KEYWORDS = [
    'login', 'signin', 'verify', 'verification', 'update', 'account', 'secure',
    'banking', 'wallet', 'claim', 'refund', 'confirm', 'auth', 'checkpoint'
]

def analyze_urls_in_text(text: str) -> dict:
    """
    Extracts and inspects URLs purely statically.
    CRITICAL SECURITY NOTICE: This function NEVER makes network requests or opens URLs.
    """
    if not text:
        return {
            "url_count": 0,
            "urls_detected": [],
            "suspicious_url_flags": [],
            "has_ip_hostname": False,
            "has_shorteners": False,
            "has_suspicious_tld": False,
            "has_sensitive_keywords_in_url": False
        }

    raw_matches = URL_REGEX.findall(text)
    # Deduplicate while preserving order
    unique_urls = list(dict.fromkeys(raw_matches))
    url_count = len(unique_urls)

    suspicious_flags = []
    has_ip_hostname = False
    has_shorteners = False
    has_suspicious_tld = False
    has_sensitive_keywords = False

    sanitized_url_previews = []

    for raw_url in unique_urls:
        formatted = raw_url if raw_url.startswith(('http://', 'https://')) else f'http://{raw_url}'
        try:
            parsed = urlparse(formatted)
            netloc = parsed.netloc.lower()
            path = parsed.path.lower()
            host = netloc.split(':')[0]
            
            # Mask or display sanitized preview without clickable links
            sanitized_url_previews.append(raw_url[:60] + ('...' if len(raw_url) > 60 else ''))

            # Check 1: IP address as host
            if IP_HOST_REGEX.match(host):
                has_ip_hostname = True
                suspicious_flags.append(f"Host is a raw IP address ({host}) rather than a verified domain name")

            # Check 2: URL shortener
            if host in KNOWN_SHORTENERS:
                has_shorteners = True
                suspicious_flags.append(f"URL shortener detected ({host}) hiding final destination")

            # Check 3: Suspicious TLD
            for tld in SUSPICIOUS_TLDS:
                if host.endswith(tld):
                    has_suspicious_tld = True
                    suspicious_flags.append(f"High-risk domain extension detected ({tld})")
                    break

            # Check 4: Sensitive keyword in unverified URL
            for kw in SUSPICIOUS_PATH_KEYWORDS:
                if kw in path or kw in host:
                    has_sensitive_keywords = True
                    suspicious_flags.append(f"Security/credential keyword '{kw}' detected in link structure")
                    break

        except Exception:
            continue

    # Deduplicate flags
    unique_flags = list(dict.fromkeys(suspicious_flags))

    return {
        "url_count": url_count,
        "urls_detected": sanitized_url_previews,
        "suspicious_url_flags": unique_flags,
        "has_ip_hostname": has_ip_hostname,
        "has_shorteners": has_shorteners,
        "has_suspicious_tld": has_suspicious_tld,
        "has_sensitive_keywords_in_url": has_sensitive_keywords
    }

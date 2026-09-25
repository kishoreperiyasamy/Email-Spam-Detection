import re

PROMOTIONAL_KEYWORDS = [
    r'\b(?:free|100% free|discount|clearance|sale|special offer|limited time|buy now|exclusive deal|lowest price|cheap|save up to|best price|voucher|coupon|promo code|act fast|shop now|flash sale|mega discount|exclusive promo|claim offer|bogo|unbeatable deal|sponsored ad|promotional offer|special brochure|exclusive catalog)\b'
]

BROCHURE_AD_KEYWORDS = [
    r'\b(?:brochure|catalog|flyer|pamphlet|prospectus|marketing leaflet|sales brochure|product catalog|spec sheet|promotional flyer)\b'
]

PRIZE_KEYWORDS = [
    r'\b(?:won|winner|lottery|jackpot|congratulations|prize|sweepstakes|claim your reward|selected as winner|million dollars|cash reward|lucky visitor|claim prize)\b'
]

URGENT_KEYWORDS = [
    r'\b(?:urgent|immediately|action required|final warning|expires in \d+|within 24 hours|immediate attention|deadline|account suspended|last chance|respond now|today only)\b'
]

SECURITY_VERIFY_KEYWORDS = [
    r'\b(?:verify your account|suspended|unauthorized login|security alert|unusual activity|confirm identity|confirm password|compromised|locked account|reset required|checkpoint)\b'
]

CREDENTIAL_HARVESTING_KEYWORDS = [
    r'\b(?:ssn|social security|credit card|routing number|bank account|debit card|enter password|cvv|pin|billing details|wire transfer|direct deposit)\b'
]

def analyze_spam_indicators(subject: str, body: str, text_stats: dict, url_stats: dict, attachment_info: dict = None) -> list:
    """
    Evaluates supporting indicators across subject, body, and attachment metadata.
    These are presented clearly as supporting signals, not definitive proof.
    """
    combined = f"{subject} {body}".lower()
    indicators = []

    # 1. Promotional language
    promo_matches = []
    for pattern in PROMOTIONAL_KEYWORDS:
        found = re.findall(pattern, combined, flags=re.IGNORECASE)
        if found:
            promo_matches.extend(found[:3])
    if promo_matches:
        indicators.append({
            "category": "Promotional Content",
            "badge": "Promo Ad",
            "severity": "Medium",
            "indicator": "Promotional & Marketing Ad Copy",
            "description": f"Detected commercial advertising or discount triggers: {', '.join(set(promo_matches))}.",
            "signal_type": "supporting"
        })

    # 1b. Brochure / Catalog / Flyer references
    brochure_matches = []
    for pattern in BROCHURE_AD_KEYWORDS:
        found = re.findall(pattern, combined, flags=re.IGNORECASE)
        if found:
            brochure_matches.extend(found[:3])
    if brochure_matches or (attachment_info and "brochure" in attachment_info.get("file_type", "").lower()):
        indicators.append({
            "category": "Attachment / Media",
            "badge": "Brochure",
            "severity": "Low",
            "indicator": "Marketing Brochure / Flyer Material",
            "description": "Email references or contains commercial brochure material. Verify sender identity before downloading external media.",
            "signal_type": "supporting"
        })

    # 2. Prize / Giveaway / Lottery language
    prize_matches = []
    for pattern in PRIZE_KEYWORDS:
        found = re.findall(pattern, combined, flags=re.IGNORECASE)
        if found:
            prize_matches.extend(found[:3])
    if prize_matches:
        indicators.append({
            "category": "Prizes & Rewards",
            "badge": "Prize",
            "severity": "High",
            "indicator": "Lottery / Prize / Giveaway Claims",
            "description": f"Contains unverified winning or prize claims: {', '.join(set(prize_matches))}.",
            "signal_type": "supporting"
        })

    # 3. Urgency & Time Pressure
    urgent_matches = []
    for pattern in URGENT_KEYWORDS:
        found = re.findall(pattern, combined, flags=re.IGNORECASE)
        if found:
            urgent_matches.extend(found[:3])
    if urgent_matches:
        indicators.append({
            "category": "Urgency & Pressure",
            "badge": "Urgency",
            "severity": "High",
            "indicator": "Urgent Action Required",
            "description": f"Employs psychological urgency: {', '.join(set(urgent_matches))}.",
            "signal_type": "supporting"
        })

    # 4. Account Verification / Security Alert
    sec_matches = []
    for pattern in SECURITY_VERIFY_KEYWORDS:
        found = re.findall(pattern, combined, flags=re.IGNORECASE)
        if found:
            sec_matches.extend(found[:3])
    if sec_matches:
        indicators.append({
            "category": "Account Security",
            "badge": "Security Alert",
            "severity": "High",
            "indicator": "Account Suspension / Verification Request",
            "description": f"Claims account lock or requires urgent verification: {', '.join(set(sec_matches))}.",
            "signal_type": "supporting"
        })

    # 5. Sensitive Financial / Credential Harvesting
    cred_matches = []
    for pattern in CREDENTIAL_HARVESTING_KEYWORDS:
        found = re.findall(pattern, combined, flags=re.IGNORECASE)
        if found:
            cred_matches.extend(found[:3])
    if cred_matches:
        indicators.append({
            "category": "Credentials & Banking",
            "badge": "Harvesting",
            "severity": "High",
            "indicator": "Sensitive Data / Financial Request",
            "description": f"Requests sensitive personal or banking info: {', '.join(set(cred_matches))}.",
            "signal_type": "supporting"
        })

    # 6. Excessive Capital Letters
    caps_ratio = text_stats.get("caps_ratio", 0.0)
    if caps_ratio >= 20.0 and text_stats.get("total_chars", 0) > 20:
        indicators.append({
            "category": "Formatting",
            "badge": "Excessive Caps",
            "severity": "Medium",
            "indicator": "Excessive Capitalization",
            "description": f"{caps_ratio}% of characters are uppercase, often used in spam to demand attention.",
            "signal_type": "supporting"
        })

    # 7. Excessive Punctuation / Special Symbols
    exclamation_count = text_stats.get("exclamation_count", 0)
    dollar_count = text_stats.get("dollar_count", 0)
    punct_ratio = text_stats.get("punctuation_ratio", 0.0)
    if exclamation_count >= 3 or dollar_count >= 2 or punct_ratio > 15.0:
        indicators.append({
            "category": "Formatting",
            "badge": "Symbols",
            "severity": "Medium",
            "indicator": "Unusual Punctuation & Monetary Symbols",
            "description": f"Found {exclamation_count} exclamation marks and {dollar_count} monetary symbols.",
            "signal_type": "supporting"
        })

    # 8. URL Analysis Signals
    if url_stats.get("url_count", 0) > 0:
        flags = url_stats.get("suspicious_url_flags", [])
        if flags:
            for flag in flags[:3]:
                indicators.append({
                    "category": "Suspicious Links",
                    "badge": "Link Risk",
                    "severity": "High",
                    "indicator": "Suspicious URL Structure",
                    "description": flag,
                    "signal_type": "supporting"
                })
        else:
            indicators.append({
                "category": "Links",
                "badge": "URLs Present",
                "severity": "Low",
                "indicator": f"{url_stats['url_count']} Embedded Link(s)",
                "description": f"The email contains {url_stats['url_count']} link(s). Exercise caution before following links from unknown senders.",
                "signal_type": "supporting"
            })

    return indicators

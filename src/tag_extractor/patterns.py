"""Regex patterns for identifying different tag types in P&ID diagrams."""

import re

# Equipment tag patterns
PUMP_PATTERN_STORM = r"STORM_P\d{4}-\d+"  # e.g., STORM_P1001-1
PUMP_PATTERN_SHORT = r"\bP\d{4}\b"  # e.g., P1021 (word boundary to avoid false matches)
ROCK_TRAP_PATTERN = r"ROCK TRAP \d+"  # e.g., ROCK TRAP 1

# Valve tag patterns
VALVE_PATTERN = r"VLV\d{4}"  # e.g., VLV1001, VLV2041

# Instrument tag patterns (complex hyphenated format)
INSTRUMENT_PATTERN = r"\b[A-Z]{2}-[A-Z0-9]{2,4}-[A-Z0-9]{2,4}-\d{4}\b"  # e.g., QD-1E-84-1101

# Generic instrument/equipment tags: 3-4 letters followed by 4 digits
GENERIC_TAG_PATTERN = r"\b[A-Z]{3,4}\d{4}\b"  # e.g., FIT1001, PDIT2345, PSV1234

# Vendor/equipment codes (generic alphanumeric)
VENDOR_EQUIPMENT_PATTERN = r"\b[A-Z]{2}\d{1,3}\b"  # e.g., KD1, KD2

# Patterns to EXCLUDE (false positives)
EXCLUDE_PATTERNS = [
    r"^ST\d{4}$",  # Drawing numbers like ST0008
    r"^P\d{4}-\d+-\d+$",  # Sheet numbers like P1011-1-3
    r"^P\d{4}-\d+$",  # Sheet numbers like P1011-1 (need to be careful with pump tags)
    r"^NOTE \d+$",  # Note references
    r"^[A-G]$",  # Grid coordinates (letters)
    r"^\d{1,2}$",  # Grid coordinates (numbers)
    r"^EXISTING$|^PROPOSED$|^WATER CANNON$|^WATER HYDRANT$",  # Legend items
    r"^SHEET No\.$|^DRAWING STATUS$|^REVISION$",  # Title block headers
    r"^COPYRIGHT$|^APPROVAL$|^DRAWN BY$|^CHECKED BY$",  # More title block content
]

# Compile patterns for efficiency
COMPILED_PATTERNS = {
    "pump_storm": re.compile(PUMP_PATTERN_STORM),
    "pump_short": re.compile(PUMP_PATTERN_SHORT),
    "rock_trap": re.compile(ROCK_TRAP_PATTERN),
    "valve": re.compile(VALVE_PATTERN),
    "instrument": re.compile(INSTRUMENT_PATTERN),
    "generic_tag": re.compile(GENERIC_TAG_PATTERN),
    "vendor": re.compile(VENDOR_EQUIPMENT_PATTERN),
}

COMPILED_EXCLUDE = [re.compile(pattern) for pattern in EXCLUDE_PATTERNS]


def is_excluded(text: str) -> bool:
    """Check if text matches any exclusion pattern."""
    return any(pattern.match(text) for pattern in COMPILED_EXCLUDE)


def is_likely_tag(text: str) -> bool:
    """
    Check if text is likely a valid tag.

    Additional heuristics beyond pattern matching:
    - Must be uppercase or contain mostly uppercase letters
    - Should not be too long (tags are typically concise)
    - Should not contain common non-tag words
    """
    if not text or len(text) > 50:  # Tags shouldn't be very long
        return False

    # Check if mostly uppercase (tags are typically uppercase)
    if text.isupper() or sum(c.isupper() for c in text) / len(text) > 0.5:
        return True

    return False

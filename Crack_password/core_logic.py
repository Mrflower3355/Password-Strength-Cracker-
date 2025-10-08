# core_logic.py

import re
import string

# Theoretical cracking speeds based on hardware (Attempts/s)
ATTACK_SPEEDS = {
    "CPU (Default PC)": 500_000,
    "GPU (Gaming Card)": 10_000_000,
    "ASIC (Dedicated Hardware)": 1_000_000_000
}


def format_time_duration(seconds):
    """Converts seconds into a human-readable duration (seconds, minutes, hours, days, years)."""
    if seconds is None or seconds == float('inf'):
        return "Decades (or more)"

    if seconds < 60:
        return f"{seconds:.4f} seconds"
    elif seconds < 3600:
        return f"{seconds / 60:.2f} minutes"
    elif seconds < 86400:
        return f"{seconds / 86400:.2f} days"
    elif seconds < 31536000:
        return f"{seconds / 31536000:.2f} years"
    else:
        return f"{seconds / 31536000:.2f} years"


def assess_password_strength(password):
    """Analyzes password complexity and returns 7 values."""
    score = 0
    feedback = []

    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^a-zA-Z0-9\s]", password))

    length = len(password)
    if length >= 12:
        score += 4
        feedback.append("Excellent length (12+ characters)")
    elif length >= 8:
        score += 2
        feedback.append("Good length (8-11 characters)")
    else:
        score += 1
        feedback.append("Short length (less than 8 characters)")

    if has_upper:
        score += 1
        feedback.append("Includes uppercase letters")
    if has_lower:
        score += 1
        feedback.append("Includes lowercase letters")
    if has_digit:
        score += 1
        feedback.append("Includes numbers")
    if has_special:
        score += 2
        feedback.append("Includes special characters")

    if score >= 8:
        strength_level = "Very Strong"
    elif score >= 5:
        strength_level = "Strong"
    elif score >= 3:
        strength_level = "Moderate"
    else:
        strength_level = "Weak"

    return strength_level, score, feedback, has_upper, has_lower, has_digit, has_special


def build_keyspace(password, has_upper, has_lower, has_digit, has_special):
    """Constructs the dynamic charset and calculates keyspace details."""
    dynamic_charset = []
    keyspace_log_items = []

    if has_lower:
        dynamic_charset.extend(list(string.ascii_lowercase))
        keyspace_log_items.append("26 Lower (a-z)")
    if has_upper:
        dynamic_charset.extend(list(string.ascii_uppercase))
        keyspace_log_items.append("26 Upper (A-Z)")
    if has_digit:
        dynamic_charset.extend(list(string.digits))
        keyspace_log_items.append("10 Digits (0-9)")
    if has_special:
        # Standard symbol set
        symbol_chars = list("!@#$%^&*()-_+=[]{}|:;\"'<,>.?/`~")
        dynamic_charset.extend(symbol_chars)
        keyspace_log_items.append(f"{len(symbol_chars)} Symbols")

    # Manually include space if present in the password, as it's not in the standard symbol set
    if ' ' in password and ' ' not in dynamic_charset:
        dynamic_charset.append(' ')
        keyspace_log_items.append("1 Space")

    if not dynamic_charset:
        dynamic_charset = list(string.ascii_letters + string.digits)

    dynamic_charset_size = len(dynamic_charset)
    total_keyspace = dynamic_charset_size ** len(password)

    return dynamic_charset, dynamic_charset_size, total_keyspace, keyspace_log_items

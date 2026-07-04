"""Email validator — no-skill version (typical LLM output without discipline)."""

import re


class EmailValidationError(Exception):
    """Raised when an email address is invalid."""
    pass


class EmailValidator:
    """Validates email addresses according to common standards."""

    # Pattern based on RFC 5322 simplified
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9]'
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
        r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
    )

    MAX_LENGTH = 254
    MIN_LENGTH = 3

    def __init__(self, allow_ip_domains=False, allow_comments=False):
        self.allow_ip_domains = allow_ip_domains
        self.allow_comments = allow_comments

    def validate(self, email):
        """Validate an email address. Returns bool."""
        if not isinstance(email, str):
            return False
        email = email.strip()
        if not email:
            return False
        if len(email) > self.MAX_LENGTH or len(email) < self.MIN_LENGTH:
            return False
        if not self.EMAIL_PATTERN.match(email):
            return False
        local, domain = email.rsplit('@', 1)
        if '..' in local or local.startswith('.') or local.endswith('.'):
            return False
        return True


def validate_email(email):
    """Convenience wrapper."""
    validator = EmailValidator()
    return validator.validate(email)

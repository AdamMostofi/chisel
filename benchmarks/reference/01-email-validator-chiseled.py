"""Email validator — chiseled version. Minimum that works."""

def validate_email(email):
    """Return True if email looks valid (has @, has domain with dot)."""
    if not email or not isinstance(email, str):
        return False
    email = email.strip()
    if '@' not in email:
        return False
    local, domain = email.rsplit('@', 1)
    return bool(local and '.' in domain)

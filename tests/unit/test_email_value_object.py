import pytest

from src.domain.value_objects.email import Email


def test_valid_email():
    valid_emails = [
        "user@example.com",
        "test.user@example.com",
        "user+tag@example.co.uk",
    ]

    for email_str in valid_emails:
        email = Email(email_str)
        assert email.value == email_str
        assert str(email) == email_str


def test_invalid_email():
    invalid_emails = [
        "invalid",
        "@example.com",
        "user@",
        "user @example.com",
        "user@example",
    ]

    for email_str in invalid_emails:
        with pytest.raises(ValueError):
            Email(email_str)


def test_email_immutability():
    email = Email("test@example.com")

    with pytest.raises(Exception):
        email.value = "new@example.com"

from email_validator import validate_email, EmailNotValidError

emails_to_test = [
    "test@example.com",
    "sailikhit81@gmail.com",
    "invalid-email",
]

for email in emails_to_test:
    try:
        valid = validate_email(email)
        print(f"[{email}] Valid: {valid.email}")
    except EmailNotValidError as e:
        print(f"[{email}] Invalid: {e}")

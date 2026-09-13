import re

UZ_PHONE_RE = re.compile(r'^\+998\d{9}$')


def is_valid_uz_phone(phone_number):
    return bool(UZ_PHONE_RE.match(phone_number.strip()))


def get_password_strength_errors(password):
    errors = []
    if len(password) < 8:
        errors.append("Parol kamida 8 ta belgidan iborat bo'lishi kerak.")
    if not re.search(r'[A-Z]', password):
        errors.append("Parolda kamida 1 ta katta harf bo'lishi kerak.")
    if not re.search(r'[a-z]', password):
        errors.append("Parolda kamida 1 ta kichik harf bo'lishi kerak.")
    if not re.search(r'\d', password):
        errors.append("Parolda kamida 1 ta raqam bo'lishi kerak.")
    if not re.search(r'[^A-Za-z0-9]', password):
        errors.append("Parolda kamida 1 ta maxsus belgi (masalan: !@#$%) bo'lishi kerak.")
    return errors

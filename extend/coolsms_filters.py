import re


def phone_number(pn, hyphen=True):
    pn = re.sub(r'[^0-9]', r'', pn)
    if hyphen:
        pn = re.sub(r'([0-9]{3})([0-9]{3,4})([0-9]{4})', r'\1-\2-\3', pn)
    return pn


def preg_replace(subject, pattern, replacement):
    return re.sub(pattern, replacement, subject)

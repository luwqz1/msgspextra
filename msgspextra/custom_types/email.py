import re
import typing
from annotationlib import type_repr

LOCAL_PART_PATTERN: typing.Final = re.compile(r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~.-]+$")
LABEL_PATTERN: typing.Final = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


def validate_email(email: typing.Any, /) -> str:
    if not isinstance(email, str):
        raise TypeError(f"Email must be `str`, got `{type_repr(email.__class__)}`.")

    if not email:
        raise TypeError("Email must be non-empty.")

    if any(ch.isspace() for ch in email):
        raise TypeError("Email must not contain whitespace.")

    if email.count("@") != 1:
        raise TypeError("Email must contain exactly one `@`.")

    local, domain = email.split("@", 1)

    if len(email) > 254:
        raise TypeError("Email is too long (max 254 characters).")

    if len(local) == 0 or len(local) > 64:
        raise TypeError("Local-part length must be 1..64 characters.")

    if len(domain) == 0 or len(domain) > 253:
        raise TypeError("Domain length must be 1..253 characters.")

    if not LOCAL_PART_PATTERN.fullmatch(local):
        raise TypeError("Local-part contains invalid characters (ASCII subset expected).")

    if local[0] == "." or local[-1] == ".":
        raise TypeError("Local-part must not start or end with `.`.")

    if ".." in local:
        raise TypeError("Local-part must not contain consecutive dots `..`.")

    if domain[0] == "." or domain[-1] == ".":
        raise TypeError("Domain must not start or end with `.`.")

    if ".." in domain:
        raise TypeError("Domain must not contain consecutive dots `..`.")

    labels = domain.split(".")
    if len(labels) < 2:
        raise TypeError("Domain must contain a dot (e.g. `example.com`).")

    for label in labels:
        if not label:
            raise TypeError("Domain contains an empty label.")

        if len(label) > 63:
            raise TypeError("Domain label is too long (max 63 characters).")

        if not LABEL_PATTERN.fullmatch(label):
            raise TypeError(f"Domain label is invalid: {label!r}.")

    if labels[-1].isdigit():
        raise TypeError("Top-level domain must not be all numeric.")

    return email


def validate_idn_email(email: typing.Any, /) -> str:
    if not isinstance(email, str):
        raise TypeError(f"IDNEmail must be `str`, got `{type_repr(email.__class__)}`.")

    if not email:
        raise TypeError("IDNEmail must be non-empty.")

    if any(ch.isspace() for ch in email):
        raise TypeError("IDNEmail must not contain whitespace.")

    if email.count("@") != 1:
        raise TypeError("IDNEmail must contain exactly one `@`.")

    local, domain = email.split("@", 1)

    if len(local) == 0 or len(local) > 64:
        raise TypeError("Local-part length must be 1..64 characters.")

    if local[0] == "." or local[-1] == ".":
        raise TypeError("Local-part must not start or end with `.`.")

    if ".." in local:
        raise TypeError("Local-part must not contain consecutive dots `..`.")

    if any(ord(ch) < 0x20 for ch in local):
        raise TypeError("Local-part must not contain control characters.")

    if len(domain) == 0:
        raise TypeError("Domain must be non-empty.")

    if domain[0] == "." or domain[-1] == ".":
        raise TypeError("Domain must not start or end with `.`.")

    if ".." in domain:
        raise TypeError("Domain must not contain consecutive dots `..`.")

    labels = domain.split(".")
    if len(labels) < 2:
        raise TypeError("Domain must contain a dot (e.g. `example.com`).")

    ascii_labels: list[str] = []
    for label in labels:
        if not label:
            raise TypeError("Domain contains an empty label.")

        try:
            ascii_label = label.encode("idna").decode("ascii")
        except UnicodeError as ex:
            raise TypeError(f"Domain label is invalid: {label!r}.") from ex

        if len(ascii_label) > 63:
            raise TypeError("Domain label is too long (max 63 characters).")

        if not LABEL_PATTERN.fullmatch(ascii_label):
            raise TypeError(f"Domain label is invalid: {label!r}.")

        ascii_labels.append(ascii_label)

    ascii_domain = ".".join(ascii_labels)

    if len(ascii_domain) > 253:
        raise TypeError("Domain length must be <= 253 characters in IDNA ASCII form.")

    if ascii_labels[-1].isdigit():
        raise TypeError("Top-level domain must not be all numeric.")

    if len(local) + 1 + len(ascii_domain) > 254:
        raise TypeError("IDNEmail is too long (max 254 characters in IDNA ASCII form).")

    return email


class Email(str):
    def __new__(cls, email: str, /) -> typing.Self:
        return super().__new__(cls, validate_email(email))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"


class IDNEmail(str):
    def __new__(cls, email: str, /) -> typing.Self:
        return super().__new__(cls, validate_idn_email(email))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"


__all__ = ("Email", "IDNEmail")

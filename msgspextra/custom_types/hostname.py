import re
import typing
from annotationlib import type_repr

LABEL_PATTERN: typing.Final = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


def _validate_ascii_hostname(hostname: str, /, *, type_name: str) -> None:
    if hostname[0] == "." or hostname[-1] == ".":
        raise TypeError(f"{type_name} must not start or end with `.`.")

    if ".." in hostname:
        raise TypeError(f"{type_name} must not contain consecutive dots `..`.")

    labels = hostname.split(".")
    for label in labels:
        if not label:
            raise TypeError(f"{type_name} contains an empty label.")

        if len(label) > 63:
            raise TypeError(f"{type_name} label is too long (max 63 characters).")

        if not LABEL_PATTERN.fullmatch(label):
            raise TypeError(f"{type_name} label is invalid: {label!r}.")


def validate_hostname(hostname: typing.Any, /) -> str:
    if not isinstance(hostname, str):
        raise TypeError(f"Hostname must be `str`, got `{type_repr(hostname.__class__)}`.")

    if not hostname:
        raise TypeError("Hostname must be non-empty.")

    if any(ch.isspace() or ord(ch) < 0x20 for ch in hostname):
        raise TypeError("Hostname must not contain whitespace or control characters.")

    if any(ord(ch) > 0x7F for ch in hostname):
        raise TypeError("Hostname must contain only ASCII characters.")

    if len(hostname) > 253:
        raise TypeError("Hostname is too long (max 253 characters).")

    _validate_ascii_hostname(hostname, type_name="Hostname")
    return hostname


def validate_idn_hostname(hostname: typing.Any, /) -> str:
    if not isinstance(hostname, str):
        raise TypeError(f"IDNHostname must be `str`, got `{type_repr(hostname.__class__)}`.")

    if not hostname:
        raise TypeError("IDNHostname must be non-empty.")

    if any(ch.isspace() or ord(ch) < 0x20 for ch in hostname):
        raise TypeError("IDNHostname must not contain whitespace or control characters.")

    if hostname[0] == "." or hostname[-1] == ".":
        raise TypeError("IDNHostname must not start or end with `.`.")

    if ".." in hostname:
        raise TypeError("IDNHostname must not contain consecutive dots `..`.")

    labels = hostname.split(".")
    ascii_labels: list[str] = []

    for label in labels:
        if not label:
            raise TypeError("IDNHostname contains an empty label.")

        try:
            ascii_label = label.encode("idna").decode("ascii")
        except UnicodeError as ex:
            raise TypeError(f"IDNHostname label is invalid: {label!r}.") from ex

        ascii_labels.append(ascii_label)

    ascii_hostname = ".".join(ascii_labels)
    if len(ascii_hostname) > 253:
        raise TypeError("IDNHostname is too long (max 253 characters in IDNA ASCII form).")

    _validate_ascii_hostname(ascii_hostname, type_name="IDNHostname")
    return hostname


class Hostname(str):
    def __new__(cls, hostname: str, /) -> typing.Self:
        return super().__new__(cls, validate_hostname(hostname))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"


class IDNHostname(str):
    def __new__(cls, hostname: str, /) -> typing.Self:
        return super().__new__(cls, validate_idn_hostname(hostname))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"


__all__ = ("Hostname", "IDNHostname")

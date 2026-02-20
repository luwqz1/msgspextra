import re
import typing
from annotationlib import type_repr
from urllib.parse import urlsplit

SCHEME_PATTERN: typing.Final = re.compile(r"^[A-Za-z][A-Za-z0-9+\-.]*$")


def is_hexdig(c: str, /) -> bool:
    return len(c) == 1 and (c.isdigit() or c.lower() in "abcdef")


def is_valid_percent_encoding(s: str, /) -> bool:
    i = 0

    while i < len(s):
        if s[i] == "%":
            if i + 2 >= len(s):
                return False

            a, b = s[i + 1], s[i + 2]

            if not is_hexdig(a) or not is_hexdig(b):
                return False

            i += 3
        else:
            i += 1

    return True


def _validate_uri_like(
    uri: typing.Any,
    /,
    *,
    type_name: str,
    require_scheme: bool,
    require_http_netloc: bool,
    allow_empty: bool,
    ascii_only: bool,
) -> str:
    if not isinstance(uri, str):
        raise TypeError(f"{type_name} must be `str`, got `{type_repr(uri.__class__)}`.")

    if not uri:
        if allow_empty:
            return uri
        raise TypeError(f"{type_name} must be non-empty.")

    if any(ord(ch) < 0x20 or ch in " \t\r\n" for ch in uri):
        raise TypeError(f"{type_name} contains whitespace or control characters.")

    if ascii_only and any(ord(ch) > 0x7F for ch in uri):
        raise TypeError(f"{type_name} must contain only ASCII characters.")

    if not is_valid_percent_encoding(uri):
        raise TypeError(
            f"{type_name} contains invalid percent-encoding (expected % followed by two hex digits).",
        )

    split_result = urlsplit(uri)

    if require_scheme and not split_result.scheme:
        raise TypeError(
            f"{type_name} must be absolute and include a scheme (e.g. `https`, `mailto`, `urn`).",
        )

    if split_result.scheme and not SCHEME_PATTERN.fullmatch(split_result.scheme):
        raise TypeError(f"{type_name} has invalid scheme: {split_result.scheme!r}.")

    if require_http_netloc and split_result.scheme.lower() in ("http", "https") and not split_result.netloc:
        raise TypeError(f"HTTP(S) {type_name} must include an authority/host (netloc), e.g. `https://domain.com`.")

    return uri


def validate_uri(uri: typing.Any, *, require_http_netloc: bool = True) -> str:
    return _validate_uri_like(
        uri,
        type_name="URI",
        require_scheme=True,
        require_http_netloc=require_http_netloc,
        allow_empty=False,
        ascii_only=True,
    )


def validate_uri_reference(uri: typing.Any, *, require_http_netloc: bool = True) -> str:
    return _validate_uri_like(
        uri,
        type_name="URIReference",
        require_scheme=False,
        require_http_netloc=require_http_netloc,
        allow_empty=True,
        ascii_only=True,
    )


def validate_iri(iri: typing.Any, *, require_http_netloc: bool = True) -> str:
    return _validate_uri_like(
        iri,
        type_name="IRI",
        require_scheme=True,
        require_http_netloc=require_http_netloc,
        allow_empty=False,
        ascii_only=False,
    )


def validate_iri_reference(iri: typing.Any, *, require_http_netloc: bool = True) -> str:
    return _validate_uri_like(
        iri,
        type_name="IRIReference",
        require_scheme=False,
        require_http_netloc=require_http_netloc,
        allow_empty=True,
        ascii_only=False,
    )


class URI(str):
    def __new__(cls, uri: str, /, *, require_http_netloc: bool = True) -> typing.Self:
        return super().__new__(cls, validate_uri(uri, require_http_netloc=require_http_netloc))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"


class URIReference(str):
    def __new__(cls, uri: str, /, *, require_http_netloc: bool = True) -> typing.Self:
        return super().__new__(
            cls,
            validate_uri_reference(uri, require_http_netloc=require_http_netloc),
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"


class IRI(str):
    def __new__(cls, iri: str, /, *, require_http_netloc: bool = True) -> typing.Self:
        return super().__new__(cls, validate_iri(iri, require_http_netloc=require_http_netloc))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"


class IRIReference(str):
    def __new__(cls, iri: str, /, *, require_http_netloc: bool = True) -> typing.Self:
        return super().__new__(
            cls,
            validate_iri_reference(iri, require_http_netloc=require_http_netloc),
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"


__all__ = ("IRI", "URI", "IRIReference", "URIReference")

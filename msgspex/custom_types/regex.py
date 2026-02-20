import re
import typing
from annotationlib import type_repr


def validate_regex(pattern: typing.Any, /) -> str:
    if not isinstance(pattern, str):
        raise TypeError(f"Regex must be `str`, got `{type_repr(pattern.__class__)}`.")

    try:
        re.compile(pattern)
    except re.error as ex:
        raise TypeError(f"Regex pattern is invalid: {pattern!r}.") from ex

    return pattern


class Regex(str):
    def __new__(cls, pattern: str, /) -> typing.Self:
        return super().__new__(cls, validate_regex(pattern))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"

    def compile(self, /, flags: int = 0) -> re.Pattern[str]:
        return re.compile(str(self), flags=flags)


__all__ = ("Regex",)

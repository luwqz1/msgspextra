import typing
from annotationlib import type_repr


def _validate_pointer_escapes(pointer: str, /, *, type_name: str) -> None:
    idx = 0
    while idx < len(pointer):
        if pointer[idx] == "~":
            if idx + 1 >= len(pointer) or pointer[idx + 1] not in ("0", "1"):
                raise TypeError(f"{type_name} contains invalid escape sequence, expected `~0` or `~1`.")
            idx += 2
        else:
            idx += 1


def validate_json_pointer(pointer: typing.Any, /) -> str:
    if not isinstance(pointer, str):
        raise TypeError(f"JsonPointer must be `str`, got `{type_repr(pointer.__class__)}`.")

    if pointer == "":
        return pointer

    if not pointer.startswith("/"):
        raise TypeError("JsonPointer must be empty or start with `/`.")

    _validate_pointer_escapes(pointer, type_name="JsonPointer")
    return pointer


def validate_relative_json_pointer(pointer: typing.Any, /) -> str:
    if not isinstance(pointer, str):
        raise TypeError(f"RelativeJsonPointer must be `str`, got `{type_repr(pointer.__class__)}`.")

    if not pointer:
        raise TypeError("RelativeJsonPointer must be non-empty.")

    idx = 0
    while idx < len(pointer) and pointer[idx].isdigit():
        idx += 1

    if idx == 0:
        raise TypeError("RelativeJsonPointer must start with a non-negative integer.")

    if idx < len(pointer) and pointer[idx] in ("+", "-"):
        idx += 1
        start = idx
        while idx < len(pointer) and pointer[idx].isdigit():
            idx += 1
        if idx == start:
            raise TypeError("RelativeJsonPointer index adjustment must be followed by a non-negative integer.")

    tail = pointer[idx:]
    if tail == "#":
        return pointer

    if tail and not tail.startswith("/"):
        raise TypeError("RelativeJsonPointer tail must be `#`, empty, or start with `/`.")

    _validate_pointer_escapes(tail, type_name="RelativeJsonPointer")
    return pointer


class JsonPointer(str):
    def __new__(cls, pointer: str, /) -> typing.Self:
        return super().__new__(cls, validate_json_pointer(pointer))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"


class RelativeJsonPointer(str):
    def __new__(cls, pointer: str, /) -> typing.Self:
        return super().__new__(cls, validate_relative_json_pointer(pointer))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"


__all__ = ("JsonPointer", "RelativeJsonPointer")

import math
import sys
import typing
from annotationlib import type_repr

INT32_MIN: typing.Final = -(2**31)
INT32_MAX: typing.Final = 2**31 - 1
INT64_MIN: typing.Final = -(2**63)
INT64_MAX: typing.Final = 2**63 - 1
FLOAT32_MAX: typing.Final = 3.4028234663852886e38
FLOAT64_MAX: typing.Final = sys.float_info.max


def _coerce_int(value: typing.Any, /, *, type_name: str) -> int:
    if isinstance(value, bool):
        raise TypeError(f"{type_name} must not be `bool`.")

    if isinstance(value, float):
        if not value.is_integer():
            raise TypeError(f"{type_name} requires an integer value.")
        return int(value)

    try:
        return int(value)
    except (TypeError, ValueError) as ex:
        raise TypeError(f"{type_name} must be `int`-compatible, got `{type_repr(value.__class__)}`.") from ex


def _coerce_float(value: typing.Any, /, *, type_name: str) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{type_name} must not be `bool`.")

    try:
        number = float(value)
    except (TypeError, ValueError) as ex:
        raise TypeError(f"{type_name} must be `float`-compatible, got `{type_repr(value.__class__)}`.") from ex

    if math.isnan(number) or math.isinf(number):
        raise TypeError(f"{type_name} must be a finite number.")

    return number


class Int32(int):
    def __new__(cls, value: typing.Any, /) -> typing.Self:
        int_value = _coerce_int(value, type_name="Int32")
        if not (INT32_MIN <= int_value <= INT32_MAX):
            raise TypeError(f"Int32 value must be in range [{INT32_MIN}, {INT32_MAX}].")
        return super().__new__(cls, int_value)


class Int64(int):
    def __new__(cls, value: typing.Any, /) -> typing.Self:
        int_value = _coerce_int(value, type_name="Int64")
        if not (INT64_MIN <= int_value <= INT64_MAX):
            raise TypeError(f"Int64 value must be in range [{INT64_MIN}, {INT64_MAX}].")
        return super().__new__(cls, int_value)


class Float32(float):
    def __new__(cls, value: typing.Any, /) -> typing.Self:
        float_value = _coerce_float(value, type_name="Float32")
        if abs(float_value) > FLOAT32_MAX:
            raise TypeError(f"Float32 value must be in range [-{FLOAT32_MAX}, {FLOAT32_MAX}].")
        return super().__new__(cls, float_value)


class Float64(float):
    def __new__(cls, value: typing.Any, /) -> typing.Self:
        float_value = _coerce_float(value, type_name="Float64")
        if abs(float_value) > FLOAT64_MAX:
            raise TypeError(f"Float64 value must be in range [-{FLOAT64_MAX}, {FLOAT64_MAX}].")
        return super().__new__(cls, float_value)


__all__ = ("Float32", "Float64", "Int32", "Int64")

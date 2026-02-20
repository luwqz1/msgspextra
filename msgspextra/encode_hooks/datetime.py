import datetime as dt
import typing

from msgspextra.custom_types.datetime import (
    FloatTimestampDatetime,
    IntTimestampDatetime,
    ISODatetime,
    StringTimestampDatetime,
    datetime,
)
from msgspextra.encoder import encoder
from msgspextra.tools import fullname


@encoder.add_enc_hook(datetime)
def datetime_enc_hook(obj: typing.Any, /) -> str | int | float:
    if isinstance(obj, StringTimestampDatetime):
        return string_timestamp_datetime_enc_hook(obj)

    if isinstance(obj, IntTimestampDatetime):
        return int_timestamp_datetime_enc_hook(obj)

    if isinstance(obj, FloatTimestampDatetime):
        return float_timestamp_datetime_enc_hook(obj)

    if isinstance(obj, ISODatetime | dt.datetime):
        return isodatetime_enc_hook(obj)

    raise TypeError(f"Cannot encode object of type `{fullname(obj)}` into `ISO | timestamp`.")


@encoder.add_enc_hook(StringTimestampDatetime)
def string_timestamp_datetime_enc_hook(obj: StringTimestampDatetime, /) -> str:
    if obj.is_from_digits_string:
        return str(int(obj.timestamp()))

    if obj.is_from_float_string:
        return str(float(obj.timestamp()))

    raise TypeError(
        f"Cannot encode object of type `{fullname(obj)}` into `timestamp`. "
        "String timestamp datetime must be from `digits` string or `float` string."
    )


@encoder.add_enc_hook(IntTimestampDatetime)
def int_timestamp_datetime_enc_hook(obj: IntTimestampDatetime, /) -> int:
    return int(obj.timestamp())


@encoder.add_enc_hook(FloatTimestampDatetime)
def float_timestamp_datetime_enc_hook(obj: FloatTimestampDatetime, /) -> float:
    return float(obj.timestamp())


@encoder.add_enc_hook(ISODatetime)
def isodatetime_enc_hook(obj: datetime, /) -> str:
    return obj.isoformat().replace("+00:00", "Z")


__all__ = (
    "datetime_enc_hook",
    "float_timestamp_datetime_enc_hook",
    "int_timestamp_datetime_enc_hook",
    "isodatetime_enc_hook",
    "string_timestamp_datetime_enc_hook",
)

import datetime as dt
import re
import typing

from msgspextra.custom_types.datetime import (
    DT,
    Datetime,
    FloatTimestampDatetime,
    IntTimestampDatetime,
    ISODatetime,
    StringTimestampDatetime,
    datetime,
)
from msgspextra.decoder import decoder
from msgspextra.tools import fullname

_INT_STRING_TIMESTAMP_RE: typing.Final = re.compile(r"^[+-]?\d+$")
_FLOAT_STRING_TIMESTAMP_RE: typing.Final = re.compile(
    r"^[+-]?(?:(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)$",
)
_ISO8601_DATETIME_RE: typing.Final = re.compile(
    r"^\d{4}-\d{2}-\d{2}"
    r"(?:[Tt ]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?(?:Z|[+-]\d{2}:\d{2})?)?$",
)


def _raise_type_error(
    obj: typing.Any,
    /,
    *,
    with_type: str | None = None,
    from_ex: Exception | None = None,
) -> typing.NoReturn:
    raise TypeError(
        f"Cannot validate object of type `{fullname(obj)}` into `datetime.datetime`"
        + ("" if not with_type else f" with `{with_type}`."),
    ) from from_ex


def _validate_datetime(
    tp: type[Datetime],
    obj: typing.Any,
    /,
    *,
    with_type: str | None = None,
) -> typing.Any:
    if isinstance(obj, dt.datetime):
        return tp.cast(obj)

    if isinstance(obj, DT):
        return obj

    return _raise_type_error(obj, with_type=with_type)


def _is_iso8601_datetime_string(value: str, /) -> bool:
    return _ISO8601_DATETIME_RE.fullmatch(value) is not None


@decoder.add_dec_hook(FloatTimestampDatetime)
def float_timestamp_datetime_dec_hook(
    tp: type[FloatTimestampDatetime],
    obj: typing.Any,
    /,
) -> FloatTimestampDatetime:
    if isinstance(obj, float):
        return tp.fromtimestamp(timestamp=obj, tz=dt.timezone.utc)

    return _validate_datetime(tp, obj, with_type="float timestamp")


@decoder.add_dec_hook(IntTimestampDatetime)
def int_timestamp_datetime_dec_hook(
    tp: type[IntTimestampDatetime],
    obj: typing.Any,
    /,
) -> IntTimestampDatetime:
    if isinstance(obj, int):
        return tp.fromtimestamp(timestamp=obj, tz=dt.timezone.utc)

    return _validate_datetime(tp, obj, with_type="integer timestamp")


@decoder.add_dec_hook(StringTimestampDatetime)
def string_timestamp_datetime_dec_hook(
    tp: type[StringTimestampDatetime],
    obj: typing.Any,
    /,
) -> StringTimestampDatetime:
    if isinstance(obj, str):
        value = obj.strip()

        if _INT_STRING_TIMESTAMP_RE.fullmatch(value) is not None:
            return tp.from_digits_string(value)

        if _FLOAT_STRING_TIMESTAMP_RE.fullmatch(value) is not None:
            return tp.from_float_string(value)

    return _validate_datetime(tp, obj, with_type="string timestamp")


@decoder.add_dec_hook(datetime)
def datetime_dec_hook(_: type[datetime], obj: typing.Any, /) -> DT:
    if isinstance(obj, str):
        value = obj.strip()
        return (
            isodatetime_dec_hook(ISODatetime, value)
            if _is_iso8601_datetime_string(value)
            else string_timestamp_datetime_dec_hook(StringTimestampDatetime, value)
        )

    if isinstance(obj, int):
        return int_timestamp_datetime_dec_hook(IntTimestampDatetime, obj)

    if isinstance(obj, float):
        return float_timestamp_datetime_dec_hook(FloatTimestampDatetime, obj)

    return _validate_datetime(Datetime, obj)


@decoder.add_dec_hook(ISODatetime)
def isodatetime_dec_hook(tp: type[ISODatetime], obj: typing.Any, /) -> ISODatetime:
    if isinstance(obj, str):
        try:
            return tp.fromisoformat(obj.strip().replace("Z", "+00:00"))
        except ValueError as ex:
            _raise_type_error(obj, with_type="ISO format", from_ex=ex)

    return _validate_datetime(tp, obj, with_type="ISO format")


__all__ = (
    "datetime_dec_hook",
    "float_timestamp_datetime_dec_hook",
    "int_timestamp_datetime_dec_hook",
    "isodatetime_dec_hook",
    "string_timestamp_datetime_dec_hook",
)

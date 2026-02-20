import datetime as dt
import typing
from datetime import date

from msgspex.caster import SupportsCast


class Datetime(dt.datetime, SupportsCast):
    @classmethod
    def cast(cls, obj: dt.datetime) -> typing.Self:
        return cls.fromtimestamp(timestamp=obj.timestamp(), tz=obj.tzinfo)


class StringTimestampDatetime(Datetime):
    """String timestamp datetime."""

    is_from_digits_string: bool = False
    is_from_float_string: bool = False

    @classmethod
    def from_digits_string(cls, digits: str, /) -> typing.Self:
        obj = cls.fromtimestamp(timestamp=int(digits), tz=dt.timezone.utc)
        obj.is_from_digits_string = True
        return obj

    @classmethod
    def from_float_string(cls, float_str: str, /) -> typing.Self:
        obj = cls.fromtimestamp(timestamp=float(float_str), tz=dt.timezone.utc)
        obj.is_from_float_string = True
        return obj


class IntTimestampDatetime(Datetime):
    """Integer timestamp datetime."""


class FloatTimestampDatetime(Datetime):
    """Float timestamp datetime."""


class ISODatetime(Datetime):
    """ISO datetime."""


isodatetime = ISODatetime


class timedelta(dt.timedelta, SupportsCast):  # noqa: N801  # type: ignore
    @classmethod
    def cast(cls, obj: dt.timedelta) -> typing.Self:
        return cls(seconds=obj.total_seconds())


DT: typing.TypeAlias = StringTimestampDatetime | IntTimestampDatetime | FloatTimestampDatetime | ISODatetime | dt.datetime


if typing.TYPE_CHECKING:
    from datetime import datetime, timedelta  # type: ignore

else:

    class datetimemeta(type):  # noqa: N801
        def __instancecheck__(cls, __instance: typing.Any) -> bool:
            return isinstance(__instance, DT)

    class datetime(metaclass=datetimemeta):  # noqa: N801
        pass


__all__ = (
    "FloatTimestampDatetime",
    "ISODatetime",
    "IntTimestampDatetime",
    "StringTimestampDatetime",
    "date",
    "datetime",
    "isodatetime",
    "timedelta",
)

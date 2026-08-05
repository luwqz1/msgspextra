import datetime as dt
import typing

from msgspex.caster import SupportsCast


class Datetime(dt.datetime, SupportsCast):
    @classmethod
    def cast(cls, obj: dt.datetime) -> typing.Self:
        return cls.fromtimestamp(timestamp=obj.timestamp(), tz=obj.tzinfo)

    def __repr__(self) -> str:
        data = (
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
        )

        if self.second != 0:
            data += (self.second,)

        if self.microsecond:
            data += (self.microsecond,)

        representation = "datetime({})".format("".join(repr(x) for x in data))

        if self.tzinfo is not None:
            representation = representation[:-1] + ", tzinfo=%r" % self.tzinfo + ")"

        if self.fold:
            representation = representation[:-1] + ", fold=1)"

        return representation


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


class timedelta(dt.timedelta, SupportsCast):  # noqa: N801  # type: ignore
    @classmethod
    def cast(cls, obj: dt.timedelta) -> typing.Self:
        return cls(seconds=obj.total_seconds())


if typing.TYPE_CHECKING:
    from datetime import date, datetime, timedelta  # type: ignore
    from datetime import datetime as ftimestamp
    from datetime import datetime as isodatetime
    from datetime import datetime as itimestamp
    from datetime import datetime as stimestamp

else:
    from datetime import date

    class datetimemeta(type):  # noqa: N801
        def __instancecheck__(cls, __instance: typing.Any) -> bool:
            return isinstance(__instance, DT)

    class datetime(metaclass=datetimemeta):  # noqa: N801
        pass

    stimestamp = StringTimestampDatetime
    itimestamp = IntTimestampDatetime
    ftimestamp = FloatTimestampDatetime
    isodatetime = ISODatetime


DT: typing.TypeAlias = stimestamp | itimestamp | ftimestamp | isodatetime | dt.datetime


__all__ = (
    "FloatTimestampDatetime",
    "ISODatetime",
    "IntTimestampDatetime",
    "StringTimestampDatetime",
    "date",
    "datetime",
    "ftimestamp",
    "isodatetime",
    "itimestamp",
    "stimestamp",
    "timedelta",
)

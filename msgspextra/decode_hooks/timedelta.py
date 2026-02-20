import datetime as dt
import typing

from msgspextra.caster import SupportsCast
from msgspextra.custom_types.datetime import timedelta
from msgspextra.decoder import decoder
from msgspextra.tools import fullname


@decoder.add_dec_hook(timedelta)
def timedelta_dec_hook(tp: type[timedelta], obj: typing.Any, /) -> typing.Any:
    if isinstance(obj, tp):
        return obj

    if isinstance(obj, dt.timedelta):
        assert issubclass(tp, SupportsCast)
        return tp.cast(obj)

    if isinstance(obj, int | float):
        obj = tp(seconds=obj)
        if isinstance(obj, int):
            setattr(obj, "is_from_int", True)
        return obj

    raise TypeError(f"Cannot validate object of type `{fullname(obj)}` into `datetime.timedelta`.")


__all__ = ("timedelta_dec_hook",)

import datetime as dt
import typing

from msgspextra.caster import SupportsCast
from msgspextra.custom_types.datetime import datetime, timedelta
from msgspextra.encoder import encoder

encoder.add_cast_type(dt.datetime, typing.cast("type[SupportsCast]", datetime))
encoder.add_cast_type(dt.timedelta, typing.cast("type[SupportsCast]", timedelta))


__all__ = ("datetime", "timedelta")

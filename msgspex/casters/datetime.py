import datetime as dt
import typing

from msgspex.caster import SupportsCast
from msgspex.custom_types.datetime import datetime, timedelta
from msgspex.encoder import encoder

encoder.add_cast_type(dt.datetime, typing.cast("type[SupportsCast]", datetime))
encoder.add_cast_type(dt.timedelta, typing.cast("type[SupportsCast]", timedelta))


__all__ = ("datetime", "timedelta")
